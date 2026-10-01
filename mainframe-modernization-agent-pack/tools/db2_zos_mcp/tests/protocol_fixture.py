"""Test-only SDK launcher. No production option enables this driver double."""
import asyncio
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import execute_tool
from config import load_config
from server import serve
from test_backend import FakeDriver

def fake_executor(project_root,name,arguments):
    return execute_tool(load_config(project_root),FakeDriver(),name,arguments)

if __name__=='__main__':
    asyncio.run(serve(Path(sys.argv[1]),executor=fake_executor))
