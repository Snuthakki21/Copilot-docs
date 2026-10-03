"""Persistent Start → one SME exchange → verification → reports coordinator."""
import json
from pathlib import Path
import sqlite3
import threading
import time
from .domain import require, identity, safe_path, write_new, encode, decode, sha, ValidationError
from .intake import parse_manifest
from .ledger import Ledger, now
from .source import analyze_sources
from .target import emit_program, emit_jobs, check_generated
from .fixtures import plan_cases, verify_program
from .review import export_packet, read_answers
from .knowledge import update_knowledge
from .layout import require_layout, output_path


class StageInterrupted(Exception):
    pass


class Coordinator:
    def __init__(self, root):
        from .instance import InstanceLock
        require_layout(root)
        self.root=Path(root).resolve();self.instance=InstanceLock(self.root)
        self.lock=threading.RLock();self.stopped=threading.Event();self.worker=None;self.closed=False;self.active=set();self.ledger=None
        try:
            self.ledger=Ledger(self.root)
            from .provider import configured_provider
            self.provider=configured_provider()
            for p in self.ledger.list(True):
                prior_artifacts=len(p['artifacts'])
                hashes=p.get('artifact_hashes') or {}
                review_paths=['review/'+f for f in ('packet.json','sme-checklist.xlsx','sme-checklist.docx','sme-checklist.html')]
                legacy=not p.get('manifest_hash') or any(relative not in hashes for relative in p['artifacts']) or (p['packet_issued'] and any(relative not in hashes for relative in review_paths))
                if legacy:
                    already_flagged=any(b['kind']=='legacy_missing_baseline' for b in p['blockers'])
                    if not already_flagged:p['blockers'].append({'kind':'legacy_missing_baseline','message':'This preserved older process lacks immutable manifest/artifact baselines; original evidence is uncredited and target execution is prohibited. Preserve the old process; create a new intake from original exports to establish baselines.'})
                    final_hashes=p.get('report_hashes') or {}
                    accepted=p['status']=='COMPLETED_WITH_BLOCKERS' and p.get('report_verified') and already_flagged and bool(final_hashes)
                    if accepted:
                        for relative,fingerprint in final_hashes.items():
                            path=output_path(self.root,p['id'],relative)
                            if hashes.get(relative)!=fingerprint or not path.is_file() or sha(path.read_bytes())!=fingerprint:accepted=False;break
                    if not accepted:p['report_verified']=False;self.ledger.save(p,'QUEUED_REPORT')
                    continue # Never restore or repin mutable legacy artifacts.
                if p['status'] in ('COMPLETED','COMPLETED_WITH_BLOCKERS'):
                    try:self.manifest_integrity(p)
                    except (ValidationError,FileNotFoundError) as exc:
                        p['report_verified']=False
                        if not any(b['kind']=='evidence_integrity' for b in p['blockers']):p['blockers'].append({'kind':'evidence_integrity','message':str(exc)})
                        p=self.ledger.save(p,'QUEUED_REPORT')
                if p['packet_issued']:
                    for file in ['packet.json','sme-checklist.xlsx','sme-checklist.docx','sme-checklist.html']:
                        require(safe_path(self.process_root(p['id']),'review/'+file).is_file(),'Issued packet is incomplete; recover its preserved snapshot')
                        self.register(p,'review/'+file)
                if p['status'] in ('ANALYZING','VERIFYING','REPORTING'):
                    status='QUEUED_REPORT' if p['status']=='REPORTING' or p.get('cancel_requested') or p.get('verification_finished') else 'QUEUED_ANALYSIS' if not p['packet_issued'] else 'QUEUED_VERIFY' if p['packet_imported'] else 'WAITING_SME'
                    self.ledger.save(p,status)
                elif len(p['artifacts'])!=prior_artifacts:self.ledger.save(p)
        except Exception:
            try:
                if self.ledger:self.ledger.close()
            finally:self.instance.close()
            raise

    def process_root(self,pid):return safe_path(self.root,'processes/'+identity(pid))

    def create(self, manifest_text, source_files=None, demo=False, prompt=''):
        require_layout(self.root)
        manifest=parse_manifest(manifest_text)
        if source_files is None:
            folder=self.root/'Endeavor';source_files={}
            if folder.exists():
                require(folder.is_dir(),'Endeavor must be a source-export directory')
                for entry,path in enumerate(folder.rglob('*'),1):
                    require(entry<=10000,'Source directory traversal exceeds 10,000 entries; provide a process-scoped export')
                    require(not path.is_symlink(),'Symlinks are not accepted in Endeavor')
                    require(path.is_dir() or path.is_file(),'Endeavor accepts only regular source files and directories')
                    if path.is_file():
                        relative=path.relative_to(folder).as_posix()
                        require(path.stat().st_size<=512000 and len(source_files)<200,'Endeavor export exceeds bounds: '+relative)
                        try:source_files[relative]=path.read_bytes().decode('utf-8')
                        except UnicodeError as exc:raise ValidationError('Endeavor file is not UTF-8 text: '+relative+'; supply a readable export for explicit source accounting') from exc
        require(isinstance(source_files,dict) and 0<len(source_files)<=200,'Provide a source folder with 1 to 200 supported text files')
        require(all(isinstance(k,str) and isinstance(v,str) for k,v in source_files.items()),'Source filenames and contents must be text')
        require(all('\x00' not in value for value in source_files.values()),'Source contains NUL/binary content; provide readable source separately from data/load modules')
        from .domain import MAX_SOURCE_LINES
        require(sum(len(value.splitlines()) for value in source_files.values())<=MAX_SOURCE_LINES,'Source export exceeds 100,000 physical lines; provide a process-scoped export before generating coverage')
        require(isinstance(prompt,str),'Analysis prompt must be text')
        try:
            encoded_sources={path:text.encode('utf-8') for path,text in source_files.items()}
            for path in source_files:path.encode('utf-8')
            encoded_manifest=manifest_text.encode('utf-8');prompt.encode('utf-8')
        except UnicodeError as exc:raise ValidationError('Source filenames, source text, manifest and prompt must be valid UTF-8 text without unpaired surrogates') from exc
        require(sum(len(raw) for raw in encoded_sources.values())<=8*1024*1024,'Source export exceeds size bound')
        # Reject collisions before any immutable process evidence is created.
        import unicodedata
        portable={}
        for path in source_files:
            require(Path(path).as_posix()==path and all(part not in ('','.','..') for part in path.split('/')),'Source paths must be canonical relative filenames')
            folded=unicodedata.normalize('NFC',path).casefold()
            require(folded not in portable,'Source filenames collide across supported platforms: '+path)
            portable[folded]=path
        require(not any('/'.join(path.split('/')[:i]) in portable for path in portable for i in range(1,len(path.split('/')))), 'Source file/directory names collide across supported platforms')
        from .mainframe import load_knowledge
        knowledge=load_knowledge(self.root)
        with self.lock:
            require_layout(self.root)
            require(not self.process_root(manifest['id']).exists(),'Process directory already exists')
            require(not any(p.name.casefold()==manifest['id'].casefold() for p in (self.root/'processes').glob('*')),'Process ID collides on case-insensitive platforms; use a unique ID')
            for path,text in source_files.items():
                output_path(self.root,manifest['id'],'input/sources/'+path)
                require(len(encoded_sources[path])<=512000,'Source file exceeds bounds: '+path)
            doc=self.ledger.create(manifest,demo)
            try:
                base=self.process_root(doc['id']);write_new(base/'input'/'process-input.md',encoded_manifest)
                hashes={}
                for path,raw in encoded_sources.items():hashes[path]=write_new(output_path(self.root,doc['id'],'input/sources/'+path),raw)
                doc['source_files']=hashes;doc['manifest_hash']=sha(encoded_manifest);doc['prompt']=prompt[:16000]
                doc['mainframe_knowledge']=knowledge
                write_new(base/'analysis'/'mainframe-knowledge.json',encode(knowledge))
                self.register(doc,'analysis/mainframe-knowledge.json')
                return self.ledger.save(doc)
            except Exception:
                doc['blockers']=[{'kind':'intake_storage','message':'Input storage failed; preserved available evidence.'}];self.ledger.save(doc,'FAILED');raise

    def start(self,pid):
        with self.lock:
            require_layout(self.root)
            doc=self.ledger.get(pid);self.manifest_integrity(doc);require(doc['status']=='READY','Process already started; use Resume when applicable')
            doc['authorization']={'recorded':now(),'scope':doc['source_files'],'target':'trusted-generated-subset/python-sqlite','seed':21,'max_cases_per_program':256,'max_repair_attempts':1,'source_operations':'read-only','mainframe_execution':False}
            return self.ledger.save_event(doc,'QUEUED_ANALYSIS','start','Start authorization recorded; source writes and mainframe execution are prohibited')

    def control(self,pid,action):
        with self.lock:
            doc=self.ledger.get(pid)
            require(doc['status'] not in ('COMPLETED','COMPLETED_WITH_BLOCKERS'),'Terminal evidence cannot be changed in place')
            if action=='pause':
                require(doc['status'] in ('QUEUED_ANALYSIS','ANALYZING','WAITING_SME','QUEUED_VERIFY','VERIFYING','QUEUED_REPORT','REPORTING'),'There is no running stage to pause; use Resume to recover a failed stage')
                doc['resume_status']={'ANALYZING':'QUEUED_ANALYSIS','VERIFYING':'QUEUED_VERIFY','REPORTING':'QUEUED_REPORT'}.get(doc['status'],doc['status']);status='PAUSED'
            elif action=='resume':
                require(doc['status'] in ('PAUSED','FAILED','REPORTING_FAILED'),'Nothing eligible to resume')
                status=doc.pop('resume_status','QUEUED_REPORT' if doc['packet_imported'] else 'WAITING_SME' if doc['packet_issued'] else 'QUEUED_ANALYSIS')
                if doc['status'] in ('FAILED','REPORTING_FAILED'):doc.setdefault('stage_attempts',{})[status]=0
                if status=='QUEUED_ANALYSIS' and doc['packet_issued']:status='QUEUED_VERIFY' if doc['packet_imported'] else 'WAITING_SME'
                if status=='QUEUED_VERIFY' and doc.get('verification_finished'):status='QUEUED_REPORT'
                doc['next_retry_at']=0
            elif action=='cancel':
                if not any(b['kind']=='cancelled' for b in doc['blockers']):doc['blockers'].append({'kind':'cancelled','message':'Operator cancelled this process'})
                doc['cancel_requested']=True;status='QUEUED_REPORT'
            else:raise ValidationError('Unknown control')
            doc['control_revision']=doc.get('control_revision',0)+1
            return self.ledger.save_event(doc,status,action,'Operator '+action+' recorded; existing SME quota retained')

    def checkpoint(self,doc,status=None,persist=True):
        """Accept durable controls under a short lock; workers never overwrite them."""
        with self.lock:
            current=self.ledger.get(doc['id']) if persist or status else self.ledger.controls(doc['id'])
            interrupted=current['status']=='PAUSED' or (current.get('cancel_requested') and doc.get('_active_stage')!='QUEUED_REPORT') or self.closed
            for key in ('control_revision','cancel_requested','resume_status'):
                if key in current:doc[key]=current[key]
            for blocker in current['blockers']:
                if blocker['kind']=='cancelled' and blocker not in doc['blockers']:doc['blockers'].append(blocker)
            if interrupted:
                target=current['status']
                if self.closed and target not in ('PAUSED','QUEUED_REPORT'):target=doc['_active_stage']
                self.ledger.save(doc,target);raise StageInterrupted()
            if status in ('COMPLETED','COMPLETED_WITH_BLOCKERS'):status='COMPLETED_WITH_BLOCKERS' if doc['blockers'] else 'COMPLETED'
            return self.ledger.save(doc,status) if persist or status else current

    def stage_success(self,doc,stage):
        doc['blockers']=[b for b in doc['blockers'] if not (b['kind']=='stage_failure' and b.get('stage')==stage)]
        doc.pop('last_failure',None);doc.pop('last_error',None);doc.pop('resume_status',None);doc['next_retry_at']=0

    def artifact(self,pid,relative):
        doc=self.ledger.get(pid);require(relative in doc['artifacts'],'Artifact not registered for this process')
        path=output_path(self.root,pid,relative)
        final_report=Path(relative).parts[0]=='reports' and relative in doc.get('report_hashes',{})
        if not final_report:self.manifest_integrity(doc)
        require(path.is_file(),'Artifact unavailable')
        fingerprint=doc.get('artifact_hashes',{}).get(relative)
        require(fingerprint,'Registered artifact baseline is missing; preserved evidence cannot be certified or silently repinned')
        require(sha(path.read_bytes())==fingerprint,'Registered artifact changed after freezing: '+relative)
        if relative in doc.get('report_hashes',{}):require(fingerprint==doc['report_hashes'][relative],'Report artifact differs from its inspected version')
        return path

    def register(self,doc,relative):
        path=output_path(self.root,doc['id'],relative)
        require(path.is_file(),'Artifact registration requires an existing regular file: '+relative)
        fingerprint=sha(path.read_bytes());hashes=doc.setdefault('artifact_hashes',{})
        if relative in doc['artifacts'] or relative in hashes:
            require(relative in hashes,'Registered artifact baseline is missing; preserved evidence cannot be silently repinned: '+relative)
            require(hashes[relative]==fingerprint,'Registered artifact changed after freezing: '+relative)
        else:hashes[relative]=fingerprint
        if relative not in doc['artifacts']:doc['artifacts'].append(relative)

    def import_answers(self,pid,data,reviewer):
        with self.lock:
            require_layout(self.root)
            doc=self.ledger.get(pid);self.sources(doc);require(doc['status']=='WAITING_SME','Process is not waiting for SME answers')
            packet=decode(self.artifact(pid,'review/packet.json').read_bytes())
            require(packet.get('packet_hash')==doc['packet_hash'] and sha(encode({k:v for k,v in packet.items() if k!='packet_hash'}))==doc['packet_hash'],'Frozen SME packet integrity failed')
            require(packet.get('process_id')==pid and packet.get('source_snapshot')==doc['analysis']['source_snapshot'],
                    'Frozen SME packet does not belong to this process and source snapshot')
            answers=read_answers(data,packet,reviewer)
            returned=self.process_root(pid)/'input'/'sme-return.xlsx'
            if returned.exists():require(returned.read_bytes()==data,'Recovery return differs from the preserved SME file')
            else:write_new(returned,data)
            self.ledger.consume_return(pid,answers)
            return self.ledger.get(pid)

    def manifest_integrity(self,doc):
        require(doc.get('manifest_hash'),'Frozen manifest baseline is missing; preserve this process and create a new intake with an original manifest baseline; never pin an existing mutable file on Resume')
        raw=output_path(self.root,doc['id'],'input/process-input.md').read_bytes()
        require(sha(raw)==doc['manifest_hash'],'Frozen process manifest changed; existing evidence cannot be credited')
        frozen=parse_manifest(raw.decode('utf-8'))
        require(all(frozen[key]==doc[key] for key in ('id','name','jobs')),'Process metadata differs from the frozen manifest')
        if 'mainframe_knowledge' in doc or 'analysis/mainframe-knowledge.json' in doc.get('artifact_hashes',{}):
            from .mainframe import validate_snapshot
            snapshot=doc.get('mainframe_knowledge');validate_snapshot(snapshot)
            relative='analysis/mainframe-knowledge.json'
            raw=output_path(self.root,doc['id'],relative).read_bytes()
            require(raw==encode(snapshot) and sha(raw)==doc.get('artifact_hashes',{}).get(relative),'Frozen mainframe knowledge changed; preserve the original process evidence')

    def review_integrity(self,doc):
        self.manifest_integrity(doc)
        if not doc['packet_issued']:return
        for file in ('packet.json','sme-checklist.xlsx','sme-checklist.docx','sme-checklist.html'):self.artifact(doc['id'],'review/'+file)
        packet=decode((self.process_root(doc['id'])/'review'/'packet.json').read_bytes())
        require(packet.get('packet_hash')==doc['packet_hash'] and sha(encode({k:v for k,v in packet.items() if k!='packet_hash'}))==doc['packet_hash'],'Frozen SME packet integrity failed')
        require(packet['source_snapshot']==doc['analysis']['source_snapshot'],'SME packet differs from the frozen source snapshot')
        if doc['packet_imported']:
            answers=doc.get('answers') or {};raw=safe_path(self.process_root(doc['id']),'input/sme-return.xlsx').read_bytes()
            require(sha(raw)==answers.get('return_hash'),'Preserved SME return changed')
            require(read_answers(raw,packet,answers.get('reviewer',''))==answers,'SME answers differ from the preserved return')

    def target_checkpoint(self,doc):
        self.checkpoint(doc,persist=False)
        require(not doc.get('cancel_requested'),'Cancelled: target execution is prohibited')
        require(not any(b['kind']=='legacy_missing_baseline' for b in doc['blockers']),'Legacy immutable baselines are missing: target execution is prohibited')

    def sources(self,doc):
        self.manifest_integrity(doc)
        source_root=self.process_root(doc['id'])/'input'/'sources'
        inventory=set()
        for count,path in enumerate(source_root.rglob('*'),1):
            require(count<=10000,'Frozen source traversal exceeds 10,000 entries')
            require(not path.is_symlink() and (path.is_file() or path.is_dir()),
                    'Source snapshot contains an unsafe file')
            if path.is_file():inventory.add(path.relative_to(source_root).as_posix())
        require(inventory==set(doc['source_files']),
                'Source snapshot file inventory changed; every exported file must retain its frozen accounting')
        result={}
        for path,h in doc['source_files'].items():
            raw=safe_path(self.process_root(doc['id'])/'input'/'sources',path).read_bytes()
            require(sha(raw)==h,'Source snapshot changed; existing evidence cannot be credited')
            result[path]=raw.decode('utf-8')
        return result

    def advance(self,pid):
        with self.lock:
            require_layout(self.root)
            doc=self.ledger.get(pid);stage=doc['status']
            if pid in self.active or stage not in ('QUEUED_ANALYSIS','QUEUED_VERIFY','QUEUED_REPORT') or doc.get('next_retry_at',0)>time.time():return doc
            self.active.add(pid);doc['_active_stage']=stage
            doc.setdefault('stage_attempts',{})[stage]=doc.get('stage_attempts',{}).get(stage,0)+1
            self.ledger.save(doc,{'QUEUED_ANALYSIS':'ANALYZING','QUEUED_VERIFY':'VERIFYING','QUEUED_REPORT':'REPORTING'}[stage])
        try:
            {'QUEUED_ANALYSIS':self.analyze,'QUEUED_VERIFY':self.verify,'QUEUED_REPORT':self.report}[stage](doc)
        except StageInterrupted:pass
        except Exception as exc:
            with self.lock:
                current=self.ledger.get(pid)
                if current['status']=='PAUSED' or (current.get('cancel_requested') and stage!='QUEUED_REPORT') or self.closed:
                    try:self.checkpoint(doc)
                    except StageInterrupted:return self.ledger.get(pid)
                else:
                    if stage=='QUEUED_REPORT':doc['report_verified']=False
                    doc['last_error']=type(exc).__name__;doc['last_failure']={'stage':stage,'attempt':doc['stage_attempts'][stage],'type':type(exc).__name__,'message':str(exc)[:1000],'recorded':now()};doc['resume_status']=stage
                    transient=isinstance(exc,(OSError,TimeoutError,sqlite3.OperationalError)) and not isinstance(exc,(FileNotFoundError,PermissionError))
                    retry=transient and doc['stage_attempts'][stage]<3
                    doc['blockers']=[b for b in doc['blockers'] if not (b['kind']=='stage_failure' and b.get('stage')==stage)]
                    doc['blockers'].append({'kind':'stage_failure','stage':stage,'message':'Stage failed; successful recovery is required before completion','failure':doc['last_failure']})
                    doc['next_retry_at']=time.time()+.1*doc['stage_attempts'][stage] if retry else 0
                    self.ledger.save(doc,stage if retry else 'REPORTING_FAILED' if stage=='QUEUED_REPORT' else 'FAILED')
                    self.ledger.event(pid,'error','Transient stage retry queued' if retry else 'Stage failed safely; evidence retained',doc['last_failure'])
            raise
        finally:
            with self.lock:
                self.active.discard(pid)
                if self.closed and (not self.worker or not self.worker.is_alive()):self._release()
        return self.ledger.get(pid) if self.ledger is not None else doc

    def analyze(self,doc):
        pid=doc['id'];self.checkpoint(doc,'ANALYZING');self.ledger.event(pid,'analysis','Reading complete source snapshot and extracting supported atomic rules')
        source_files=self.sources(doc)
        analysis=doc.get('analysis') or analyze_sources(source_files,doc);self.checkpoint(doc);doc['analysis']=analysis;doc['blockers']=list(analysis['blockers'])
        context_path=self.root/'knowledge'/'inbox'/'context.md'
        if context_path.exists() and 'knowledge_context' not in doc:
            require(not context_path.is_symlink() and context_path.stat().st_size<=16000,'Knowledge context must be a regular Markdown file of at most 16 KB')
            doc['knowledge_context']={'text':context_path.read_text(),'sha256':sha(context_path.read_bytes()),'status':'UNVERIFIED_INPUT'}
        from .connectors import read_only_discovery
        if 'discovery' not in doc:doc['discovery']=read_only_discovery()
        doc.setdefault('llm',{'status':'NOT_CONFIGURED','live_ready':False})
        if self.provider and doc['llm']['status']=='NOT_CONFIGURED':
            try:
                context=''
                if doc.get('mainframe_knowledge'):
                    facts={'status':'UNVERIFIED_CONTEXT_NOT_CONVERSION_PROOF',
                           'classifications':{path:record['kind'] for path,record in analysis.get('classifications',{}).items()},
                           'utility_findings':analysis.get('utility_findings',[]),
                           'application':doc['mainframe_knowledge']['application']}
                    context='Frozen mainframe context (bounded excerpt; full facts are in the SME packet):\n'+json.dumps(facts,ensure_ascii=False)[:4000]+'\nSource excerpts:\n'
                excerpts=(context+'\n'.join(p['source_text'] for p in analysis['programs'].values())+'\nUnverified background knowledge:\n'+doc.get('knowledge_context',{}).get('text',''))[:16000]
                doc['llm']={'status':'ANALYSIS_RETURNED',**self.provider.analyze(excerpts,doc.get('prompt') or 'Review this process and identify assumptions for its one SME checklist.')}
            except ValidationError as exc:
                doc['llm']={'status':'UNAVAILABLE','message':str(exc),'live_ready':False}
                doc['blockers'].append({'kind':'llm_unavailable','message':str(exc)})
        self.checkpoint(doc)
        self.ledger.register_assets(pid,analysis['assets'])
        root=self.process_root(pid)
        analysis_path=root/'analysis'/'source-analysis.json'
        if analysis_path.exists():require(analysis_path.read_bytes()==encode(analysis),'Analysis recovery disagrees with frozen evidence')
        else:write_new(analysis_path,encode(analysis))
        self.register(doc,'analysis/source-analysis.json')
        doc['program_versions']={}
        for name,program in analysis['programs'].items():
            self.checkpoint(doc)
            if program['blockers']:continue
            code=emit_program(program);check_generated(code)
            version=sha(code);doc['program_versions'][name]=version
            path=self.root/'shared'/'target'/'python'/(version+'.py')
            if not path.exists():write_new(path,code.encode())
            require(path.read_text()==code,'Shared target version integrity failed')
        if self.ledger.get(pid)['packet_issued']:
            packet=decode((root/'review'/'packet.json').read_bytes())
            require(packet.get('packet_hash')==self.ledger.get(pid)['packet_hash'] and sha(encode({k:v for k,v in packet.items() if k!='packet_hash'}))==packet['packet_hash'],'Issued packet integrity failed')
            require(packet['source_snapshot']==analysis['source_snapshot'] and packet['process_id']==pid,'Issued packet does not belong to the frozen process')
        else:packet=export_packet(doc,root/'review')
        for file in ['packet.json','sme-checklist.xlsx','sme-checklist.docx','sme-checklist.html']:self.register(doc,'review/'+file)
        self.checkpoint(doc,'ANALYZING')
        with self.lock:
            self.checkpoint(doc)
            if not self.ledger.get(pid)['packet_issued']:self.ledger.issue_packet(pid,packet['packet_hash'])
            else:require(self.ledger.get(pid)['packet_hash']==packet['packet_hash'],'Recovered packet differs from issued quota')
        self.ledger.event(pid,'review','The single comprehensive checklist is ready for download',{'rules':len(analysis['rules']),'blockers':len(analysis['blockers'])})
        self.stage_success(doc,'QUEUED_ANALYSIS');self.checkpoint(doc,'WAITING_SME')

    def verify(self,doc):
        pid=doc['id'];root=self.process_root(pid);self.checkpoint(doc,'VERIFYING')
        try:self.sources(doc);self.review_integrity(doc)
        except (ValidationError,FileNotFoundError) as exc:
            doc['blockers'].append({'kind':'evidence_integrity','message':str(exc)});self.checkpoint(doc,'QUEUED_REPORT');return
        if doc.get('verification_finished'):
            doc['knowledge_records']=update_knowledge(self.ledger,doc)
            self.stage_success(doc,'QUEUED_VERIFY');self.checkpoint(doc,'QUEUED_REPORT');return
        require(doc['packet_imported'] and doc['answers'],'Verification requires the frozen SME return')
        require(decode((root/'analysis'/'source-analysis.json').read_bytes())==doc['analysis'],'Analysis snapshot changed')
        doc['blockers']=[b for b in doc['blockers'] if b['kind'] not in ('sme_unresolved','verification_gap','job_integration_gap')]
        for rid,answer in doc['answers']['items'].items():
            if answer['answer']!='Yes' or answer['correction']:doc['blockers'].append({'kind':'sme_unresolved','item_id':rid,'message':'SME item '+rid+': '+answer['answer']+'. '+answer['correction'],'correction_preserved':bool(answer['correction'])})
        prior=[int(p.name[4:]) for p in (root/'synthetic').glob('run-*') if p.name[4:].isdigit()]
        run_id=f'run-{max([len(doc["runs"]),*prior])+1:04d}';runroot=root/'synthetic'/run_id;runroot.mkdir(parents=True,exist_ok=False)
        run={'id':run_id,'created':now(),'programs':{},'evidence_basis':'SOURCE_DERIVED_EXPECTED','observed_legacy_parity':False,'target_profile':'trusted-generated-subset/python-sqlite-json'}
        self.ledger.event(pid,'synthetic','Generating source-derived boundaries, matching records and interaction witnesses; freezing expectations before target execution')
        for name,p in doc['analysis']['programs'].items():
            if p['blockers']:continue
            self.checkpoint(doc)
            suite=plan_cases(p,doc['authorization']['seed'],doc['authorization']['max_cases_per_program']);self.checkpoint(doc)
            expected_path=runroot/name/'expected.json';write_new(expected_path,encode(suite));self.register(doc,f'synthetic/{run_id}/{name}/expected.json')
            target_path=self.root/'shared'/'target'/'python'/(doc['program_versions'][name]+'.py')
            code=target_path.read_text();require(sha(code)==doc['program_versions'][name],'Target version changed')
            write_new(root/'target'/run_id/(name+'.py'),code.encode());self.register(doc,f'target/{run_id}/{name}.py')
            self.checkpoint(doc)
            result=verify_program(p,code,suite,checkpoint=lambda:self.checkpoint(doc,persist=False));self.checkpoint(doc)
            from .fixtures import adversarial_review
            adversarial=adversarial_review(p,code,suite,checkpoint=lambda:self.checkpoint(doc,persist=False));self.checkpoint(doc)
            result['adversarial']=adversarial
            write_new(runroot/name/'actual-and-comparison.json',encode(result));self.register(doc,f'synthetic/{run_id}/{name}/actual-and-comparison.json')
            self.checkpoint(doc)
            run['programs'][name]=result
            if result['differences'] or not result['coverage']['complete'] or not adversarial['passed']:doc['blockers'].append({'kind':'verification_gap','program':name,'message':'Mismatch, uncovered branch or adversarial witness gap remains'})
        # Real local target database records actual computed outputs; never a source Db2 database.
        dbpath=root/'target'/run_id/'target.sqlite';dbpath.parent.mkdir(parents=True,exist_ok=True)
        db=sqlite3.connect(dbpath)
        try:
            with db:
                db.execute('CREATE TABLE results(program TEXT,case_id TEXT,result TEXT,PRIMARY KEY(program,case_id))')
                for name,result in run['programs'].items():db.executemany('INSERT INTO results VALUES(?,?,?)',[(name,r['case_id'],json.dumps(r['result'])) for r in result['actual']])
        finally:db.close()
        self.register(doc,f'target/{run_id}/target.sqlite')
        if len(doc['program_versions'])==len(doc['analysis']['programs']) and not any(b['kind'] in ('missing_source','unresolved_condition','unsupported_jcl','scope_mismatch','unsupported_utility','source_classification','unsupported_source') for b in doc['blockers']):
            jobs=emit_jobs(doc,doc['program_versions']);write_new(root/'target'/run_id/'jobs.py',jobs.encode());self.register(doc,f'target/{run_id}/jobs.py')
            from .orchestration import verify_jobs
            self.checkpoint(doc)
            result=verify_jobs(doc,self.root,jobs,checkpoint=lambda:self.checkpoint(doc,persist=False));self.checkpoint(doc)
            write_new(root/'target'/run_id/'job-comparison.json',encode(result));self.register(doc,f'target/{run_id}/job-comparison.json')
            if not result['matched']:doc['blockers'].append({'kind':'job_integration_gap','message':result['reason']})
        self.checkpoint(doc)
        doc['runs'].append(run);doc['verification_finished']=True;self.checkpoint(doc)
        doc['knowledge_records']=update_knowledge(self.ledger,doc)
        self.ledger.event(pid,'verification','Local target comparisons complete; source-derived expectations remain distinct from observed mainframe results',{'programs':len(run['programs']),'unresolved':len(doc['blockers'])})
        doc['blockers']=[b for b in doc['blockers'] if not (b['kind']=='stage_failure' and b.get('stage')=='QUEUED_VERIFY')]
        doc['verification_finished']=True
        self.stage_success(doc,'QUEUED_VERIFY');self.checkpoint(doc,'QUEUED_REPORT')

    def report(self,doc):
        require_layout(self.root)
        from .reports import generate_reports
        from .coverage import build_coverage
        self.checkpoint(doc,'REPORTING')
        try:self.review_integrity(doc)
        except (ValidationError,FileNotFoundError) as exc:
            if not any(b['kind']=='evidence_integrity' for b in doc['blockers']):doc['blockers'].append({'kind':'evidence_integrity','message':str(exc)})
        if not doc.get('verification_finished') and not any(b['kind']=='verification_incomplete' for b in doc['blockers']):doc['blockers'].append({'kind':'verification_incomplete','message':'Verification did not finish; no unblocked completion is permitted'})
        self.stage_success(doc,'QUEUED_REPORT')
        doc['blockers']=[b for b in doc['blockers'] if b['kind']!='source_accountability']
        coverage=build_coverage(doc,self.root,checkpoint=lambda:self.target_checkpoint(doc));doc['coverage_summary']=coverage['summary']
        if not coverage['summary']['completion_eligible']:doc['blockers'].append({'kind':'source_accountability','message':'Source accounting, applicable verification or evidence integrity gate remains unmet'})
        self.ledger.event(doc['id'],'report','Generating management metrics, source accounting and editable PowerPoint')
        root=self.process_root(doc['id']);versions=[int(p.name[7:]) for p in (root/'reports').glob('report-*') if p.name[7:].isdigit()]
        output=root/'reports'/f'report-{max([0,*versions])+1:04d}'
        generated_cancelled=bool(doc.get('cancel_requested'))
        try:paths=generate_reports(self.ledger,doc,output,checkpoint=lambda:self.target_checkpoint(doc))
        finally:
            # Even an interrupted writer's partial files remain reviewable evidence.
            if output.exists():
                for partial in output.rglob('*'):
                    if partial.is_file() and not partial.is_symlink():self.register(doc,str(partial.relative_to(root)))
        self.checkpoint(doc)
        required={'metrics.json','metrics.csv','metrics.xlsx','management.pptx','inspection.json','coverage.json','coverage.csv','coverage.xlsx','coverage.html','executive-report.html'}
        require(required.issubset({Path(p).name for p in paths}),'Mandatory report or source coverage outputs missing')
        hashes={}
        for path in paths:
            path=Path(path);relative=str(path.relative_to(root));safe_path(root,relative)
            require(path.is_file() and path.stat().st_size>0,'Generated report artifact missing or empty')
            self.register(doc,relative);hashes[relative]=sha(path.read_bytes())
        inspection=decode((output/'inspection.json').read_bytes());require(inspection.get('verified') is True,'Report inspection did not pass')
        require(inspection.get('primary_report')=='executive-report.html'
                and inspection.get('executive_schema_version')==1
                and inspection.get('executive_html_checked') is True,
                'Executive report inspection did not pass')
        require((required-{'inspection.json'}).issubset(inspection.get('sha256',{})),'Report inspection omitted mandatory artifact hashes')
        for name,fingerprint in inspection.get('sha256',{}).items():require(sha((output/name).read_bytes())==fingerprint,'Report inspection hash differs')
        with self.lock:
            self.checkpoint(doc)
            if bool(doc.get('cancel_requested'))!=generated_cancelled:
                doc['report_verified']=False;self.checkpoint(doc,'QUEUED_REPORT');raise StageInterrupted()
            doc['report_hashes']=hashes;doc['report_verified']=True
            self.ledger.complete_report(doc,decode((output/'metrics.json').read_bytes())['metrics'])

    def launch_worker(self):
        if self.worker:return
        def loop():
            try:
                while not self.stopped.wait(.1):
                    for p in self.ledger.list(True):
                        if self.stopped.is_set():break
                        if p['status'] not in ('QUEUED_ANALYSIS','QUEUED_VERIFY','QUEUED_REPORT'):continue
                        try:self.advance(p['id'])
                        except Exception:pass # advance persists bounded retry/failure.
            finally:
                if self.closed:self._release()
        self.worker=threading.Thread(target=loop,daemon=True);self.worker.start()

    def _release(self):
        with self.lock:
            if self.active:return
            if self.ledger is not None:
                ledger=self.ledger;self.ledger=None
                try:ledger.close()
                finally:self.instance.close()

    def close(self):
        if self.closed:return
        self.closed=True;self.stopped.set()
        if self.worker:self.worker.join(timeout=.5)
        if not self.worker or not self.worker.is_alive():self._release()
