"""Source-order analysis for a deliberately bounded COBOL/JCL/BMS POC subset.

Supported executable COBOL: flat IF/ELSE with typed comparisons joined by
AND/OR, literal MOVE, CONTINUE and terminal GOBACK/STOP RUN. Every other
executable construct is an explicit blocker. No inference from target code.
"""
import re
from .domain import sha, require, ValidationError, encode

NAME = r'[A-Z][A-Z0-9-]*'
TOKEN = re.compile(r'"(?:[^"]|"")*"|\'(?:[^\']|\'\')*\'|>=|<=|<>|=|>|<|-?\d+|[A-Z][A-Z0-9-]*', re.I)


def literal(token):
    if re.fullmatch(r'"(?:[^"\n]|"")*"|\'(?:[^\'\n]|\'\')*\'', token): return token[1:-1].replace(token[0]*2, token[0])
    if re.fullmatch(r'-?\d+', token): return int(token)
    if token.upper() in ('SPACE','SPACES'): return ' '
    if token.upper() in ('ZERO','ZEROS','ZEROES'): return 0
    raise ValidationError('Only explicit numeric/string literal values are supported')


def condition(text, fields):
    stripped = text.strip().rstrip('.')
    tokens = TOKEN.findall(stripped)
    require(''.join(tokens).replace(' ', '').upper() == re.sub(r'\s+', '', stripped).upper(), 'Unsupported condition syntax')
    pos = 0
    def operand():
        nonlocal pos
        require(pos < len(tokens), 'Missing condition operand')
        token = tokens[pos];pos += 1
        if token.upper() in fields: return {'field':token.upper()}
        return literal(token)
    def comparison():
        nonlocal pos
        left=operand()
        require(pos < len(tokens) and tokens[pos] in ('=','<>','>','<','>=','<='), 'Unsupported comparison')
        op=tokens[pos];pos+=1;right=operand()
        if not isinstance(left,dict) and not isinstance(right,dict):
            require(type(left) is type(right), 'Condition operand types differ')
            if isinstance(left,str):
                require(op in ('=','<>'), 'String ordering needs the verified source collation')
                width=max(len(left),len(right));left=left.ljust(width);right=right.ljust(width)
        if isinstance(left,dict) and isinstance(right,dict):
            a,b=fields[left['field']],fields[right['field']]
            require(a['type']==b['type'] and (a['type']!='string' or a['width']==b['width']), 'Differing operand layouts need an exact comparison adapter')
            require(a['type']!='string' or op in ('=','<>'),'String ordering needs the verified source collation')
        for operand_value,other,other_side in [(left,right,'right'),(right,left,'left')]:
            if isinstance(operand_value,dict) and not isinstance(other,dict):
                spec=fields[operand_value['field']]
                require(type(other) is (int if spec['type']=='integer' else str),'Condition operand types differ')
                if spec['type']=='string':
                    require(op in ('=','<>'),'String ordering needs the verified source collation')
                    require(len(other)<=spec['width'],'Over-width literal comparison needs an adapter')
                    if other_side=='right':right=other.ljust(spec['width'])
                    else:left=other.ljust(spec['width'])
        return {'op':op,'left':left,'right':right}
    def conjunction():
        nonlocal pos
        result=comparison()
        while pos<len(tokens) and tokens[pos].upper()=='AND':
            pos+=1;result={'op':'AND','left':result,'right':comparison()}
        return result
    result=conjunction()
    while pos<len(tokens) and tokens[pos].upper()=='OR':
        pos+=1;result={'op':'OR','left':result,'right':conjunction()}
    require(pos==len(tokens), 'Unsupported condition suffix')
    return result


def assignments(lines, fields):
    effects=[]
    for line in lines:
        line=line.strip().rstrip('.')
        if not line or line.upper()=='CONTINUE':continue
        m=re.fullmatch(r'MOVE\s+(.+?)\s+TO\s+('+NAME+r')',line,re.I)
        require(m is not None, f'Unsupported effect: {line[:80]}')
        name=m.group(2).upper();require(name in fields,'Unknown MOVE destination')
        value=literal(m.group(1).strip())
        spec=fields[name]
        require(type(value) is (int if spec['type']=='integer' else str), 'MOVE literal and field type differ')
        require(spec['type']!='integer' or 0<=value<=spec['max'], 'Numeric MOVE outside PICTURE range')
        require(spec['type']!='string' or len(value)<=spec['width'], 'String MOVE exceeds PICTURE width')
        effects.append({'field':name,'value':value.ljust(spec['width']) if spec['type']=='string' else value})
    return effects


def without_comment(line):
    # COBOL inline comment markers have no effect within quoted literals.
    quote=None;i=0
    while i<len(line):
        c=line[i]
        if quote:
            if c==quote:
                if i+1<len(line) and line[i+1]==quote:i+=2;continue
                quote=None
        elif c in ('"', "'"):quote=c
        elif line[i:i+2]=='*>':return line[:i]
        i+=1
    return line


def normalized_lines(text):
    result=[]
    for raw in text.splitlines():
        line=raw
        # Blank indentation is not evidence of fixed format. Never silently discard nonblank content.
        if len(line)>6 and re.fullmatch('[ 0-9]{6}',line[:6]) and (line[:6].isdigit() or line[6] in '*/-') and line[6] in ' */-':
            if line[6] in '*/': result.append(('comment',''));continue
            if line[6]=='-':result.append(('unsupported',line));continue
            if line[72:].strip():result.append(('unsupported',line));continue
            line=line[7:72]
        if line.lstrip().startswith('*>'):result.append(('comment',''));continue
        line=without_comment(line).strip()
        result.append(('blank' if not line else 'code',line))
    return result


def analyze_program(path, text, files):
    source_hash=sha(text)
    program_matches=[re.fullmatch(r'PROGRAM-ID\.\s*('+NAME+r')\.', line,re.I) for kind,line in normalized_lines(text) if kind=='code']
    program_matches=[m for m in program_matches if m]
    program_match=program_matches[0] if program_matches else None
    name=program_match.group(1).upper() if program_match else path.rsplit('/',1)[-1].split('.')[0].upper()
    p={'name':name,'path':path,'source_hash':source_hash,'id':sha('program:'+name+':'+source_hash),'kind':'cobol_program','fields':{},'rules':[], 'copybooks':[], 'dependencies':[], 'blockers':[], 'coverage':[], 'source_text':text, 'relationships':[]}
    lines=normalized_lines(text)
    for i,(kind,line) in enumerate(lines,1):p['coverage'].append({'line':i,'disposition':kind if kind in ('blank','comment') else 'unaccounted','source':line,'original':text.splitlines()[i-1]})
    procedure=False
    proc=[]
    group='INPUT';groups=set();division_order=[];section=None
    def block(msg, indices):
        p['blockers'].append({'kind':'unsupported_source','message':msg,'path':path,'lines':indices})
        for n in indices:p['coverage'][n-1]['disposition']='unsupported'
    def field_line(line, origin):
        nonlocal group
        gm=re.fullmatch(r'01\s+('+NAME+r')\.',line,re.I)
        if gm:
            group=gm.group(1).upper();require(group not in groups,'Duplicate record group names need qualification support');groups.add(group);return True
        fm=re.fullmatch(r'(?:05|77)\s+('+NAME+r')\s+PIC(?:TURE)?\s+(X|9)(?:\((\d+)\))?(?:\s+VALUE\s+(.+?))?\.',line,re.I)
        if not fm:return False
        key,typ,width,value=fm.groups();key=key.upper();typ=typ.upper();width=int(width or 1)
        require(1<=width<=18 if typ=='9' else 1<=width<=256,'PICTURE width outside supported limit')
        require(key not in p['fields'], 'Duplicate field names need qualification support')
        spec={'type':'integer' if typ=='9' else 'string','width':width,'group':group,'source_ref':origin,'storage_section':section,'default':0 if typ=='9' else ' '*width}
        if typ=='9':spec.update({'min':0,'max':10**width-1})
        if value:
            v=literal(value);require(type(v) is (int if typ=='9' else str),'VALUE type mismatch')
            require(0<=v<=10**width-1 if typ=='9' else len(v)<=width,'VALUE exceeds PICTURE bounds')
            spec['default']=v if typ=='9' else v.ljust(width)
        p['fields'][key]=spec;return True
    if len(program_matches)!=1:block('Exactly one unambiguous PROGRAM-ID is required',[])
    try:
        for i,(kind,line) in enumerate(lines,1):
            if kind in ('comment','blank'):continue
            if kind=='unsupported':block('Fixed-format continuation or nonblank content beyond column 72 is unsupported',[i]);continue
            upper=line.upper()
            if upper.startswith('PROCEDURE DIVISION'):
                pm=re.fullmatch(r'PROCEDURE DIVISION(?: USING ('+NAME+r'(?:\s+'+NAME+r')*))?\.',upper)
                if procedure or not pm:block('Unsupported or repeated PROCEDURE DIVISION',[i]);continue
                if 0 not in division_order or 2 not in division_order:block('IDENTIFICATION and DATA DIVISION are required before PROCEDURE',[i])
                if not pm[1] or set(pm[1].split())!=groups or len(pm[1].split())!=len(groups):block('PROCEDURE USING must map each declared record group exactly once',[i])
                elif p['coverage'][i-1]['disposition']!='unsupported':p['coverage'][i-1]['disposition']='structure'
                procedure=True;continue
            if procedure:proc.append((i,line));continue
            if upper in ('LINKAGE SECTION.','WORKING-STORAGE SECTION.','FILE SECTION.'):
                section=upper.split()[0]
                if section!='LINKAGE':block('Storage lifetime or file binding needs an adapter; only caller-owned LINKAGE records are supported',[i])
                elif not division_order or division_order[-1]!=2:block('Record SECTION requires DATA DIVISION',[i])
                else:p['coverage'][i-1]['disposition']='structure'
                continue
            cm=re.fullmatch(r'COPY\s+('+NAME+r')\.',line,re.I)
            if cm:
                if section!='LINKAGE':block('COPY layout must belong to the supported LINKAGE record section',[i])
                book=cm.group(1).upper();p['copybooks'].append(book)
                matches=[(fp,ft) for fp,ft in files.items() if fp.lower().endswith(('.cpy','.copy')) and fp.rsplit('/',1)[-1].rsplit('.',1)[0].upper()==book]
                if len(matches)!=1:
                    p['dependencies'].extend({'name':book,'path':fp,'source_hash':sha(ft),'resolution':'ambiguous'} for fp,ft in matches)
                    block('Copybook missing or ambiguous: '+book,[i]);continue
                p['dependencies'].append({'name':book,'path':matches[0][0],'source_hash':sha(matches[0][1])})
                before=len(p['blockers'])
                for ci,(ck,cl) in enumerate(normalized_lines(matches[0][1]),1):
                    if ck in ('comment','blank'):continue
                    if not field_line(cl,f'{matches[0][0]}:{ci}'):block('Unsupported copybook layout: '+book,[i])
                if len(p['blockers'])==before and p['coverage'][i-1]['disposition']!='unsupported':p['coverage'][i-1]['disposition']='copybook'
                continue
            if field_line(line,f'{path}:{i}'):
                if section!='LINKAGE':block('Data field must belong to the supported LINKAGE record section',[i])
                else:p['coverage'][i-1]['disposition']='data_layout'
                continue
            if re.fullmatch(r'(IDENTIFICATION|ENVIRONMENT|DATA) DIVISION\.|(LINKAGE|WORKING-STORAGE|FILE) SECTION\.|PROGRAM-ID\.\s*'+NAME+r'\.',upper):
                if upper.endswith(' DIVISION.'):
                    rank={'IDENTIFICATION DIVISION.':0,'ENVIRONMENT DIVISION.':1,'DATA DIVISION.':2}[upper]
                    if division_order and rank<=division_order[-1]:block('Repeated or out-of-order DIVISION',[i]);continue
                    division_order.append(rank)
                p['coverage'][i-1]['disposition']='structure';continue
            block('Unsupported declaration: '+line[:100],[i])
    except ValidationError as exc: block(str(exc),[i])
    if not procedure:block('Missing PROCEDURE DIVISION',[])
    if not p['fields']:block('No supported source field layout',[])
    cursor=0;terminated=False
    while cursor<len(proc):
        i,line=proc[cursor];upper=line.upper().rstrip('.')
        if terminated:block('Executable source after terminal statement',[i]);cursor+=1;continue
        if upper in ('GOBACK','STOP RUN'):
            p['coverage'][i-1]['disposition']='terminal';terminated=True;cursor+=1;continue
        if re.fullmatch(NAME+r'\.',line):p['coverage'][i-1]['disposition']='paragraph';cursor+=1;continue
        if not upper.startswith('IF '):block('Unsupported executable statement: '+line[:100],[i]);cursor+=1;continue
        start=cursor;depth=1;cursor+=1;else_at=None;nested=False
        while cursor<len(proc) and depth:
            u=proc[cursor][1].upper().rstrip('.')
            if u.startswith('IF '):depth+=1;nested=True
            if u=='END-IF':depth-=1
            if u=='ELSE' and depth==1:else_at=cursor
            if depth:cursor+=1
        indices=[x[0] for x in proc[start:min(cursor+1,len(proc))]]
        if depth or nested:block('Unclosed or nested IF requires a parser extension',indices);cursor+=1;continue
        try:
            require(not any(x[1].rstrip().endswith('.') for x in proc[start:cursor]), 'Sentence period inside IF changes implicit scope; unsupported')
            require(sum(x[1].upper().rstrip('.')=='ELSE' for x in proc[start:cursor])<=1,'Repeated ELSE is unsupported')
            pred=condition(line[3:],p['fields'])
            then=assignments([x[1] for x in proc[start+1:else_at if else_at is not None else cursor]],p['fields'])
            otherwise=assignments([x[1] for x in proc[else_at+1:cursor]],p['fields']) if else_at is not None else []
            rid=f'{name}_R{len(p["rules"])+1:03d}'
            rule={'id':rid,'predicate':pred,'then':then,'else':otherwise,'source_refs':[f'{path}:{i}-{proc[cursor][0]}'],'source_start':i,'source_end':proc[cursor][0], 'plain':f'If {line[3:].strip()}, '+(' and '.join(f"set {a['field']} to {a['value']!r}" for a in then) or 'keep the current values')+'. Otherwise '+(' and '.join(f"set {a['field']} to {a['value']!r}" for a in otherwise) or 'keep the current values')+'.'}
            p['rules'].append(rule)
            for n in indices:p['coverage'][n-1].update({'disposition':'modeled','rule_id':rid})
            if pred['op']=='=' and isinstance(pred['left'],dict) and isinstance(pred['right'],dict):p['relationships'].append({'left':pred['left']['field'],'right':pred['right']['field'],'kind':'conditional_match','source_refs':rule['source_refs']})
        except ValidationError as exc:block(str(exc),indices)
        cursor+=1
    if not terminated:block('No supported terminal statement',[])
    for entry in p['coverage']:
        if entry['disposition']=='unaccounted':block('Unaccounted source line',[entry['line']])
    p['loc']={'physical':len(lines),'blank':sum(k=='blank' for k,_ in lines),'comment':sum(k=='comment' for k,_ in lines),'code':sum(k not in ('blank','comment') for k,_ in lines)}
    p['dependency_hash']=sha(encode(p['dependencies']))
    p['semantic_hash']=sha(encode({'source_hash':p['source_hash'],'dependencies':p['dependencies']}))
    return p


def analyze_sources(files, manifest):
    require(isinstance(files,dict) and len(files)<=200,'Source export exceeds file-count bound')
    programs={};assets=[];blockers=[]
    for path,text in sorted(files.items()):
        require(isinstance(text,str) and len(text)<=512000,'Source file too large')
        lower=path.lower();stem=path.rsplit('/',1)[-1].rsplit('.',1)[0].upper();h=sha(text)
        if lower.endswith(('.cbl','.cob','.cobol')):
            p=analyze_program(path,text,files)
            require(p['name'] not in programs,'Duplicate program ID needs disambiguation')
            programs[p['name']]=p;assets.append(dict(p))
        else:
            kind='copybook' if lower.endswith(('.cpy','.copy')) else 'jcl_job' if lower.endswith('.jcl') else 'bms_map' if lower.endswith('.bms') else 'sql' if lower.endswith('.sql') else 'other_source'
            asset={'id':sha(kind+':'+stem+':'+h),'kind':kind,'name':stem,'path':path,'source_hash':h,'source_text':text,'loc':{'physical':len(text.splitlines()),'code':sum(bool(x.strip()) and not x.lstrip().startswith(('*>','--','//*')) for x in text.splitlines())}}
            if kind=='sql':asset['tables']=sorted(set(re.findall(r'\b(?:FROM|JOIN|INTO|UPDATE|CREATE\s+TABLE)\s+([A-Z][A-Z0-9_.]*)',text,re.I)))
            if kind=='bms_map':
                asset['screens']=re.findall(r'^(\w+)\s+DFHMDI\b',text,re.M|re.I)
                blockers.append({'kind':'unsupported_source','message':'BMS/CICS behavior requires source-supported action mapping; no replacement screen is credited.','path':path})
            assets.append(asset)
    graph=[]
    used=set()
    for job in manifest['jobs']:
        for step in job['steps']:
            name=step['program'].upper();used.add(name)
            graph.append({'from':job['name']+'.'+step['name'],'to':name,'kind':'calls','inputs':step['inputs'],'outputs':step['outputs']})
            if name not in programs:blockers.append({'kind':'missing_source','message':'Program/utility source or supported adapter missing: '+name})
            if step['condition'].upper() not in ('ALWAYS','') and not re.fullmatch(r'RC\s*(?:<=|>=|=|<|>)\s*\d{1,5}',step['condition'],re.I):blockers.append({'kind':'unresolved_condition','message':'Unknown step condition: '+step['condition']})
    for p in programs.values():
        for book in p['copybooks']:graph.append({'from':p['name'],'to':book,'kind':'copybook'})
    # Validate the entire supported card grammar and reconcile source step order.
    jcl_job_origins={}
    for path,text in files.items():
        if not path.lower().endswith('.jcl'):continue
        current=None;source_jobs={}
        for raw in text.splitlines():
            if not raw.strip() or raw.startswith('//*'):continue
            card=raw.rstrip()
            job=re.fullmatch(r"//([A-Z][A-Z0-9]{0,7})\s+JOB(?:\s+\([^)]*\)(?:,'[^']*')?)?",card,re.I)
            execute=re.fullmatch(r'//([A-Z][A-Z0-9]{0,7})\s+EXEC\s+PGM=('+NAME+r')',card,re.I)
            dd=re.fullmatch(r'//([A-Z][A-Z0-9]{0,7})\s+DD\s+DSN=[A-Z0-9@$#.-]+(?:,DISP=SHR)?',card,re.I)
            if job:
                current=job[1].upper()
                if current in jcl_job_origins:blockers.append({'kind':'unsupported_jcl','path':path,'message':'Repeated JCL JOB declaration requires explicit identity/scope resolution: '+current})
                jcl_job_origins[current]=path;source_jobs.setdefault(current,[])
            elif execute and current:source_jobs[current].append((execute[1].upper(),execute[2].upper()))
            elif dd and current and source_jobs[current]:blockers.append({'kind':'unsupported_jcl','path':path,'message':'DD dataset allocation/read/write semantics need an explicit I/O adapter: '+card[:100]})
            else:blockers.append({'kind':'unsupported_jcl','path':path,'message':'Unsupported complete JCL card or trailing clause: '+card[:100]})
        manifest_jobs={j['name'].upper():j for j in manifest['jobs']}
        for name,steps in source_jobs.items():
            job=manifest_jobs.get(name)
            expected=[(s['name'].upper(),s['program'].upper()) for s in job['steps']] if job else None
            if steps!=expected:blockers.append({'kind':'scope_mismatch','path':path,'message':'JCL job/step/program order differs from manifest: '+name})
            if job and any(s['condition'].upper() not in ('ALWAYS','') for s in job['steps']):blockers.append({'kind':'scope_mismatch','path':path,'message':'Manifest conditional steps are not evidenced by the supported unconditional JCL grammar: '+name})
    # Unreferenced programs are discovered but do not inflate the selected conversion scope.
    scoped={n:p for n,p in programs.items() if n in used}
    selected_paths={p['path'] for p in scoped.values()} | {d['path'] for p in scoped.values() for d in p['dependencies']}
    for p in scoped.values():blockers+=p['blockers']
    for asset in assets:
        asset['selected']=asset['path'] in selected_paths or asset['kind'] in ('jcl_job','bms_map','sql','other_source')
        asset['scope_disposition']='selected' if asset['selected'] else 'out_of_scope'
        asset['scope_reason']='Selected manifest program, resolved dependency, or additional process export requiring accountability' if asset['selected'] else 'Not called by the selected manifest and not a resolved COPY dependency'
    scoped_assets=assets
    return {'programs':scoped,'assets':scoped_assets,'rules':[r for p in scoped.values() for r in p['rules']], 'graph':graph,'blockers':blockers,'source_snapshot':sha('\n'.join(k+':'+sha(v) for k,v in sorted(files.items()))),'source_accounting':{p['name']:p['coverage'] for p in scoped.values()}, 'relationships':[r for p in scoped.values() for r in p['relationships']], 'evidence_basis':'SOURCE_DERIVED_EXPECTED'}
