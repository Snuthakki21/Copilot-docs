"""Run all authored offline suites without importing/executing vendored UI scripts."""
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parent
failed=False
for path,pattern in [(root/'db2_zos_mcp/tests','test_*.py'),(root/'zowe_connection','test_*.py'),(root,'test_headroom_stdio.py')]:
    print('Offline suite:',path.name,flush=True)
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(path),'-p',pattern],check=False)
    failed=failed or result.returncode!=0
raise SystemExit(1 if failed else 0)
