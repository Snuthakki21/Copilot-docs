# Generated ordered orchestration. Program implementations are shared and version-pinned.
def run_job_refjob(context, programs):
    results = []
    previous_rc = 0
    if True:
        result = programs['ELIGIBLE'](context['record'])
        results.append({'step': 'CHECK', 'version': '53fcfed5bff8aa5e0c89d77b4e65d9638b7b0acd5a20db95913a1bccc21d0587'} | result)
        previous_rc = result['return_code']
        context['record'] = result['record']
    else:
        results.append({'step': 'CHECK', 'status': 'SKIPPED'})
    return results
def run_process(context, programs):
    results = {}
    results['REFJOB'] = run_job_refjob(context, programs)
    return results
