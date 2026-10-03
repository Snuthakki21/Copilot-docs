"""Loopback control API; explicit bounds and same-origin mutation protection."""
import base64
import secrets
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, JSONResponse
from .coordinator import Coordinator
from .domain import decode, ValidationError, require, safe_path
from .reports import portfolio

def create_app(root, origin='http://127.0.0.1:8765'):
    c=Coordinator(root)
    @asynccontextmanager
    async def lifespan(app):
        c.launch_worker()
        try:yield
        finally:await asyncio.to_thread(c.close)
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.state.coordinator=c;token=secrets.token_urlsafe(32)
    static=Path(__file__).with_name('static')
    @app.middleware('http')
    async def boundary(request, call_next):
        if request.headers.getlist('host')!=[origin.split('://',1)[1]]:
            response=JSONResponse({'error':'Invalid host'},400)
        elif request.method not in ('GET','HEAD') and (request.headers.getlist('origin')!=[origin] or request.headers.getlist('x-workbench-token')!=[token]):
            response=JSONResponse({'error':'Same-origin session required'},403)
        else:
            try:response=await call_next(request)
            except Exception:response=JSONResponse({'error':'Operation failed; inspect the local event ledger'},500)
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        return response
    @app.exception_handler(ValidationError)
    async def invalid(request,exc):return JSONResponse({'error':str(exc)},400)
    async def body(request):
        raw=bytearray()
        async for chunk in request.stream():
            if len(raw)+len(chunk)>12*1024*1024:raise HTTPException(413,'Request exceeds 12 MiB')
            raw.extend(chunk)
        result=decode(bytes(raw),12*1024*1024);require(isinstance(result,dict),'Request must be a JSON object');return result
    def display_process(doc):
        # Polling never repeats full synthetic record bodies. Evidence is downloaded on demand.
        result=dict(doc)
        result['runs']=[{k:v for k,v in run.items() if k!='programs'}|{'programs':{name:{k:v for k,v in r.items() if k not in ('actual','differences')}|{'case_count':len(r['actual']),'difference_count':len(r['differences'])} for name,r in run['programs'].items()}} for run in doc['runs']]
        if doc.get('analysis'):
            result['analysis']={k:v for k,v in doc['analysis'].items() if k!='programs'}
        return result
    @app.get('/api/state')
    async def state():
        return {'processes':[display_process(p) for p in c.ledger.list(True)],'portfolio':portfolio(c.ledger),'token':token,
                'capability':'Flat COBOL IF / literal MOVE subset. Other syntax remains blocked.',
                'connections':{'zowe_profile_configured':bool(__import__('os').environ.get('WB_ZOWE_PROFILE')),'db2_endpoint_configured':bool(__import__('os').environ.get('WB_DB2_MCP_URL')),'llm_configured':bool(c.provider),'local_source_export':(c.root/'Endeavor').is_dir()}}
    @app.get('/api/templates/intake')
    async def template():
        path=Path(__file__).parent.parent/'examples/intake-template.xlsx'
        return Response(path.read_bytes(),media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="intake-template.xlsx"'})
    @app.get('/api/preflight')
    async def preflight():
        from .preflight import inspect_workspace
        return await asyncio.to_thread(inspect_workspace,c.root,coordinator_owned=True)
    @app.get('/api/knowledge')
    async def knowledge():
        from .mainframe import load_knowledge
        package=Path(__file__).parent.parent
        return {'snapshot':load_knowledge(c.root),'application_template_path':str(package/'examples/application-knowledge.json'),
                'application_path':str(c.root/'knowledge/application-knowledge.json'),'reference_path':str(package/'knowledge/README.md')}
    @app.post('/api/intake')
    async def intake(request:Request):
        b=await body(request)
        if b.get('xlsx'):
            from .intake import parse_intake_xlsx
            from .intake import HEADERS
            require(isinstance(b['xlsx'],str),'Intake workbook must be base64 text')
            try:data=base64.b64decode(b['xlsx'],validate=True)
            except ValueError as exc:raise ValidationError('Invalid intake workbook encoding') from exc
            m=parse_intake_xlsx(data);rows=[]
            for j in m['jobs']:
                for s in j['steps']:rows.append([j['order'],j['name'],s['order'],s['name'],s['program'],';'.join(s['inputs']),';'.join(s['outputs']),s['condition']])
            b['manifest']='- Process ID: '+m['id']+'\n- Process name: '+m['name']+'\n| '+' | '.join(HEADERS)+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)
        require(isinstance(b.get('manifest'),str),'Provide a Markdown or Excel process manifest')
        return c.create(b['manifest'],b.get('sources'),False,b.get('prompt',''))
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
        require(isinstance(b.get('xlsx'),str),'Supply the returned checklist as base64 text')
        try:data=base64.b64decode(b['xlsx'],validate=True)
        except (ValueError,KeyError) as exc:raise ValidationError('Supply the returned checklist workbook') from exc
        return c.import_answers(pid,data,b.get('reviewer',''))
    @app.get('/api/process/{pid}/events')
    async def events(pid:str):return c.ledger.events(pid)
    @app.get('/api/process/{pid}/coverage')
    async def coverage(pid:str):
        from .coverage import build_coverage
        return await asyncio.to_thread(build_coverage,c.ledger.get(pid),c.root)
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
