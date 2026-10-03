import asyncio
import tempfile
import unittest
import json
from workbench.api import create_app

class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.app=create_app(self.tmp.name)
    async def asyncTearDown(self):
        self.app.state.coordinator.close();self.tmp.cleanup()
    async def request(self,path,method='GET',payload=None,headers=None):
        messages=[];received=False
        async def receive():
            nonlocal received
            if not received:received=True;return {'type':'http.request','body':json.dumps(payload or {}).encode(),'more_body':False}
            await asyncio.Future()
        async def send(m):messages.append(m)
        scope={'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','scheme':'http','method':method,'path':path,'raw_path':path.encode(),'query_string':b'','root_path':'','server':('127.0.0.1',8765),'client':('127.0.0.1',1000),'headers':[(b'host',b'127.0.0.1:8765'),*(headers or [])]}
        await self.app(scope,receive,send)
        return messages[0]['status'],b''.join(m.get('body',b'') for m in messages[1:])
    async def test_cross_origin_mutation_denied(self):
        status,_=await self.request('/api/demo','POST');self.assertEqual(status,403)
        _,raw=await self.request('/api/state');token=json.loads(raw)['token']
        status,_=await self.request('/api/demo','POST',headers=[(b'origin',b'http://evil.example'),(b'x-workbench-token',token.encode())]);self.assertEqual(status,403)
    async def test_real_demo_enters_single_review_stage_and_static_is_local(self):
        status,raw=await self.request('/api/state');self.assertEqual(status,200);token=json.loads(raw)['token']
        status,raw=await self.request('/api/demo','POST',headers=[(b'origin',b'http://127.0.0.1:8765'),(b'x-workbench-token',token.encode())]);self.assertEqual(status,200)
        doc=json.loads(raw);self.app.state.coordinator.advance(doc['id'])
        self.assertEqual(self.app.state.coordinator.ledger.get(doc['id'])['status'],'WAITING_SME')
        status,raw=await self.request('/');self.assertEqual(status,200);self.assertIn(b'/app.js',raw)

if __name__=='__main__':unittest.main()
