"""Generate auditable Python from a constrained source IR, not arbitrary LLM code."""
import ast
from .domain import require, sha


def expression(node):
    if not isinstance(node,dict):return repr(node)
    if 'field' in node:return 'row['+repr(node['field'])+']'
    op={'=':'==','<>':'!=','AND':'and','OR':'or'}.get(node['op'],node['op'])
    return '('+expression(node['left'])+' '+op+' '+expression(node['right'])+')'


def emit_program(program):
    require(not program['blockers'], 'Unsupported program cannot receive a complete executable translation')
    lines=['# Generated from source SHA256 '+program['source_hash'], '# Evidence class: SOURCE_DERIVED_EXPECTED', 'def run_program(record):','    row = dict(record)','    trace = []']
    for rule in program['rules']:
        lines.append('    if '+expression(rule['predicate'])+':')
        for effect in rule['then']:lines.append('        row['+repr(effect['field'])+'] = '+repr(effect['value']))
        lines.append('        trace.append('+repr({'rule_id':rule['id'],'branch':True,'source_refs':rule['source_refs']})+')')
        lines.append('    else:')
        for effect in rule['else']:lines.append('        row['+repr(effect['field'])+'] = '+repr(effect['value']))
        lines.append('        trace.append('+repr({'rule_id':rule['id'],'branch':False,'source_refs':rule['source_refs']})+')')
    lines.append("    return {'input_status': 'ACCEPT_INPUT', 'record': row, 'trace': trace, 'return_code': 0}")
    return '\n'.join(lines)+'\n'


def check_generated(code):
    require(isinstance(code,str) and len(code)<=512000,'Target code exceeds limit')
    try:tree=ast.parse(code)
    except SyntaxError as exc:raise ValueError('Invalid target syntax') from exc
    require(len(tree.body)==1 and isinstance(tree.body[0],ast.FunctionDef) and tree.body[0].name=='run_program','Only one generated program function is accepted')
    allowed=(ast.Module,ast.FunctionDef,ast.arguments,ast.arg,ast.Assign,ast.Name,ast.Load,ast.Store,ast.Call,ast.Dict,ast.Constant,ast.List,ast.If,ast.Compare,ast.BoolOp,ast.And,ast.Or,ast.Eq,ast.NotEq,ast.Gt,ast.GtE,ast.Lt,ast.LtE,ast.Subscript,ast.Expr,ast.Attribute,ast.Return,ast.UnaryOp,ast.USub)
    for node in ast.walk(tree):
        require(isinstance(node,allowed),'Target includes an unsupported executable capability')
        if isinstance(node,ast.Name):require(node.id in {'run_program','record','row','trace','dict'},'Unknown target identifier')
        if isinstance(node,ast.Attribute):require(isinstance(node.value,ast.Name) and node.value.id=='trace' and node.attr=='append','Target attribute access is not allowed')
        if isinstance(node,ast.Call):require((isinstance(node.func,ast.Name) and node.func.id=='dict') or (isinstance(node.func,ast.Attribute) and node.func.attr=='append'),'Target call is not allowed')
        if isinstance(node,ast.Assign):require(all((isinstance(t,ast.Name) and t.id in {'row','trace'}) or (isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='row' and isinstance(t.slice,ast.Constant) and isinstance(t.slice.value,str)) for t in node.targets),'Unsafe assignment target')
    return tree


def run_generated(code, record):
    # This is a restricted generator/template boundary, not an OS sandbox for user-supplied Python.
    tree=check_generated(code)
    namespace={'__builtins__':{},'dict':dict}
    exec(compile(tree,'<source-generated-target>','exec'),namespace)
    return namespace['run_program'](record)


def emit_jobs(manifest, program_versions):
    lines=['# Generated ordered orchestration. Program implementations are shared and version-pinned.']
    for job in manifest['jobs']:
        name=job['name'].lower().replace('-','_')
        lines += ['def run_job_'+name+'(context, programs):','    results = []','    previous_rc = 0']
        for step in job['steps']:
            condition=step['condition'].upper().replace(' ','')
            cond='True' if condition in ('ALWAYS','') else condition.replace('RC','previous_rc').replace('=','==') if condition.startswith('RC=') else condition.replace('RC','previous_rc')
            lines+=['    if '+cond+':',"        result = programs["+repr(step['program'].upper())+"](context['record'])",'        results.append('+repr({'step':step['name'],'version':program_versions[step['program'].upper()]})+" | result)",'        previous_rc = result[\'return_code\']',"        context['record'] = result['record']",'    else:',"        results.append({'step': "+repr(step['name'])+", 'status': 'SKIPPED'})"]
        lines.append('    return results')
    lines+=['def run_process(context, programs):','    results = {}']
    for job in manifest['jobs']:lines.append("    results["+repr(job['name'])+"] = run_job_"+job['name'].lower().replace('-','_')+'(context, programs)')
    lines.append('    return results')
    return '\n'.join(lines)+'\n'
