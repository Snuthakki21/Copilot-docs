"""Execute record-based job orchestration against independently interpreted rules."""
import re
from .reference import run_reference
from .target import run_generated, emit_jobs
from .domain import encode, sha, require

def verify_jobs(doc,root,jobs,checkpoint=None):
    require(jobs==emit_jobs(doc,doc['program_versions']), 'Job template differs from validated manifest generation')
    programs=doc['analysis']['programs']
    if not programs:return {'matched':False,'reason':'No supported program to execute'}
    if any(p['blockers'] for p in programs.values()):return {'matched':False,'reason':'Unsupported source program cannot receive integration credit'}
    first=next(iter(programs.values()));fields=set(first['fields'])
    if any(set(p['fields'])!=fields for p in programs.values()):return {'matched':False,'reason':'Programs have different record layouts; an explicit input/output mapping adapter is required'}
    if any(any((p['fields'][k]['type'],p['fields'][k]['width'])!=(first['fields'][k]['type'],first['fields'][k]['width']) for k in fields) for p in programs.values()):return {'matched':False,'reason':'Record field types or widths differ; explicit record mapping is required'}
    record={k:v['default'] for k,v in first['fields'].items()};row=dict(record);expected={}
    for job in doc['jobs']:
        results=[];rc=0
        for step in job['steps']:
            if checkpoint:checkpoint()
            text=step['condition'].upper().replace(' ','');execute=text in ('ALWAYS','')
            if not execute:
                m=re.fullmatch(r'RC(<=|>=|=|<|>)(\d+)',text)
                if not m:return {'matched':False,'reason':'Unresolved job condition'}
                n=int(m[2]);execute={'<=':rc<=n,'>=':rc>=n,'=':rc==n,'<':rc<n,'>':rc>n}[m[1]]
            if execute:
                p=programs[step['program'].upper()];r=run_reference(p,row)
                if r['input_status']!='ACCEPT_INPUT':return {'matched':False,'reason':'Source reference rejected the integration record'}
                row=r['record'];rc=r['return_code'];results.append({'step':step['name'],'version':doc['program_versions'][p['name']],**r})
            else:results.append({'step':step['name'],'status':'SKIPPED'})
        expected[job['name']]=results
    target={}
    for name,v in doc['program_versions'].items():
        require(re.fullmatch(r'[a-f0-9]{64}',v) is not None,'Invalid pinned target version')
        code=(root/'shared/target/python'/f'{v}.py').read_text()
        require(sha(code)==v,'Pinned job target changed')
        def execute(record,code=code):
            if checkpoint:checkpoint()
            return run_generated(code,record)
        target[name]=execute
    namespace={'__builtins__':{}};exec(compile(jobs,'<trusted-job-generator>','exec'),namespace)
    actual=namespace['run_process']({'record':record},target)
    return {'matched':encode(expected)==encode(actual),'reason':'Ordered record-adapter job comparison; DSN I/O and external scheduling are outside this profile','expected':expected,'actual':actual,'observed_mainframe_parity':False,'integration_cases':1,'io_adapter':'in_memory_record_only','dataset_io_verified':False}
