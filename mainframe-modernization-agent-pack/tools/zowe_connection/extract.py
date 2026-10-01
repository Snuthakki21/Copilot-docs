"""Fixed, scoped Zowe text-source reads. Raw CLI JSON stays local, not in chat."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time
import uuid
from connection import read_configuration, build_command, ConfigurationError

QUAL=r'[A-Z@$#][A-Z0-9@$#-]{0,7}'
MEMBER=r'[A-Z@$#][A-Z0-9@$#]{0,7}'
DATASET=re.compile(rf'({QUAL}(?:\.{QUAL})*)(?:\(({MEMBER})\))?\Z')
MAX_BYTES=1048576

def allowed_dataset(value,prefixes):
    if not isinstance(value,str):return False
    m=DATASET.fullmatch(value)
    return bool(m and len(m[1])<=44 and any(m[1]==p or m[1].startswith(p+'.') for p in prefixes))

def read_arguments(operation,value,prefixes):
    if operation=='datasets':
        base=value[:-2] if isinstance(value,str) and value.endswith('.*') else value
        if not allowed_dataset(base,prefixes) or '(' in base:raise ValueError('dataset_scope')
        return ['zos-files','list','data-set',value]
    if not allowed_dataset(value,prefixes):raise ValueError('dataset_scope')
    if operation=='members' and '(' not in value:return ['zos-files','list','all-members',value]
    if operation=='view':return ['zos-files','view','data-set',value]
    raise ValueError('unsupported_operation')

def allowed_prefixes(root):
    from dotenv import dotenv_values
    values=dotenv_values(Path(root)/'.env',interpolate=False)
    raw=values.get('ZOWE_ALLOWED_DATASET_PREFIXES','')
    prefixes=raw.split(',') if isinstance(raw,str) and raw else []
    prefixes=[p.strip() for p in prefixes]
    if len(prefixes)>64 or any(not DATASET.fullmatch(p) or '(' in p or len(p)>44 for p in prefixes):
        raise ConfigurationError('DATASET_PREFIXES_INVALID')
    return prefixes

def extract(root,options,operation,dataset,prefixes):
    args=read_arguments(operation,dataset,prefixes)
    _,env=build_command(options)
    command=[options['node'],options['cli_js'],*args,'--response-format-json','--reject-unauthorized','true']
    root=Path(root).resolve(strict=True)
    dest=root
    for name in ['.migration','evidence','zowe']:
        dest=dest/name
        if dest.is_symlink():raise ConfigurationError('EVIDENCE_PATH_INVALID')
        dest.mkdir(exist_ok=True)
    if not dest.resolve().is_relative_to(root):raise ConfigurationError('EVIDENCE_PATH_INVALID')
    path=None;proc=None;keep=False
    try:
        with tempfile.NamedTemporaryFile(dir=dest,prefix='pending-',suffix='.json',delete=False) as out:
            path=Path(out.name)
            proc=subprocess.Popen(command,env=env,shell=False,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.DEVNULL,cwd=root)
            deadline=time.monotonic()+30
            while proc.poll() is None:
                if path.stat().st_size>MAX_BYTES:return {'ok':False,'code':'OUTPUT_LIMIT_NARROW_SCOPE'}
                if time.monotonic()>deadline:return {'ok':False,'code':'ZOWE_READ_TIMEOUT'}
                time.sleep(0.05)
        if proc.returncode!=0:return {'ok':False,'code':'ZOWE_READ_FAILED'}
        if path.stat().st_size>MAX_BYTES:return {'ok':False,'code':'OUTPUT_LIMIT_NARROW_SCOPE'}
        raw=path.read_bytes()
        result=json.loads(raw)
        if not isinstance(result,dict) or result.get('success') is not True:
            return {'ok':False,'code':'ZOWE_RESPONSE_UNVERIFIED'}
        final=dest/(uuid.uuid4().hex+'.json');path.rename(final);keep=True
        return {'ok':True,'operation':operation,'dataset':dataset,'evidence_path':str(final.relative_to(root)),
                'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                'coverage':'Inspect CLI continuation/pagination; this is not proof of complete dataset inventory.',
                'format':'Unmodified Zowe JSON response. Text view is not original binary/mainframe record bytes.'}
    except Exception:
        return {'ok':False,'code':'ZOWE_READ_FAILED'}
    finally:
        if proc is not None and proc.poll() is None:
            try:proc.kill();proc.wait(timeout=5)
            except Exception:pass
        if path is not None and not keep:
            try:path.unlink(missing_ok=True)
            except OSError:pass

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--operation',choices=['scope','datasets','members','view'],required=True)
    parser.add_argument('--dataset')
    args=parser.parse_args()
    try:
        options=read_configuration(args.project_root);prefixes=allowed_prefixes(args.project_root)
        result=({'ok':True,'allowed_dataset_prefixes':prefixes,'scope':'local_config_only'} if args.operation=='scope'
                else extract(args.project_root,options,args.operation,args.dataset,prefixes))
    except (ConfigurationError,ValueError):result={'ok':False,'code':'ZOWE_SCOPE_OR_CONFIGURATION_INVALID'}
    except Exception:result={'ok':False,'code':'ZOWE_READ_FAILED'}
    print(json.dumps(result))
    return 0 if result['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
