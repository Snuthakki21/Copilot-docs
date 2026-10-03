"""Loopback control API; explicit bounds and same-origin mutation protection."""
import base64
import secrets
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from .coordinator import Coordinator
from .domain import decode, ValidationError, require, safe_path
from .reports import portfolio

def create_app(root, origin='http://127.0.0.1:8765'):
    c=Coordinator(root);app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    app.state.coordinator=c;token=secrets.token_urlsafe(32)
    static=Path(__file__).with_name('static')
    @app.middleware('http')
    async def boundary(request, call_next):
        if request.headers.get('host')!=origin.split('://',1)[1]:return JSONResponse({'error':'Invalid host'},400)
        if request.method not in ('GET','HEAD'):
            if request.headers.get('origin')!=origin or request.headers.get('x-workbench-token')!=token:return JSONResponse({'error':'Same-origin session required'},403)
        try:response=await call_next(request)
        except Exception:response=JSONResponse({'error':'Operation failed; inspect the local event ledger'},500)
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        return response
    @app.exception_handler(ValidationError)
    async def invalid(request,exc):return JSONResponse({'error':str(exc)},400)
    async def body(request):
        raw=await request.body();result=decode(raw,12*1024*1024);require(isinstance(result,dict),'Request must be a JSON object');return result
    @app.get('/api/state')
    async def state():
        return {'processes':c.ledger.list(True),'portfolio':portfolio(c.ledger),'token':token,
                'capability':'Flat COBOL IF / literal MOVE subset. Other syntax remains blocked.',
                'connections':{'zowe_profile_configured':bool(__import__('os').environ.get('WB_ZOWE_PROFILE')),'db2_endpoint_configured':bool(__import__('os').environ.get('WB_DB2_MCP_URL')),'llm_configured':bool(c.provider),'local_source_export':(c.root/'Endeavor').is_dir()}}
    @app.post('/api/intake')
    async def intake(request:Request):
        b=await body(request)
        if b.get('xlsx'):
            from .intake import parse_intake_xlsx
            from .intake import HEADERS
            m=parse_intake_xlsx(base64.b64decode(b['xlsx'],validate=True));rows=[]
            for j in m['jobs']:
                for s in j['steps']:rows.append([j['order'],j['name'],s['order'],s['name'],s['program'],';'.join(s['inputs']),';'.join(s['outputs']),s['condition']])
            b['manifest']='- Process ID: '+m['id']+'\n- Process name: '+m['name']+'\n| '+' | '.join(HEADERS)+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)
        return c.create(b['manifest'],b['sources'],False,b.get('prompt',''))
    @app.post('/api/demo')
    async def demo():
        examples=Path(__file__).parent.parent/'examples';pid='demo-'+secrets.token_hex(4)
        manifest=(examples/'process-input.md').read_text().replace('example-referral',pid)
        sources={p.name:p.read_text() for p in (examples/'Endeavor').iterdir() if p.is_file()}
        doc=c.create(manifest,sources,True);return c.start(doc['id'])
    @app.post('/api/process/{pid}/{action}')
    async def action(pid:str,action:str,request:Request):
        if action=='start':return c.start(pid)
        if action in ('pause','resume','cancel'):return c.control(pid,action)
        require(action=='answers','Unknown action')
        b=await body(request)
        try:data=base64.b64decode(b['xlsx'],validate=True)
        except (ValueError,KeyError) as exc:raise ValidationError('Supply the returned checklist workbook') from exc
        return c.import_answers(pid,data,b.get('reviewer',''))
    @app.get('/api/process/{pid}/events')
    async def events(pid:str):return c.ledger.events(pid)
    @app.get('/api/process/{pid}/artifact')
    async def artifact(pid:str,path:str):
        p=c.artifact(pid,path);return Response(p.read_bytes(),media_type='application/octet-stream',headers={'Content-Disposition':'attachment; filename="'+p.name+'"'})
    @app.get('/{asset:path}')
    async def frontend(asset:str):
        if not asset:asset='index.html'
        p=safe_path(static,asset);require(p.is_file(),'Build the frontend first; see START_HERE.md')
        types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png'}
        return Response(p.read_bytes(),media_type=types.get(p.suffix,'application/octet-stream'))
    return app
