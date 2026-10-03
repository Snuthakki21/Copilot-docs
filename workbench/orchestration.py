"""Execute record-based job orchestration against independently interpreted rules."""
import re
from .reference import run_reference
from .target import run_generated
from .domain import encode

def verify_jobs(doc,root,jobs):
    programs=doc['analysis']['programs']
    if not programs:return {'matched':False,'reason':'No supported program to execute'}
    first=next(iter(programs.values()));fields=set(first['fields'])
    if any(set(p['fields'])!=fields for p in programs.values()):return {'matched':False,'reason':'Programs have different record layouts; an explicit input/output mapping adapter is required'}
    record={k:v['default'] for k,v in first['fields'].items()};row=dict(record);expected={}
    for job in doc['jobs']:
        results=[];rc=0
        for step in job['steps']:
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
        code=(root/'shared/target/python'/f'{v}.py').read_text();target[name]=lambda r,code=code:run_generated(code,r)
    namespace={'__builtins__':{}};exec(compile(jobs,'<trusted-job-generator>','exec'),namespace)
    actual=namespace['run_process']({'record':record},target)
    return {'matched':encode(expected)==encode(actual),'reason':'Ordered record-adapter job comparison; DSN I/O and external scheduling are outside this profile','expected':expected,'actual':actual,'observed_mainframe_parity':False,'integration_cases':1}
