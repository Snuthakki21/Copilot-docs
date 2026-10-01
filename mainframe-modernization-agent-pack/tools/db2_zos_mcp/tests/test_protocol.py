"""Actual official MCP SDK client/server stdio smoke test with a fake IBM backend."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_config import fixture

HERE=Path(__file__).resolve().parents[1]

class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import asyncio
        asyncio.get_running_loop().set_debug(False)
    async def test_sdk_initialize_tools_list_call_validation_and_clean_shutdown(self):
        self.assertTrue((HERE/'server.py').is_file(),'server.py must implement official SDK stdio')
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); fixture(root)
            params=StdioServerParameters(command=sys.executable,args=[str(HERE/'tests/protocol_fixture.py'),str(root)])
            async with stdio_client(params) as (read,write):
                async with ClientSession(read,write) as session:
                    init=await session.initialize()
                    self.assertEqual(init.serverInfo.name,'db2-zos-read-only')
                    listed=await session.list_tools()
                    self.assertEqual({t.name for t in listed.tools},{'db2_allowed_scope','db2_list_tables','db2_describe_table','db2_read_rows'})
                    for tool in listed.tools:
                        self.assertTrue(tool.annotations.readOnlyHint)
                        self.assertFalse(tool.annotations.destructiveHint)
                        self.assertFalse(tool.inputSchema['additionalProperties'])
                    scope=await session.call_tool('db2_allowed_scope',{})
                    self.assertFalse(scope.isError)
                    scope_data=json.loads(scope.content[0].text)
                    self.assertEqual(scope_data['allowed_tables'],['APP.ITEMS','APP.OTHER'])
                    for forbidden in ['private-test-secret','test_user','db2.example.invalid','SSLServerCertificate']:
                        self.assertNotIn(forbidden,scope.content[0].text)
                    ok=await session.call_tool('db2_read_rows',{'schema':'APP','table':'ITEMS','columns':['ID','NAME'],'order_by':['ID'],'limit':2})
                    self.assertFalse(ok.isError)
                    payload=json.loads(ok.content[0].text)
                    self.assertEqual(payload['rows'],[[1,'first'],[2,'second']]); self.assertEqual(payload['next_offset'],2)
                    for name,args in [('run_sql',{'sql':'DROP TABLE X'}),('db2_read_rows',{'password':'private-secret'}),('db2_list_tables',{'schema':'APP','limit':True})]:
                        bad=await session.call_tool(name,args)
                        self.assertTrue(bad.isError); self.assertNotIn('private-secret',str(bad))
                        self.assertEqual(json.loads(bad.content[0].text)['code'],'invalid_arguments')
    async def test_production_stdio_exposes_tools_without_config_or_database(self):
        self.assertTrue((HERE/'server.py').is_file(),'server.py must implement official SDK stdio')
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        with tempfile.TemporaryDirectory() as tmp:
            params=StdioServerParameters(command=sys.executable,args=[str(HERE/'server.py'),'--project-root',tmp])
            async with stdio_client(params) as (read,write):
                async with ClientSession(read,write) as session:
                    await session.initialize(); self.assertEqual(len((await session.list_tools()).tools),4)
                    result=await session.call_tool('db2_list_tables',{'schema':'APP'})
                    self.assertTrue(result.isError)
                    self.assertEqual(json.loads(result.content[0].text)['code'],'configuration_error')
    def test_config_check_prints_no_secret_and_never_connects(self):
        self.assertTrue((HERE/'server.py').is_file(),'server.py must implement official SDK stdio')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); fixture(root)
            result=subprocess.run([sys.executable,str(HERE/'server.py'),'--project-root',str(root),'--check-config'],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0); self.assertNotIn('private-test-secret',result.stdout+result.stderr)

if __name__=='__main__': unittest.main()

class CancellationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import asyncio
        asyncio.get_running_loop().set_debug(False)
    async def test_cancelled_call_keeps_permit_until_worker_finishes(self):
        import asyncio
        import threading
        from mcp.types import CallToolRequest, CallToolRequestParams
        from server import build_server
        entered=threading.Event(); release=threading.Event(); calls=[]
        def executor(root,name,args):
            calls.append(name); entered.set(); release.wait(2)
            return {'status':'ok','rows':[]}
        server=build_server(Path('.'),executor)
        handler=server.request_handlers[CallToolRequest]
        request=CallToolRequest(params=CallToolRequestParams(name='db2_list_tables',arguments={'schema':'APP'}))
        first=asyncio.create_task(handler(request))
        while not entered.is_set(): await asyncio.sleep(0.005)
        first.cancel(); second=asyncio.create_task(handler(request))
        try:
            await asyncio.sleep(0.05)
            self.assertEqual(len(calls),1,'Cancellation must not let another database worker overlap')
        finally:
            release.set()
            try: await first
            except asyncio.CancelledError: pass
            await second

class InputBoundaryTests(unittest.TestCase):
    def test_sdk_input_rejects_invalid_utf8_instead_of_changing_data(self):
        import io
        import server
        reader=server.BoundedInput(io.BytesIO(b'{"jsonrpc":"2.0","x":"\xff"}\n'))
        with self.assertRaises(UnicodeDecodeError): reader.readline()
    def test_sdk_input_reader_rejects_oversized_frame_before_parse(self):
        import io
        import server
        self.assertTrue(hasattr(server,'BoundedInput'),'SDK transport needs a bounded input reader')
        reader=server.BoundedInput(io.BytesIO(b'x'*65537+b'\n'))
        with self.assertRaises(ValueError): reader.readline()
        reader=server.BoundedInput(io.BytesIO(b'{"jsonrpc":"2.0"}\n'))
        self.assertEqual(reader.readline(),'{"jsonrpc":"2.0"}\n')
    def test_production_oversized_frame_stops_without_echo_or_driver(self):
        result=subprocess.run([sys.executable,str(HERE/'server.py'),'--project-root','.'],input=b'PRIVATE_SENTINEL'+b'x'*65537+b'\n',capture_output=True,timeout=10)
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn(b'PRIVATE_SENTINEL',result.stdout+result.stderr)
