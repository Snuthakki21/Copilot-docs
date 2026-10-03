"""Independent source-IR reference evaluation, never generated target outputs."""


def input_errors(program, record):
    errors=[]
    if not isinstance(record,dict):return ['record must be an object']
    if set(record)!=set(program['fields']):errors.append('field set differs from source layout')
    for name,f in program['fields'].items():
        value=record.get(name)
        if f['type']=='integer':
            if type(value) is not int or not 0<=value<=f['max']:errors.append(name+': invalid unsigned integer')
        elif type(value) is not str or len(value)!=f['width']:errors.append(name+': invalid fixed-width string')
    return errors


def predicate(node, record):
    if not isinstance(node,dict):return node
    if 'field' in node:return record[node['field']]
    a=predicate(node['left'],record);b=predicate(node['right'],record);op=node['op']
    if op=='AND':return bool(a) and bool(b)
    if op=='OR':return bool(a) or bool(b)
    if op=='=':return type(a) is type(b) and a==b
    if op=='<>':return type(a) is not type(b) or a!=b
    if type(a) is not type(b):raise ValueError('Source operands have differing types')
    if op=='>=':return a>=b
    if op=='<=':return a<=b
    if op=='>':return a>b
    if op=='<':return a<b
    raise ValueError('Unsupported source predicate')


def run_reference(program, record):
    errors=input_errors(program,record)
    if errors:return {'input_status':'REJECT_INPUT','errors':errors,'return_code':None}
    state=record.copy();trace=[]
    for rule in program['rules']:
        branch=predicate(rule['predicate'],state)
        for effect in rule['then'] if branch else rule['else']:state[effect['field']]=effect['value']
        trace.append({'rule_id':rule['id'],'branch':branch,'source_refs':rule['source_refs']})
    return {'input_status':'ACCEPT_INPUT','record':state,'trace':trace,'return_code':0}
