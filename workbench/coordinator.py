"""Persistent Start → one SME exchange → verification → reports coordinator."""
import ast
import json
from pathlib import Path
import sqlite3
import threading
from .domain import require, identity, safe_path, write_new, encode, decode, sha, ValidationError
from .intake import parse_manifest
from .ledger import Ledger, now
from .source import analyze_sources
from .target import emit_program, emit_jobs, run_generated, check_generated
from .fixtures import plan_cases, verify_program
from .review import export_packet, read_answers
from .knowledge import update_knowledge


class Coordinator:
    def __init__(self, root):
        from .instance import InstanceLock
        self.root=Path(root).resolve();self.instance=InstanceLock(self.root);self.ledger=Ledger(self.root);self.lock=threading.RLock();self.stopped=threading.Event();self.worker=None;self.closed=False
        from .provider import configured_provider
        self.provider=configured_provider()
        for p in self.ledger.list(True):
            if p['status'] in ('ANALYZING','VERIFYING'):
                if p['packet_issued']:
                    for file in ['packet.json','sme-checklist.xlsx','sme-checklist.docx','sme-checklist.html']:
                        require((self.process_root(p['id'])/'review'/file).is_file(),'Issued packet is incomplete; recover its preserved snapshot')
                        self.register(p,'review/'+file)
                self.ledger.save(p,'QUEUED_ANALYSIS' if not p['packet_issued'] else 'QUEUED_VERIFY' if p['packet_imported'] else 'WAITING_SME')

    def process_root(self,pid):return safe_path(self.root,'processes/'+identity(pid))

    def create(self, manifest_text, source_files=None, demo=False, prompt=''):
        manifest=parse_manifest(manifest_text)
        if not source_files:
            folder=self.root/'Endeavor';source_files={}
            if folder.exists():
                for path in folder.rglob('*'):
                    require(not path.is_symlink(),'Symlinks are not accepted in Endeavor')
                    if path.is_file() and path.suffix.lower() in ('.cbl','.cob','.cobol','.cpy','.copy','.jcl','.bms','.sql','.txt'):
                        require(path.stat().st_size<=512000 and len(source_files)<200,'Endeavor export exceeds bounds')
                        source_files[path.relative_to(folder).as_posix()]=path.read_text(encoding='utf-8')
        require(isinstance(source_files,dict) and 0<len(source_files)<=200,'Provide a source folder with 1 to 200 supported text files')
        require(all(isinstance(k,str) and isinstance(v,str) for k,v in source_files.items()),'Source filenames and contents must be text')
        require(isinstance(prompt,str),'Analysis prompt must be text')
        require(sum(len(x.encode()) for x in source_files.values())<=8*1024*1024,'Source export exceeds size bound')
        with self.lock:
            require(not self.process_root(manifest['id']).exists(),'Process directory already exists')
            for path,text in source_files.items():
                safe_path(self.process_root(manifest['id'])/'input'/'sources',path)
                require(isinstance(text,str) and len(text.encode())<=512000,'Source file exceeds bounds')
            doc=self.ledger.create(manifest,demo)
            try:
                base=self.process_root(doc['id']);write_new(base/'input'/'process-input.md',manifest_text.encode())
                hashes={}
                for path,text in source_files.items():hashes[path]=write_new(safe_path(base/'input'/'sources',path),text.encode())
                doc['source_files']=hashes;doc['prompt']=prompt[:16000]
                return self.ledger.save(doc)
            except Exception:
                doc['blockers']=[{'kind':'intake_storage','message':'Input storage failed; preserved available evidence.'}];self.ledger.save(doc,'FAILED');raise

    def start(self,pid):
        with self.lock:
            doc=self.ledger.get(pid);require(doc['status']=='READY','Process already started; use Resume when applicable')
            doc['authorization']={'recorded':now(),'scope':doc['source_files'],'target':'trusted-generated-subset/python-sqlite','seed':21,'max_cases_per_program':256,'max_repair_attempts':1,'source_operations':'read-only','mainframe_execution':False}
            self.ledger.event(pid,'start','Start authorization recorded; source writes and mainframe execution are prohibited')
            return self.ledger.save(doc,'QUEUED_ANALYSIS')

    def control(self,pid,action):
        with self.lock:
            doc=self.ledger.get(pid)
            require(doc['status'] not in ('COMPLETED','COMPLETED_WITH_BLOCKERS'),'Terminal evidence cannot be changed in place')
            if action=='pause':
                require(doc['status'] not in ('READY','PAUSED'),'There is no running stage to pause')
                doc['resume_status']=doc['status'];status='PAUSED'
            elif action=='resume':
                require(doc['status'] in ('PAUSED','FAILED','REPORTING_FAILED'),'Nothing eligible to resume')
                status=doc.pop('resume_status','QUEUED_REPORT' if doc['packet_imported'] else 'WAITING_SME' if doc['packet_issued'] else 'QUEUED_ANALYSIS')
            elif action=='cancel':doc['blockers'].append({'kind':'cancelled','message':'Operator cancelled this process'});status='QUEUED_REPORT'
            else:raise ValidationError('Unknown control')
            self.ledger.event(pid,action,'Operator '+action+' recorded; existing SME quota retained')
            return self.ledger.save(doc,status)

    def artifact(self,pid,relative):
        doc=self.ledger.get(pid);require(relative in doc['artifacts'],'Artifact not registered for this process')
        path=safe_path(self.process_root(pid),relative);require(path.is_file(),'Artifact unavailable');return path

    def register(self,doc,relative):
        if relative not in doc['artifacts']:doc['artifacts'].append(relative)

    def import_answers(self,pid,data,reviewer):
        with self.lock:
            doc=self.ledger.get(pid);require(doc['status']=='WAITING_SME','Process is not waiting for SME answers')
            packet=decode(self.artifact(pid,'review/packet.json').read_bytes())
            answers=read_answers(data,packet,reviewer)
            returned=self.process_root(pid)/'input'/'sme-return.xlsx'
            if returned.exists():require(returned.read_bytes()==data,'Recovery return differs from the preserved SME file')
            else:write_new(returned,data)
            self.ledger.consume_return(pid,answers);self.ledger.event(pid,'review','One SME return imported; automatic continuation queued')
            return self.ledger.get(pid)

    def sources(self,doc):
        result={}
        for path,h in doc['source_files'].items():
            raw=safe_path(self.process_root(doc['id'])/'input'/'sources',path).read_bytes()
            require(sha(raw)==h,'Source snapshot changed; existing evidence cannot be credited')
            result[path]=raw.decode('utf-8')
        return result

    def advance(self,pid):
        with self.lock:
            doc=self.ledger.get(pid)
            if doc['status']=='QUEUED_ANALYSIS':self.analyze(doc)
            elif doc['status']=='QUEUED_VERIFY':self.verify(doc)
            elif doc['status']=='QUEUED_REPORT':self.report(doc)
            return self.ledger.get(pid)

    def analyze(self,doc):
        pid=doc['id'];self.ledger.save(doc,'ANALYZING');self.ledger.event(pid,'analysis','Reading complete source snapshot and extracting supported atomic rules')
        analysis=analyze_sources(self.sources(doc),doc);doc['analysis']=analysis;doc['blockers']=list(analysis['blockers'])
        context_path=self.root/'knowledge'/'inbox'/'context.md'
        if context_path.exists():
            require(not context_path.is_symlink() and context_path.stat().st_size<=16000,'Knowledge context must be a regular Markdown file of at most 16 KB')
            doc['knowledge_context']={'text':context_path.read_text(),'sha256':sha(context_path.read_bytes()),'status':'UNVERIFIED_INPUT'}
        from .connectors import read_only_discovery
        doc['discovery']=read_only_discovery()
        doc['llm']={'status':'NOT_CONFIGURED','live_ready':False}
        if self.provider:
            try:
                excerpts=('\n'.join(p['source_text'] for p in analysis['programs'].values())+'\nUnverified background knowledge:\n'+doc.get('knowledge_context',{}).get('text',''))[:16000]
                doc['llm']={'status':'ANALYSIS_RETURNED',**self.provider.analyze(excerpts,doc.get('prompt') or 'Review this process and identify assumptions for its one SME checklist.')}
            except ValidationError as exc:
                doc['llm']={'status':'UNAVAILABLE','message':str(exc),'live_ready':False}
                doc['blockers'].append({'kind':'llm_unavailable','message':str(exc)})
        self.ledger.register_assets(pid,analysis['assets'])
        root=self.process_root(pid)
        analysis_path=root/'analysis'/'source-analysis.json'
        if analysis_path.exists():require(analysis_path.read_bytes()==encode(analysis),'Analysis recovery disagrees with frozen evidence')
        else:write_new(analysis_path,encode(analysis))
        self.register(doc,'analysis/source-analysis.json')
        doc['program_versions']={}
        for name,program in analysis['programs'].items():
            if program['blockers']:continue
            code=emit_program(program);check_generated(code)
            version=sha(code);doc['program_versions'][name]=version
            path=self.root/'shared'/'target'/'python'/(version+'.py')
            if not path.exists():write_new(path,code.encode())
            require(path.read_text()==code,'Shared target version integrity failed')
        packet=export_packet(doc,root/'review')
        self.ledger.save(doc,'ANALYZING');self.ledger.issue_packet(pid,packet['packet_hash'])
        for file in ['packet.json','sme-checklist.xlsx','sme-checklist.docx','sme-checklist.html']:self.register(doc,'review/'+file)
        self.ledger.event(pid,'review','The single comprehensive checklist is ready for download',{'rules':len(analysis['rules']),'blockers':len(analysis['blockers'])})
        self.ledger.save(doc,'WAITING_SME')

    def verify(self,doc):
        pid=doc['id'];root=self.process_root(pid);self.ledger.save(doc,'VERIFYING')
        try:self.sources(doc)
        except ValidationError as exc:
            doc['blockers'].append({'kind':'source_changed','message':str(exc)});self.ledger.save(doc,'QUEUED_REPORT');return
        for rid,answer in doc['answers']['items'].items():
            if answer['answer']!='Yes' or answer['correction']:doc['blockers'].append({'kind':'sme_unresolved','item_id':rid,'message':'SME item '+rid+': '+answer['answer']+'. '+answer['correction'],'correction_preserved':bool(answer['correction'])})
        prior=[int(p.name[4:]) for p in (root/'synthetic').glob('run-*') if p.name[4:].isdigit()]
        run_id=f'run-{max([len(doc["runs"]),*prior])+1:04d}';runroot=root/'synthetic'/run_id;runroot.mkdir(parents=True,exist_ok=False)
        run={'id':run_id,'created':now(),'programs':{},'evidence_basis':'SOURCE_DERIVED_EXPECTED','observed_legacy_parity':False,'target_profile':'trusted-generated-subset/python-sqlite-json'}
        self.ledger.event(pid,'synthetic','Generating source-derived boundaries, matching records and interaction witnesses; freezing expectations before target execution')
        for name,p in doc['analysis']['programs'].items():
            if p['blockers']:continue
            suite=plan_cases(p,doc['authorization']['seed'],doc['authorization']['max_cases_per_program'])
            expected_path=runroot/name/'expected.json';write_new(expected_path,encode(suite));self.register(doc,f'synthetic/{run_id}/{name}/expected.json')
            target_path=self.root/'shared'/'target'/'python'/(doc['program_versions'][name]+'.py')
            code=target_path.read_text();require(sha(code)==doc['program_versions'][name],'Target version changed')
            write_new(root/'target'/run_id/(name+'.py'),code.encode());self.register(doc,f'target/{run_id}/{name}.py')
            result=verify_program(p,code,suite)
            adversarial={'method':'deterministic mutation/injection checks, not an independent human or LLM review','mutation_detected':False,'forbidden_import_rejected':False,'source_accounted':all(x['disposition']!='unaccounted' for x in p['coverage'])}
            tree=ast.parse(code)
            comparisons=[x for x in ast.walk(tree) if isinstance(x,ast.Compare)]
            if comparisons:
                comparisons[0].ops[0]=ast.NotEq() if isinstance(comparisons[0].ops[0],ast.Eq) else ast.Eq()
                adversarial['mutation_detected']=bool(verify_program(p,ast.unparse(tree),suite)['differences'])
            try:check_generated('import os\ndef run_program(record):\n return record\n')
            except ValidationError:adversarial['forbidden_import_rejected']=True
            result['adversarial']=adversarial
            write_new(runroot/name/'actual-and-comparison.json',encode(result));self.register(doc,f'synthetic/{run_id}/{name}/actual-and-comparison.json')
            run['programs'][name]=result
            if result['differences'] or not result['coverage']['complete'] or (comparisons and not adversarial['mutation_detected']):doc['blockers'].append({'kind':'verification_gap','program':name,'message':'Mismatch, uncovered branch or adversarial witness gap remains'})
        # Real local target database records actual computed outputs; never a source Db2 database.
        dbpath=root/'target'/run_id/'target.sqlite';dbpath.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(dbpath) as db:
            db.execute('CREATE TABLE results(program TEXT,case_id TEXT,result TEXT,PRIMARY KEY(program,case_id))')
            for name,result in run['programs'].items():db.executemany('INSERT INTO results VALUES(?,?,?)',[(name,r['case_id'],json.dumps(r['result'])) for r in result['actual']])
        self.register(doc,f'target/{run_id}/target.sqlite')
        if len(doc['program_versions'])==len(doc['analysis']['programs']) and not any(b['kind'] in ('missing_source','unresolved_condition','unsupported_jcl') for b in doc['blockers']):
            jobs=emit_jobs(doc,doc['program_versions']);write_new(root/'target'/run_id/'jobs.py',jobs.encode());self.register(doc,f'target/{run_id}/jobs.py')
            from .orchestration import verify_jobs
            result=verify_jobs(doc,self.root,jobs)
            write_new(root/'target'/run_id/'job-comparison.json',encode(result));self.register(doc,f'target/{run_id}/job-comparison.json')
            if not result['matched']:doc['blockers'].append({'kind':'job_integration_gap','message':result['reason']})
        doc['runs'].append(run);doc['knowledge_records']=update_knowledge(self.ledger,doc)
        self.ledger.event(pid,'verification','Local target comparisons complete; source-derived expectations remain distinct from observed mainframe results',{'programs':len(run['programs']),'unresolved':len(doc['blockers'])})
        doc['blockers']=[b for b in doc['blockers'] if not (b['kind']=='stage_failure' and b.get('stage')=='QUEUED_VERIFY')]
        doc['verification_finished']=True
        self.ledger.save(doc,'QUEUED_REPORT')

    def report(self,doc):
        from .reports import generate_reports
        try:
            if not doc.get('verification_finished') and not any(b['kind']=='verification_incomplete' for b in doc['blockers']):doc['blockers'].append({'kind':'verification_incomplete','message':'Verification did not finish; no unblocked completion is permitted'})
            doc['blockers']=[b for b in doc['blockers'] if not (b['kind']=='stage_failure' and b.get('stage')=='QUEUED_REPORT')]
            self.ledger.event(doc['id'],'report','Generating management metrics, before/after evidence and editable PowerPoint')
            paths=generate_reports(self.ledger,doc,self.process_root(doc['id'])/'reports'/f'report-{len(doc["runs"]):04d}')
            for p in paths:self.register(doc,str(p.relative_to(self.process_root(doc['id']))))
            doc['report_verified']=True
            self.ledger.save(doc,'COMPLETED_WITH_BLOCKERS' if doc['blockers'] else 'COMPLETED')
            self.ledger.event(doc['id'],'complete','Report inspection passed; technical completion recorded for the stated source-derived POC boundary')
        except Exception as exc:
            doc['report_error']=type(exc).__name__;doc['resume_status']='QUEUED_REPORT';self.ledger.save(doc,'REPORTING_FAILED');self.ledger.event(doc['id'],'report','Report generation/inspection failed; process is not marked done')

    def launch_worker(self):
        if self.worker:return
        def loop():
            while not self.stopped.wait(.2):
                for p in self.ledger.list(True):
                    if p['status'] not in ('QUEUED_ANALYSIS','QUEUED_VERIFY','QUEUED_REPORT'):continue
                    try:self.advance(p['id'])
                    except Exception as exc:
                        with self.lock:
                            doc=self.ledger.get(p['id']);doc['last_error']=type(exc).__name__;doc['resume_status']=p['status']
                            doc['blockers'].append({'kind':'stage_failure','stage':p['status'],'message':'Stage failed; successful recovery is required before completion'})
                            self.ledger.save(doc,'FAILED');self.ledger.event(p['id'],'error','Stage failed safely; evidence retained and Resume is available',{'error_type':type(exc).__name__})
        self.worker=threading.Thread(target=loop,daemon=True);self.worker.start()

    def close(self):
        if self.closed:return
        self.stopped.set()
        if self.worker:self.worker.join(timeout=5)
        if self.worker and self.worker.is_alive():self.worker.join()
        self.ledger.close();self.instance.close();self.closed=True
