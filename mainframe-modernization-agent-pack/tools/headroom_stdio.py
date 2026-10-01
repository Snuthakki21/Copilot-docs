"""Run the approved Headroom stdio entrypoint without inheriting ambient secrets."""
import importlib.metadata
import os
from pathlib import Path
import subprocess
import sys

def safe_environment(source=None):
    source=os.environ if source is None else source
    keep=('SystemRoot','SYSTEMROOT','WINDIR','TEMP','TMP','HOME','USERPROFILE','APPDATA','LOCALAPPDATA','LANG')
    env={k:source[k] for k in keep if k in source}
    paths=[str(Path(sys.executable).absolute().parent)]
    if os.name=='nt' and env.get('SystemRoot',env.get('SYSTEMROOT')):
        paths.append(str(Path(env.get('SystemRoot',env.get('SYSTEMROOT')))/'System32'))
    elif os.name!='nt':paths.extend(['/usr/bin','/bin'])
    env.update(PATH=os.pathsep.join(paths),HEADROOM_BEACON='off',HEADROOM_UPDATE_CHECK='off',DO_NOT_TRACK='1',PYTHONIOENCODING='utf-8')
    return env

def command_for(executable):
    return [str(executable),'mcp','serve','--transport','stdio']

def main():
    process=None
    try:
        if importlib.metadata.version('headroom-ai')!='0.39.1':raise ValueError('version')
        executable=Path(sys.executable).absolute().with_name('headroom.exe' if os.name=='nt' else 'headroom')
        if not executable.is_file():raise ValueError('entrypoint')
        process=subprocess.Popen(command_for(executable),env=safe_environment(),shell=False,
            stdin=sys.stdin,stdout=sys.stdout,stderr=subprocess.DEVNULL,cwd=Path(__file__).resolve().parents[1])
        code=process.wait()
        if code:print('Headroom MCP stopped. Check the approved runtime prerequisites.',file=sys.stderr)
        return code
    except KeyboardInterrupt:return 0
    except Exception:
        print('Headroom MCP could not start. Provision the pinned approved MCP environment first.',file=sys.stderr)
        return 2
    finally:
        if process is not None and process.poll() is None:
            try:process.terminate();process.wait(timeout=5)
            except Exception:
                try:process.kill();process.wait(timeout=5)
                except Exception:pass

if __name__=='__main__':raise SystemExit(main())
