"""Deterministic source-driven boundaries, interactions and linked record groups."""
import itertools
import ast
import copy
import random
from .domain import encode, sha, require
from .reference import run_reference, input_errors
from .target import run_generated


def comparisons(node):
    if not isinstance(node,dict) or 'field' in node:return []
    return comparisons(node['left'])+comparisons(node['right']) if node['op'] in ('AND','OR') else [node]


def plan_cases(program, seed=21, budget=256):
    require(type(budget) is int and 1<=budget<=256,'Case budget must be between 1 and 256')
    rng=random.Random(seed)
    base={k:f['default'] for k,f in program['fields'].items()}
    values={};comparators=[c for r in program['rules'] for c in comparisons(r['predicate'])]
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
    candidates={};cases=[]
    def add(record,reason,mandatory=True):
        fingerprint=sha(encode(record))
        if fingerprint in candidates:
            candidates[fingerprint]['mandatory'] |= mandatory
            return
        expected=run_reference(program,record)
        groups={}
        for k,v in record.items():groups.setdefault(program['fields'][k]['group'],{})[k]=v
        candidates[fingerprint]={'mandatory':mandatory,'reason':reason,'record':record,'files':{group:[row] for group,row in groups.items()},'expected':expected,'intentional_invalid':expected['input_status']=='REJECT_INPUT'}
    add(base.copy(),'Source-layout baseline with synthetic identities')
    for name,options in values.items():
        unique=list(dict.fromkeys(options));values[name]=unique
        for v in unique:add({**base,name:v},f'Boundary/domain witness: {name}={v!r}')
    for name,f in program['fields'].items():
        for bad in ([-1,f['max']+1,'wrong-type'] if f['type']=='integer' else ['', 'X'*(f['width']+1),None]):add({**base,name:bad},f'Intentional input-layout violation: {name}')
    names=list(values)
    # Reserve layout violations before filling the remaining budget with interactions.
    for combination in itertools.islice(itertools.product(*(values[n] for n in names)),min(4096,budget*16)):add({**base,**dict(zip(names,combination))},'Source-predicate interaction witness',False)
    # Select decision witnesses first; every omitted mandatory boundary/invalid
    # record is still reported. A budget must never silently erase obligations.
    remaining={(r['id'],b) for r in program['rules'] for b in (True,False)}
    selected=set()
    def select(key):
        if key in selected or len(cases)>=budget:return
        case=dict(candidates[key]);case.pop('mandatory');case['id']=f'case_{len(cases):04d}';cases.append(case);selected.add(key)
        remaining.difference_update((t['rule_id'],t['branch']) for t in case['expected'].get('trace',[]))
    for key,case in candidates.items():
        if remaining.intersection((t['rule_id'],t['branch']) for t in case['expected'].get('trace',[])):select(key)
    for key,case in candidates.items():
        if case['mandatory']:select(key)
    for key in candidates:select(key)
    obligation_gaps=[{'record_hash':key,'reason':case['reason'],'status':'budget_exhausted','explanation':'Required boundary or intentional layout-negative witness omitted by the configured case budget; unverified.'} for key,case in candidates.items() if case['mandatory'] and key not in selected]
    branches={r['id']:{'true':[],'false':[]} for r in program['rules']}
    for case in cases:
        for t in case['expected'].get('trace',[]):branches[t['rule_id']]['true' if t['branch'] else 'false'].append(case['id'])
    gaps=[{'rule_id':rid,'branch':branch,'status':'unknown_or_unprovable','reason':'No witness in bounded source-derived candidates; branch may be unreachable or require additional interactions. No verification credit.'} for rid,record in branches.items() for branch,witnesses in record.items() if not witnesses]
    coverage={'rule_count':len(branches),'branch_targets':len(branches)*2,'branches_observed':sum(bool(w) for b in branches.values() for w in b.values()),'rules':branches,'gaps':gaps,'obligation_gaps':obligation_gaps,'budget':budget,'mandatory_candidates':sum(c['mandatory'] for c in candidates.values()),'complete':not gaps and not obligation_gaps and not program['blockers'],'exhaustive':False,'claim':'Decision outcomes for the supported source IR; not all input/path/condition coverage or observed legacy parity.'}
    return {'version':1,'program':program['name'],'source_hash':program['source_hash'],'seed':seed,'evidence_basis':'SOURCE_DERIVED_EXPECTED','generator_version':'source-subset-1','cases':cases,'coverage':coverage,'contract_hash':sha(encode({'source':program.get('semantic_hash',program['source_hash']),'seed':seed,'rules':program['rules'],'fields':program['fields']}))}


def verify_program(program,code,suite,checkpoint=None):
    require(encode(suite)==encode(plan_cases(program,suite['seed'],suite['coverage']['budget'])), 'Frozen suite or coverage differs from the deterministic source-derived contract')
    return _verify_cases(program,code,suite,checkpoint)


def _verify_cases(program,code,suite,checkpoint=None):
    require(suite['source_hash']==program['source_hash'],'Fixture source version differs')
    actual=[];diffs=[]
    for case in suite['cases']:
        if checkpoint:checkpoint()
        require(encode(case['expected'])==encode(run_reference(program,case['record'])),'Frozen expected result differs from independent source interpretation')
        errors=input_errors(program,case['record'])
        got={'input_status':'REJECT_INPUT','errors':errors,'return_code':None} if errors else run_generated(code,case['record'])
        actual.append({'case_id':case['id'],'result':got})
        if encode(got)!=encode(case['expected']):diffs.append({'case_id':case['id'],'expected':case['expected'],'actual':got,'triage':'Target, oracle or adapter discrepancy; inspect source evidence before changing expectations.'})
    return {'status':'MISMATCH' if diffs else 'MATCHED_SOURCE_DERIVED_EXPECTATIONS' if suite['coverage']['complete'] else 'MATCHED_WITH_COVERAGE_GAPS','source_hash':program['source_hash'],'target_hash':sha(code),'contract_hash':suite['contract_hash'],'expected_count':len(suite['cases']),'matched_count':len(suite['cases'])-len(diffs),'differences':diffs,'actual':actual,'coverage':suite['coverage'],'observed_legacy_parity':False}


def adversarial_review(program, code, suite, checkpoint=None):
    """Mutate target syntax only, preserving the frozen independent source oracle.

    Every rule gets a decision reversal, each atomic relation a boundary mutation,
    and every literal assignment a different valid field value. A surviving
    mutation is an explicit gap (including effects overwritten downstream).
    """
    require(encode(suite)==encode(plan_cases(program,suite['seed'],suite['coverage']['budget'])), 'Adversarial suite differs from frozen source contract')
    tree=ast.parse(code);rules=[n for n in tree.body[0].body if isinstance(n,ast.If)]
    require(len(rules)==len(program['rules']),'Target rule structure differs')
    mutations=[]
    boundaries={ast.Eq:ast.NotEq,ast.NotEq:ast.Eq,ast.GtE:ast.Gt,ast.Gt:ast.GtE,ast.LtE:ast.Lt,ast.Lt:ast.LtE}
    def record(mutant,rid,kind,label):
        if checkpoint:checkpoint()
        result=_verify_cases(program,ast.unparse(mutant),suite,checkpoint)
        detected=bool(result['differences'])
        mutations.append({'rule_id':rid,'kind':kind,'mutation':label,'detected':detected,'witnesses':[d['case_id'] for d in result['differences']], 'reason':'Frozen source expectations detected changed target behavior' if detected else 'No differentiating output/trace witness; effect may be masked or unreachable. Unproved, no adversarial credit.'})
    for index,rule in enumerate(program['rules']):
        mutant=copy.deepcopy(tree);branch=[n for n in mutant.body[0].body if isinstance(n,ast.If)][index]
        # Swap the whole decision, including its trace, without changing oracle IR.
        branch.body,branch.orelse=branch.orelse,branch.body
        record(mutant,rule['id'],'predicate','reverse whole decision')
        relations=[n for n in ast.walk(rules[index].test) if isinstance(n,ast.Compare)]
        for offset,relation in enumerate(relations):
            mutant=copy.deepcopy(tree);branch=[n for n in mutant.body[0].body if isinstance(n,ast.If)][index]
            comparison=[n for n in ast.walk(branch.test) if isinstance(n,ast.Compare)][offset]
            comparison.ops[0]=boundaries[type(comparison.ops[0])]()
            record(mutant,rule['id'],'comparison',f'boundary relation {offset+1}')
        for arm in ('then','else'):
            for offset,effect in enumerate(rule[arm]):
                spec=program['fields'][effect['field']];old=effect['value']
                value=(old+1)%(spec['max']+1) if spec['type']=='integer' else ('Z' if old[:1]!='Z' else 'Y')+old[1:]
                mutant=copy.deepcopy(tree);branch=[n for n in mutant.body[0].body if isinstance(n,ast.If)][index]
                assignments=[n for n in (branch.body if arm=='then' else branch.orelse) if isinstance(n,ast.Assign)]
                require(offset<len(assignments),'Target effect structure differs')
                assignments[offset].value=ast.Constant(value=value)
                record(mutant,rule['id'],'effect',f'{arm} assignment {offset+1}: {effect["field"]}')
    denied=False
    if checkpoint:checkpoint()
    try:run_generated('import os\ndef run_program(record):\n    return record\n',{})
    except ValueError:denied=True
    gaps=[m for m in mutations if not m['detected']]
    accounted=all(x['disposition']!='unaccounted' for x in program['coverage'])
    return {'method':'deterministic per-rule, per-comparison and per-effect target mutations against frozen source expectations; not independent human/model review', 'mutations':mutations,'gaps':gaps,'mutation_detected':bool(mutations) and not gaps,'forbidden_import_rejected':denied,'source_accounted':accounted,'passed':not gaps and denied and accounted}
