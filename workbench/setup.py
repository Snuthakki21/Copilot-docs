"""Deterministic operator preparation; no source, credential or network access."""
import os
from pathlib import Path
import re
import shutil
import threading

from .domain import ValidationError, atomic_json, decode, require, safe_path

MAX_SETUP_BYTES = 4096
_LOCK = threading.RLock()
_QUESTIONS = (
    ('source', 'Source export', 'How will you supply the complete read-only source export?',
     (('local_endeavor', 'Local Endeavor folder'), ('upload', 'Upload source files'), ('needs_setup', 'Help preparing the export'))),
    ('manifest', 'Process intake', 'Is the process manifest ready with ordered jobs and steps?',
     (('ready', 'Manifest ready'), ('needs_setup', 'Prepare the manifest'))),
    ('zowe', 'Read-only Zowe', 'Do you need read-only Zowe discovery for this process?',
     (('not_needed', 'Not needed'), ('configured', 'Configured locally'), ('needs_setup', 'Help configuring Zowe'))),
    ('db2', 'Read-only Db2', 'Do you need read-only Db2 catalog discovery for this process?',
     (('not_needed', 'Not needed'), ('configured', 'Configured locally'), ('needs_setup', 'Help configuring Db2'))),
    ('llm', 'Optional model suggestions', 'Use deterministic analysis, or explicitly opt in to approved source excerpts?',
     (('disabled', 'Deterministic analysis'), ('opt_in', 'Optional approved LLM suggestions'))),
    ('reviewer', 'Human reviewer', 'Is a real human reviewer available for the single SME workbook?',
     (('available', 'Reviewer available'), ('needs_setup', 'Arrange a reviewer'))),
)
_VALUES = {key: {value for value, _ in choices} for key, _, _, choices in _QUESTIONS}


def deterministic_metrics():
    return {'mode':'deterministic', 'llm_requests':0, 'input_tokens':0,
            'output_tokens':0, 'network_requests':0}


def _validate_answers(answers, *, partial):
    require(isinstance(answers, dict) and (bool(answers) if partial else set(answers) == set(_VALUES)),
            'Setup answers must contain the supported questions')
    require(set(answers) <= set(_VALUES), 'Unknown setup question; credentials and free text are not accepted')
    for key, value in answers.items():
        require(value is None or isinstance(value, str) and value in _VALUES[key],
                'Choose a listed setup option or null to reset it')
    return dict(answers)


def _state_path(workspace):
    root = Path(workspace).absolute()
    require(root.is_dir(), 'Setup requires an existing workspace directory')
    return safe_path(root, '.migration/setup.json')


def _load(path):
    if not path.exists(): return dict.fromkeys(_VALUES)
    require(path.is_file() and path.stat().st_size <= MAX_SETUP_BYTES,
            'Setup state must be a regular JSON file of at most 4096 bytes')
    with path.open('rb') as handle: data = handle.read(MAX_SETUP_BYTES + 1)
    document = decode(data, MAX_SETUP_BYTES)
    require(isinstance(document, dict) and set(document) == {'version', 'answers'}
            and type(document['version']) is int and document['version'] == 1,
            'Unsupported setup state document; preserve it and correct the local setup state')
    return _validate_answers(document['answers'], partial=False)


def _configuration(root, env):
    from .connectors import endpoint, ZoweReader
    from .provider import StructuredProvider
    try: source = safe_path(root, 'Endeavor').is_dir()
    except ValidationError: source = False
    zowe = db2 = llm = False
    if env.get('WB_ZOWE_PROFILE'):
        try:
            ZoweReader(env['WB_ZOWE_PROFILE'])
            hint = env.get('WB_DATASET_HINT', '*')
            require(isinstance(hint, str) and re.fullmatch(r'[A-Za-z0-9@$#.*()_-]{1,150}', hint)
                    and not hint.startswith('-'), 'Invalid dataset hint')
            zowe = bool(shutil.which('zowe', path=env.get('PATH', os.defpath)))
        except (ValidationError, OSError): pass
    if env.get('WB_DB2_MCP_URL'):
        try: endpoint(env['WB_DB2_MCP_URL']); db2 = True
        except ValidationError: pass
    if env.get('WB_LLM_URL'):
        try:
            # Validate public configuration syntax without reading the private token.
            StructuredProvider(env['WB_LLM_URL'], env.get('WB_LLM_MODEL'), '')
            require(env.get('WB_ALLOW_SOURCE_EGRESS', 'false') in ('true', 'false'), 'Invalid egress value')
            llm = True
        except ValidationError: pass
    return {'local_source_export':source, 'zowe_configured':zowe, 'db2_configured':db2,
            'llm_configured':llm, 'source_egress_approved':env.get('WB_ALLOW_SOURCE_EGRESS') == 'true'}


def _view(root, answers, env):
    config = _configuration(root, env)
    actions = {
        'source':'Choose a complete local Endeavor export or upload the complete UTF-8 text source set during intake. Preserve the original source; never execute it.',
        'manifest':'Download the intake template, supply the real process ID and ordered jobs/steps, then mark the manifest ready. Setup does not invent process facts.',
        'zowe':'If needed, install the approved Zowe CLI, authenticate an existing read-only profile locally, and set WB_ZOWE_PROFILE before launch. Keep credentials outside this questionnaire.',
        'db2':'If needed, configure the read-only Db2 MCP gateway and set WB_DB2_MCP_URL with private authentication in the launch environment. Setup never submits SQL or validates live access.',
        'llm':'Choose deterministic analysis unless optional suggestions are needed. For authorized excerpts, configure WB_LLM_URL and WB_LLM_MODEL and explicitly set WB_ALLOW_SOURCE_EGRESS=true in the launch environment, then restart. Never paste tokens here.',
        'reviewer':'Arrange a real human reviewer for the one SME workbook. Availability is preparation only; the actual returned workbook and reviewer attribution remain required.',
    }
    complete = {
        'source':answers['source'] == 'upload' or answers['source'] == 'local_endeavor' and config['local_source_export'],
        'manifest':answers['manifest'] == 'ready',
        'zowe':answers['zowe'] == 'not_needed' and not env.get('WB_ZOWE_PROFILE') or answers['zowe'] == 'configured' and config['zowe_configured'],
        'db2':answers['db2'] == 'not_needed' and not env.get('WB_DB2_MCP_URL') or answers['db2'] == 'configured' and config['db2_configured'],
        'llm':answers['llm'] == 'disabled' and not env.get('WB_LLM_URL') or answers['llm'] == 'opt_in' and config['llm_configured'] and config['source_egress_approved'],
        'reviewer':answers['reviewer'] == 'available',
    }
    if answers['llm'] == 'disabled' and env.get('WB_LLM_URL'):
        actions['llm'] = 'Remove WB_LLM_URL from the launch environment and restart for deterministic analysis. Saving this answer does not change the running provider configuration or authorize source transfer.'
    for key, variable in (('zowe', 'WB_ZOWE_PROFILE'), ('db2', 'WB_DB2_MCP_URL')):
        if answers[key] == 'not_needed' and env.get(variable):
            actions[key] = 'Remove ' + variable + ' from the launch environment and restart to omit this optional read-only discovery. Saving this answer does not change runtime configuration.'
    questions = [{'id':key, 'title':title, 'prompt':prompt,
                  'options':[{'value':value, 'label':label} for value, label in choices],
                  'answer':answers[key], 'status':'ANSWERED' if complete[key] else 'UNANSWERED' if answers[key] is None else 'NEEDS_ACTION',
                  'action':actions[key]} for key, title, prompt, choices in _QUESTIONS]
    pending = [q for q in questions if q['status'] != 'ANSWERED']
    return {'version':1, 'answers':dict(answers), 'questions':questions,
            'actions':[{key:q[key] for key in ('id', 'title', 'action')} for q in pending],
            'next_step':pending[0]['id'] if pending else None,
            'readiness':{'status':'NEEDS_SETUP' if pending else 'READY_FOR_INTAKE',
                         'answered':sum(value is not None for value in answers.values()), 'total':len(_QUESTIONS),
                         'remaining':[q['id'] for q in pending], 'connectivity_verified':False,
                         'source_verified':False, 'conversion_verified':False},
            'configuration':config, 'metrics':deterministic_metrics(),
            'scope':'Operator preparation only. Source validation, live connectivity, actual human review and conversion verification remain separate gates. This questionnaire performs no network or LLM calls.'}


def inspect_setup(workspace, *, environ=None):
    """Read bounded nonsecret preferences and local configuration; never contact a service."""
    with _LOCK:
        path = _state_path(workspace)
        return _view(path.parent.parent, _load(path), dict(os.environ if environ is None else environ))


def save_setup(workspace, answers, *, environ=None):
    """Atomically merge a bounded enum patch, preserving all workflow and source evidence."""
    update = _validate_answers(answers, partial=True)
    with _LOCK:
        path = _state_path(workspace)
        current = _load(path)
        current.update(update)
        result = _view(path.parent.parent, current, dict(os.environ if environ is None else environ))
        atomic_json(path, {'version':1, 'answers':current})
        return result
