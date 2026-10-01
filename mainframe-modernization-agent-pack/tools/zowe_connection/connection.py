"""On-demand, TLS-verified Zowe connection check. No installers or secret output."""
from __future__ import annotations
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import ssl
import subprocess

class ConfigurationError(Exception):
    """Carries a fixed safe code, never a configuration value."""

def valid_host(value):
    if not isinstance(value,str) or not value or len(value)>253 or value.endswith('.invalid'):
        return False
    try:
        ipaddress.ip_address(value); return True
    except ValueError:
        return bool(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?',value)) and '..' not in value

def valid_port(value):
    return isinstance(value,str) and bool(re.fullmatch(r'[0-9]{1,5}',value)) and 1<=int(value)<=65535

def read_configuration(root):
    root=Path(root).resolve(strict=True)
    path=root/'.env'
    if not path.is_file() or path.is_symlink() or path.stat().st_size>65536:
        raise ConfigurationError('ENV_FILE_REQUIRED')
    try:
        from dotenv import dotenv_values
        from dotenv.parser import parse_stream
    except ImportError:
        raise ConfigurationError('PYTHON_DOTENV_PREREQUISITE_MISSING') from None
    try:
        with path.open(encoding='utf-8') as stream:
            bindings=list(parse_stream(stream))
        keys=[b.key for b in bindings if b.key is not None]
        if any(b.error for b in bindings) or len(keys)!=len(set(keys)):
            raise ConfigurationError('ENV_SYNTAX_INVALID')
        # Read only this file; never expand ${...} or load process overrides.
        values=dotenv_values(path,interpolate=False)
        required=['ZOWE_HOST','ZOWE_PORT','ZOWE_USERNAME','ZOWE_PASSWORD','ZOWE_CA_CERTIFICATE','ZOWE_NODE_EXECUTABLE','ZOWE_CLI_JS']
        if any(not values.get(k) for k in required):
            raise ConfigurationError('ZOWE_FIELDS_REQUIRED')
        if not valid_host(values['ZOWE_HOST']) or not valid_port(values['ZOWE_PORT']):
            raise ConfigurationError('ZOWE_ENDPOINT_INVALID')
        for k in required:
            if '\x00' in values[k] or '\n' in values[k] or '\r' in values[k]:
                raise ConfigurationError('ZOWE_VALUE_INVALID')
        node=Path(values['ZOWE_NODE_EXECUTABLE'])
        cli_js=Path(values['ZOWE_CLI_JS'])
        if (not node.is_absolute() or not node.is_file() or node.name.lower() not in ('node','node.exe')
                or not cli_js.is_absolute() or not cli_js.is_file() or cli_js.name != 'main.js'):
            raise ConfigurationError('APPROVED_NODE_AND_ZOWE_JS_REQUIRED')
        node=node.resolve(strict=True); cli_js=cli_js.resolve(strict=True)
        package_file=cli_js.parent.parent/'package.json'
        if not package_file.is_file() or package_file.stat().st_size>65536:
            raise ConfigurationError('ZOWE_PACKAGE_IDENTITY_REQUIRED')
        package=json.loads(package_file.read_text(encoding='utf-8'))
        entry=package.get('bin',{}).get('zowe') if isinstance(package.get('bin'),dict) else None
        if package.get('name')!='@zowe/cli' or not isinstance(entry,str) or (package_file.parent/entry).resolve()!=cli_js:
            raise ConfigurationError('ZOWE_PACKAGE_IDENTITY_REQUIRED')
        if (root/'certs').is_symlink() or (root/values['ZOWE_CA_CERTIFICATE']).is_symlink():
            raise ConfigurationError('CERTIFICATE_PATH_INVALID')
        ca=(root/values['ZOWE_CA_CERTIFICATE']).resolve(strict=True)
        certs=(root/'certs').resolve(strict=True)
        if not certs.is_relative_to(root) or not ca.is_relative_to(certs) or not ca.is_file() or ca.stat().st_size>1048576:
            raise ConfigurationError('CERTIFICATE_PATH_INVALID')
        raw=ca.read_bytes()
        if b'PRIVATE KEY' in raw or b'-----BEGIN CERTIFICATE-----' not in raw:
            raise ConfigurationError('ZOWE_PEM_CA_REQUIRED')
        ssl.create_default_context(cafile=str(ca))
        return {'host':values['ZOWE_HOST'],'port':int(values['ZOWE_PORT']), 'user':values['ZOWE_USERNAME'],'password':values['ZOWE_PASSWORD'],'certificate':str(ca),'node':str(node),'cli_js':str(cli_js)}
    except ConfigurationError:
        raise
    except Exception:
        raise ConfigurationError('ZOWE_CONFIGURATION_INVALID') from None

def build_command(options, inherited=None):
    # Do not leak Db2 credentials, unsafe Node flags, proxy settings or ambient
    # Zowe options into this process. Keep only basic OS process requirements.
    inherited=os.environ if inherited is None else inherited
    keep=('SystemRoot','SYSTEMROOT','WINDIR','TEMP','TMP','HOME','USERPROFILE','APPDATA','LOCALAPPDATA','PROGRAMDATA','PATHEXT','COMSPEC','LANG')
    env={k:inherited[k] for k in keep if k in inherited}
    node_dir=str(Path(options['node']).parent)
    os_paths=[node_dir]
    if os.name=='nt' and env.get('SystemRoot'): os_paths.append(str(Path(env['SystemRoot'])/'System32'))
    elif os.name!='nt': os_paths += ['/usr/bin','/bin']
    env['PATH']=os.pathsep.join(os_paths)
    env.update({'ZOWE_APP_LOG_LEVEL':'OFF','ZOWE_IMPERATIVE_LOG_LEVEL':'OFF','ZOWE_OPT_HOST':options['host'],'ZOWE_OPT_PORT':str(options['port']),
        'ZOWE_OPT_USER':options['user'],'ZOWE_OPT_PASSWORD':options['password'],
        'ZOWE_OPT_PROTOCOL':'https','ZOWE_OPT_REJECT_UNAUTHORIZED':'true',
        'NODE_EXTRA_CA_CERTS':options['certificate']})
    args=[options['node'],options['cli_js'],'zosmf','check','status','--response-format-json','--reject-unauthorized','true']
    return args,env

def check(options, runner=subprocess.run):
    args,env=build_command(options)
    try:
        result=runner(args,env=env,shell=False,stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30,check=False)
        if result.returncode:
            return {'ok':False,'code':'ZOWE_CHECK_FAILED'}
        return {'ok':True,'code':'ZOSMF_STATUS_SUCCEEDED','scope':'connection_status_only'}
    except subprocess.TimeoutExpired:
        return {'ok':False,'code':'ZOWE_TIMEOUT'}
    except Exception:
        return {'ok':False,'code':'ZOWE_LAUNCH_FAILED'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--validate-only',action='store_true',help='Validate local config without starting Zowe or connecting')
    args=parser.parse_args()
    try:
        options=read_configuration(args.project_root)
        result={'ok':True,'code':'LOCAL_CONFIG_VALID_NOT_CONNECTED'} if args.validate_only else check(options)
    except ConfigurationError as exc:
        result={'ok':False,'code':str(exc)}
    except Exception:
        result={'ok':False,'code':'CONFIGURATION_FAILED'}
    print(json.dumps(result))
    return 0 if result['ok'] else 1

if __name__=='__main__':
    raise SystemExit(main())
