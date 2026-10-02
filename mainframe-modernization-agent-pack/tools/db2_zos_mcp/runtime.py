"""Bounded subprocess execution and offline IBM bundled-CLI preflight."""
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from backend import MESSAGES, SafeError, allowed_scope, error, json_bytes, validate_request
from config import ConfigError, load_config


def child_environment():
    # Deliberately exclude ambient secrets, Python injection, IBM overrides,
    # alternate driver locations and tracing switches. No inherited .env values.
    env = {k:os.environ[k] for k in ('SystemRoot','WINDIR','TEMP','TMP') if k in os.environ}
    paths = [str(Path(sys.executable).resolve().parent)]
    if os.name == 'nt' and 'SystemRoot' in env: paths.append(str(Path(env['SystemRoot'])/'System32'))
    elif os.name != 'nt': paths.extend(['/usr/bin','/bin'])
    env.update(PATH=os.pathsep.join(paths),PYTHONIOENCODING='utf-8',PYTHONUTF8='1')
    return env


def supports_hostname_validation(output):
    match = re.search(r'\bDB2 v(\d+)\.(\d+)\.(\d+)(?:\.\d+)?\b',output)
    if not match: return False
    major, minor, patch = map(int,match.groups())
    # Reject ambiguous legacy packed Windows service-level fields rather than
    # misread e.g. 0500 as feature level 500 and accept an older 11.5 client.
    return (major,minor) > (11,5) or ((major,minor)==(11,5) and 6 <= patch < 100)


def preflight_driver():
    """Run only the installed wheel's recorded absolute db2level, before login.

    External IBM client layouts are deliberately unsupported rather than trusting
    a version supplied in a setting or discovering an executable from PATH.
    """
    try:
        spec = importlib.util.find_spec('ibm_db')
        if spec is None or not spec.origin: raise SafeError('driver_unavailable')
        dist = importlib.metadata.distribution('ibm_db')
        if dist.version != '3.3.0': raise SafeError('driver_unverified')
        root = Path(dist.locate_file('')).resolve(strict=True)
        origin = Path(spec.origin).resolve(strict=True)
        recorded = {Path(dist.locate_file(f)).resolve() for f in (dist.files or [])}
        cli = root / 'clidriver'
        exe = cli / 'bin' / ('db2level.exe' if os.name == 'nt' else 'db2level')
        if (origin not in recorded or not origin.is_relative_to(root) or cli.is_symlink()
                or exe.is_symlink() or not exe.is_file() or exe.resolve() not in recorded
                or not exe.resolve().is_relative_to(cli.resolve())):
            raise SafeError('driver_unverified')
        version = subprocess.run([str(exe.resolve())],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL,cwd=str(exe.parent),env=child_environment(),
                                 timeout=5,check=False,shell=False)
        if version.returncode != 0 or len(version.stdout)>16384 or not supports_hostname_validation(version.stdout.decode('utf-8',errors='replace')):
            raise SafeError('driver_unverified')
        return cli.resolve()
    except SafeError:
        raise
    except importlib.metadata.PackageNotFoundError:
        raise SafeError('driver_unavailable') from None
    except Exception:
        raise SafeError('driver_unverified') from None


def invoke(project_root, name, arguments):
    """One disposable Python worker per call, with a hard total wall-clock cap."""
    try:
        cfg = load_config(project_root)
        validate_request(cfg,name,arguments)
    except ConfigError:
        return error('configuration_error')
    except SafeError as exc:
        return error(exc.code)
    if name == 'db2_allowed_scope': return allowed_scope(cfg)
    process = None
    try:
        command = [sys.executable,'-I',str(Path(__file__).with_name('worker.py').resolve()),str(cfg.project_root)]
        process = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                                   cwd=str(Path(__file__).parent),env=child_environment(),shell=False)
        payload = json_bytes({'name':name,'arguments':arguments})
        output,_ = process.communicate(input=payload,timeout=cfg.connect_timeout+cfg.query_timeout+5)
        if process.returncode != 0 or len(output)>cfg.max_bytes: return error('worker_failed')
        result = json.loads(output)
        if not isinstance(result,dict) or result.get('status') not in ('ok','error'): return error('worker_failed')
        if result['status']=='error':
            # Do not forward worker exception text even if a dependency wrote it.
            return error(result['code']) if result.get('code') in MESSAGES else error('worker_failed')
        if not isinstance(result.get('rows'),list) or len(json_bytes(result))>cfg.max_bytes: return error('worker_failed')
        return result
    except subprocess.TimeoutExpired:
        return error('timeout')
    except Exception:
        return error('worker_failed')
    finally:
        if process is not None and process.returncode is None:
            try: process.kill()
            except Exception: pass
            try: process.communicate(timeout=5)
            except Exception:
                try: process.wait(timeout=5)
                except Exception: pass
