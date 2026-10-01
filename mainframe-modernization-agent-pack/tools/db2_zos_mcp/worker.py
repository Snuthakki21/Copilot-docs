"""Internal one-shot database worker. Not an independently running service."""
import importlib
import json
import os
from pathlib import Path
import sys

# -I prevents ambient Python path injection; add only this tracked server folder.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from backend import MAX_REQUEST_BYTES, SafeError, error, execute_tool, json_bytes, validate_request
from config import ConfigError, load_config
from runtime import preflight_driver


def main():
    # Keep a private result pipe; suppress native driver stdout/stderr, including
    # import diagnostics. Never print driver errors or configuration values.
    result_fd = os.dup(sys.stdout.fileno())
    with open(os.devnull,'w') as null:
        os.dup2(null.fileno(),sys.stdout.fileno())
        os.dup2(null.fileno(),sys.stderr.fileno())
    try:
        cfg = load_config(Path(sys.argv[1]))
        payload = sys.stdin.buffer.read(MAX_REQUEST_BYTES+1024)
        if len(payload)>MAX_REQUEST_BYTES+512: raise SafeError('invalid_arguments')
        request = json.loads(payload)
        validate_request(cfg,request['name'],request['arguments'])
        cli = preflight_driver()
        # The only driver path comes from validated installed package metadata.
        # It is not a credential or a caller-controlled arbitrary library path.
        os.environ['IBM_DB_HOME'] = str(cli)
        dll = os.add_dll_directory(str(cli/'bin')) if os.name=='nt' else None
        try:
            driver = importlib.import_module('ibm_db')
            if hasattr(driver,'debug'): driver.debug(False)
            result = execute_tool(cfg,driver,request['name'],request['arguments'])
        finally:
            if dll is not None: dll.close()
    except ConfigError:
        result = error('configuration_error')
    except SafeError as exc:
        result = error(exc.code)
    except Exception:
        result = error('worker_failed')
    with os.fdopen(result_fd,'wb') as pipe:
        pipe.write(json_bytes(result))


if __name__ == '__main__':
    main()
