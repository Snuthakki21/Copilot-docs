"""Deterministic source-driven boundaries, interactions and linked record groups."""
import itertools
import random
from .domain import encode, sha
from .reference import run_reference, input_errors
from .target import run_generated


def comparisons(node):
    if not isinstance(node,dict) or 'field' in node:return []
    return comparisons(node['left'])+comparisons(node['right']) if node['op'] in ('AND','OR') else [node]


def plan_cases(program, seed=21, budget=256):
    rng=random.Random(seed)
    base={k:f['default'] for k,f in program['fields'].items()}
    values={};comparators=[c for r in program['rules'] for c in comparisons(r['predicate'])]
    outputs={a['field'] for r in program['rules'] for a in r['then']+r['else']}
    for c in comparators:
        for side,other in [('left','right'),('right','left')]:
            field=c[side]
            if not isinstance(field,dict) or 'field' not in field:continue
            name=field['field'];f=program['fields'][name]
            values.setdefault(name,[f['default']])
            literal=c[other]
            if isinstance(literal,dict):
                if 'field' in literal:
                    peer=literal['field']
                    if f['type']=='string':
                        token=('SYN'+str(seed)).ljust(f['width'])[:f['width']];base[name]=token;base[peer]=token.ljust(program['fields'][peer]['width'])[:program['fields'][peer]['width']]
                        values[name]+=[base[name],'Z'*f['width']]
                    else:base[name]=base[peer]=1;values[name]+=[0,1,2]
                continue
            if f['type']=='integer' and type(literal)is int:values[name]+=[literal-1,literal,literal+1,0,f['max'],rng.randrange(f['max']+1)]
            if f['type']=='string' and type(literal)is str:values[name]+=[literal.ljust(f['width'])[:f['width']],' '*f['width'],'Z'*f['width']]
    cases=[];seen=set()
    def add(record,reason):
        fingerprint=sha(encode(record))
        if fingerprint in seen or len(cases)>=budget:return
        seen.add(fingerprint)
        expected=run_reference(program,record)
        groups={}
        for k,v in record.items():groups.setdefault(program['fields'][k]['group'],{})[k]=v
        cases.append({'id':f'case_{len(cases):04d}','reason':reason,'record':record,'files':{group:[row] for group,row in groups.items()},'expected':expected,'intentional_invalid':expected['input_status']=='REJECT_INPUT'})
    add(base.copy(),'Source-layout baseline with synthetic identities')
    for name,options in values.items():
        unique=list(dict.fromkeys(options));values[name]=unique
        for v in unique:add({**base,name:v},f'Boundary/domain witness: {name}={v!r}')
    for name,f in program['fields'].items():
        if name in outputs:continue
        for bad in ([-1,f['max']+1,'wrong-type'] if f['type']=='integer' else ['', 'X'*(f['width']+1),None]):add({**base,name:bad},f'Intentional input-layout violation: {name}')
    names=list(values)
    # Reserve layout violations before filling the remaining budget with interactions.
    for combination in itertools.islice(itertools.product(*(values[n] for n in names)),budget):add({**base,**dict(zip(names,combination))},'Source-predicate interaction witness')
    branches={r['id']:{'true':[],'false':[]} for r in program['rules']}
    for case in cases:
        for t in case['expected'].get('trace',[]):branches[t['rule_id']]['true' if t['branch'] else 'false'].append(case['id'])
    gaps=[{'rule_id':rid,'branch':branch,'status':'uncovered'} for rid,record in branches.items() for branch,witnesses in record.items() if not witnesses]
    coverage={'rule_count':len(branches),'branch_targets':len(branches)*2,'branches_observed':sum(bool(w) for b in branches.values() for w in b.values()),'rules':branches,'gaps':gaps,'complete':not gaps and not program['blockers'],'exhaustive':False,'claim':'Decision outcomes for the supported source IR; not all input/path/condition coverage or observed legacy parity.'}
    return {'version':1,'program':program['name'],'source_hash':program['source_hash'],'seed':seed,'evidence_basis':'SOURCE_DERIVED_EXPECTED','generator_version':'source-subset-1','cases':cases,'coverage':coverage,'contract_hash':sha(encode({'source':program['source_hash'],'seed':seed,'rules':program['rules'],'fields':program['fields']}))}


def verify_program(program,code,suite):
    actual=[];diffs=[]
    for case in suite['cases']:
        errors=input_errors(program,case['record'])
        got={'input_status':'REJECT_INPUT','errors':errors,'return_code':None} if errors else run_generated(code,case['record'])
        actual.append({'case_id':case['id'],'result':got})
        if encode(got)!=encode(case['expected']):diffs.append({'case_id':case['id'],'expected':case['expected'],'actual':got,'triage':'Target, oracle or adapter discrepancy; inspect source evidence before changing expectations.'})
    return {'status':'MISMATCH' if diffs else 'MATCHED_SOURCE_DERIVED_EXPECTATIONS' if suite['coverage']['complete'] else 'MATCHED_WITH_COVERAGE_GAPS','source_hash':program['source_hash'],'target_hash':sha(code),'contract_hash':suite['contract_hash'],'expected_count':len(suite['cases']),'matched_count':len(suite['cases'])-len(diffs),'differences':diffs,'actual':actual,'coverage':suite['coverage'],'observed_legacy_parity':False}
