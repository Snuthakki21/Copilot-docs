"""Typed, bounded read-only source access. No free-form shell or SQL tool."""
import json
import os
import re
import subprocess
import threading
import time
import urllib.request
from urllib.parse import urlsplit
from .domain import require, decode, encode, ValidationError

READ_TOOLS={'db2_list_schemas','db2_list_tables','db2_describe_table','db2_sample_rows'}
MCP_VERSIONS=('2025-06-18','2025-03-26')
MAX_RESPONSE_BYTES=1024*1024


def endpoint(url):
    require(isinstance(url,str) and 0<len(url)<=8192 and not any(c.isspace() or ord(c)<32 or ord(c)==127 or c=='\\' for c in url),'Use an unambiguous HTTP(S) endpoint')
    try:
        parts=urlsplit(url)
        port=parts.port
    except ValueError as exc:raise ValidationError('Invalid HTTP(S) endpoint authority or port') from exc
    require(parts.scheme in ('http','https') and parts.hostname and not parts.username and not parts.password and not parts.fragment,'Use a configured HTTP(S) endpoint without embedded credentials')
    require(port is None or 1<=port<=65535,'Invalid HTTP(S) endpoint port')
    require(parts.scheme=='https' or parts.hostname in ('localhost','127.0.0.1','::1'),'Plain HTTP is allowed only on loopback')
    return url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValidationError('Endpoint redirects require explicit configuration; credentials will not be forwarded')


def _sse_response(response,request_id):
    """Consume bounded SSE events until this request's response, not stream EOF."""
    total=0;fields=[]
    while True:
        line=response.readline(MAX_RESPONSE_BYTES-total+1)
        total+=len(line);require(total<=MAX_RESPONSE_BYTES,'Remote response exceeds bound')
        if line.strip()==b'' or not line:
            if fields:
                message=decode(b'\n'.join(fields),MAX_RESPONSE_BYTES);fields=[]
                require(isinstance(message,dict),'Invalid SSE JSON-RPC message')
                if type(message.get('id')) is type(request_id) and message.get('id')==request_id and ('result' in message or 'error' in message):return message
                require('id' not in message,'Unsolicited server requests are unsupported')
            if not line:break
        elif line.startswith(b'data:'):fields.append(line[5:].lstrip(b' ').rstrip(b'\r\n'))
    raise ValidationError('SSE stream ended without the matching response')


def post_json(url,body,token='',headers=None,timeout=20):
    endpoint(url)
    h={'Content-Type':'application/json','Accept':'application/json, text/event-stream',**(headers or {})}
    if token:h['Authorization']='Bearer '+token
    request=urllib.request.Request(url,data=encode(body),headers=h,method='POST')
    try:
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=timeout) as response:
            response_headers={k.lower():v for k,v in response.headers.items()}
            content_type=response_headers.get('content-type','').split(';',1)[0].strip().lower()
            if content_type=='text/event-stream':
                require('id' in body,'Notification response must not open an SSE stream')
                return _sse_response(response,body['id']),response_headers
            data=response.read(MAX_RESPONSE_BYTES+1);require(len(data)<=MAX_RESPONSE_BYTES,'Remote response exceeds bound')
            if not data:return {},response_headers
            require(content_type=='application/json','Unsupported response content type')
            return decode(data,MAX_RESPONSE_BYTES),response_headers
    except ValidationError:raise
    except Exception as exc:raise ValidationError('Configured endpoint could not complete the bounded request; check private endpoint/auth/trust settings') from exc


class Db2MCP:
    def __init__(self,url,token=''):
        self.url=endpoint(url);self.token=token;self.counter=0;self.session=None;self.tools=set();self.protocol=None;self.timeout=20
    def headers(self):
        # Initialization negotiates in its body. Only subsequent requests send
        # the negotiated header, so an older server can return its own version.
        headers={'MCP-Protocol-Version':self.protocol} if self.protocol else {}
        if self.session:headers['Mcp-Session-Id']=self.session
        return headers
    def rpc(self,method,params):
        require(method in ('initialize','tools/list','tools/call') and isinstance(params,dict),'Only the read-only MCP protocol operations are allowed')
        if method=='tools/call':
            require(set(params)<={'name','arguments'} and isinstance(params.get('name'),str),'Invalid MCP read operation')
            catalog_sql(params['name'],params.get('arguments',{}))
        require(method=='initialize' or self.protocol in MCP_VERSIONS,'Initialize and negotiate MCP before calling tools')
        self.counter+=1
        result,h=post_json(self.url,{'jsonrpc':'2.0','id':self.counter,'method':method,'params':params},self.token,self.headers(),timeout=self.timeout)
        require(isinstance(result,dict) and result.get('jsonrpc')=='2.0' and type(result.get('id')) is int and result['id']==self.counter and 'result' in result and 'error' not in result,'Invalid MCP response identity or operation failure')
        session=next((v for k,v in h.items() if k.lower()=='mcp-session-id'),None)
        if session is not None:
            require(isinstance(session,str) and 0<len(session)<=512 and all(33<=ord(c)<=126 for c in session),'Invalid MCP session identifier')
            require(method=='initialize' or session==self.session,'MCP session changed unexpectedly')
            self.session=session
        return result['result']
    def initialize(self):
        self.protocol=None;self.session=None;self.tools=set()
        result=self.rpc('initialize',{'protocolVersion':MCP_VERSIONS[0],'capabilities':{},'clientInfo':{'name':'mainframe-workbench','version':'0.1.0'}})
        require(isinstance(result,dict) and result.get('protocolVersion') in MCP_VERSIONS,'Unsupported MCP protocol version returned by server')
        require(isinstance(result.get('capabilities'),dict) and isinstance(result['capabilities'].get('tools'),dict),'MCP server does not advertise tools')
        self.protocol=result['protocolVersion']
        notification,_=post_json(self.url,{'jsonrpc':'2.0','method':'notifications/initialized'},self.token,self.headers(),timeout=self.timeout)
        require(not notification,'Initialized notification must not return a JSON-RPC result')
        cursor=None;seen=set()
        for _ in range(20):
            listing=self.rpc('tools/list',{'cursor':cursor} if cursor else {})
            require(isinstance(listing,dict) and isinstance(listing.get('tools'),list),'Invalid MCP tool listing')
            require(all(isinstance(x,dict) and isinstance(x.get('name'),str) for x in listing['tools']),'Invalid MCP tool entry')
            self.tools.update(x['name'] for x in listing['tools'])
            require(len(self.tools)<=2000,'MCP tool listing exceeds bound')
            cursor=listing.get('nextCursor')
            if cursor is None:break
            require(isinstance(cursor,str) and 0<len(cursor)<=2048 and cursor not in seen,'Invalid or repeated MCP tool cursor')
            seen.add(cursor)
        else:raise ValidationError('MCP tool listing exceeds page budget')
        require({'db2_list_schemas','db2_list_tables'}<=self.tools,'MCP server needs exploratory schema/table tools; configure the supplied read-only gateway or a compatible server')
        return {'status':'CONNECTED','protocol_version':self.protocol,'read_tools':sorted(self.tools & READ_TOOLS)}
    def call(self,name,args):
        require(name in READ_TOOLS,'Only the explicit read-only Db2 operations are allowed')
        require(name in self.tools,'Required read capability is unavailable')
        catalog_sql(name,args)
        result=self.rpc('tools/call',{'name':name,'arguments':args})
        require(isinstance(result,dict) and result.get('isError',False) is False,'Db2 read failed')
        if 'structuredContent' in result:
            require(isinstance(result['structuredContent'],dict),'Db2 structured data must be an object')
            return result['structuredContent']
        content=result.get('content',[])
        require(isinstance(content,list) and all(isinstance(c,dict) for c in content),'Invalid Db2 content blocks')
        for c in content:
            if c.get('type')=='text':
                require(isinstance(c.get('text'),str),'Db2 text content must be a string')
                try:data=decode(c['text'].encode(),MAX_RESPONSE_BYTES)
                except UnicodeError as exc:raise ValidationError('Db2 text content must be valid UTF-8') from exc
                require(isinstance(data,dict),'Db2 structured data must be an object')
                return data
        raise ValidationError('Db2 tool returned no structured data')
    def list_schemas(self,after_schema=''):return self.call('db2_list_schemas',{'after_schema':after_schema,'limit':100})
    def list_tables(self,schema=None,after_schema='',after_table=''):
        return self.call('db2_list_tables',{'schema':schema,'after_schema':after_schema,'after_table':after_table,'limit':100})
    def describe(self,schema,table,after_column=-1):return self.call('db2_describe_table',{'schema':schema,'table':table,'after_column':after_column})
    def sample(self,schema,table,limit=10):return self.call('db2_sample_rows',{'schema':schema,'table':table,'limit':limit})


def sql_name(value):
    require(isinstance(value,str) and re.fullmatch(r'[A-Za-z@$#][A-Za-z0-9_@$#]{0,127}',value),'Unsupported/unsafe SQL identifier')
    return '"'+value+'"'


def catalog_sql(operation,args):
    require(operation in READ_TOOLS,'No arbitrary or mutating SQL operations are exposed')
    require(isinstance(args,dict),'Read arguments must be an object')
    allowed={
        'db2_list_schemas':{'limit','after_schema'},
        'db2_list_tables':{'limit','schema','after_schema','after_table'},
        'db2_describe_table':{'limit','schema','table','after_column'},
        'db2_sample_rows':{'limit','schema','table'},
    }
    require(set(args)<=allowed[operation],'Unsupported read argument')
    limit=args.get('limit',100);require(type(limit)is int and 1<=limit<=100,'Read row limit must be 1..100')
    if operation=='db2_list_schemas':
        after=args.get('after_schema','');require(isinstance(after,str) and len(after)<=128,'Invalid schema cursor')
        return f'SELECT DISTINCT CREATOR FROM SYSIBM.SYSTABLES WHERE CREATOR > ? ORDER BY CREATOR FETCH FIRST {limit+1} ROWS ONLY WITH UR',[after]
    if operation=='db2_list_tables':
        schema=args.get('schema')
        require(schema is None or isinstance(schema,str) and len(schema)<=128,'Invalid schema pattern')
        pattern=schema if schema else '%'
        a,b=args.get('after_schema',''),args.get('after_table','')
        require(isinstance(a,str) and isinstance(b,str) and len(a)<=128 and len(b)<=128,'Invalid catalog cursor')
        return f"SELECT CREATOR,NAME,TYPE FROM SYSIBM.SYSTABLES WHERE CREATOR LIKE ? AND (CREATOR > ? OR (CREATOR = ? AND NAME > ?)) ORDER BY CREATOR,NAME FETCH FIRST {limit+1} ROWS ONLY WITH UR",[pattern,a,a,b]
    schema,table=args.get('schema'),args.get('table');s,t=sql_name(schema),sql_name(table)
    if operation=='db2_describe_table':
        after=args.get('after_column',-1);require(type(after)is int and -1<=after<=32767,'Invalid column cursor')
        return f'SELECT NAME,COLTYPE,LENGTH,SCALE,NULLS,COLNO FROM SYSIBM.SYSCOLUMNS WHERE TBCREATOR=? AND TBNAME=? AND COLNO > ? ORDER BY COLNO FETCH FIRST {limit+1} ROWS ONLY WITH UR',[schema,table,after]
    return f'SELECT * FROM {s}.{t} FETCH FIRST {limit} ROWS ONLY WITH UR',[]


def discover_catalog(client,kind,max_pages=10,max_bytes=2*1024*1024,max_seconds=60):
    """Follow the supplied gateway's keyset cursors within explicit budgets."""
    require(kind in ('schemas','tables') and type(max_pages)is int and 1<=max_pages<=50,'Invalid catalog page budget')
    require(type(max_bytes)is int and 1024<=max_bytes<=8*1024*1024 and type(max_seconds) in (int,float) and 0<max_seconds<=300,'Invalid catalog resource budget')
    output={'rows':[],'pages':0,'coverage':'PARTIAL','reason':'page_budget','next_cursor':None,
            'bounded':True,'snapshot_consistent':False,'scope':'Account-visible catalog traversal, not an authorization inventory or consistent snapshot',
            'budgets':{'max_pages':max_pages,'max_bytes':max_bytes,'max_seconds':max_seconds}}
    cursor={};seen=set();size=0;deadline=time.monotonic()+max_seconds;old_timeout=client.timeout
    try:
        for _ in range(max_pages):
            remaining=deadline-time.monotonic()
            if remaining<=0:output['reason']='time_budget';break
            client.timeout=min(old_timeout,remaining)
            try:page=client.list_schemas(**cursor) if kind=='schemas' else client.list_tables(**cursor)
            except ValidationError:
                output['reason']='page_read_failed';break
            if not isinstance(page,dict) or not isinstance(page.get('rows'),list) or len(page['rows'])>100 or not all(isinstance(row,dict) for row in page['rows']):
                output['reason']='invalid_page';break
            try:page_size=len(encode(page))
            except (ValueError,TypeError,UnicodeError,RecursionError):
                output['reason']='invalid_page';break
            if size+page_size>max_bytes:output['reason']='byte_budget';break
            # Reject a repeated continuation before adding the repeated page.
            if page.get('has_more') is True and isinstance(page.get('next_cursor'),dict) and encode(page['next_cursor']) in seen:
                output.update(reason='repeated_cursor',next_cursor=None);break
            size+=page_size;output['pages']+=1;output['rows'].extend(page['rows'])
            more=page.get('has_more')
            if more is False:
                output.update(coverage='COMPLETE',reason=None,next_cursor=None);break
            if more is not True:
                output.update(reason='continuation_unavailable',next_cursor=None);break
            next_cursor=page.get('next_cursor');keys={'after_schema'} if kind=='schemas' else {'after_schema','after_table'}
            if not isinstance(next_cursor,dict) or set(next_cursor)!=keys or not all(isinstance(v,str) and 0<len(v)<=128 for v in next_cursor.values()):
                output.update(reason='invalid_cursor',next_cursor=None);break
            fingerprint=encode(next_cursor)
            if fingerprint in seen or next_cursor==cursor:
                output.update(reason='repeated_cursor',next_cursor=None);break
            seen.add(fingerprint);cursor=next_cursor;output['next_cursor']=cursor
        output['bytes']=size
        return output
    finally:client.timeout=old_timeout


def bounded_command(command,env,timeout=20,limit=1024*1024):
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,shell=False)
    chunks=[];size=[0];overflow=[False]
    def drain():
        while True:
            chunk=process.stdout.read(4096)
            if not chunk:break
            size[0]+=len(chunk)
            if size[0]>limit:overflow[0]=True;process.kill();break
            chunks.append(chunk)
    thread=threading.Thread(target=drain,daemon=True);thread.start()
    try:code=process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:process.kill();process.wait();thread.join(1);raise ValidationError('Source read timed out') from exc
    thread.join(2);process.stdout.close()
    require(not overflow[0] and code==0,'Source read failed or exceeded its output bound')
    return decode(b''.join(chunks),limit)


class ZoweReader:
    def __init__(self,profile):self.profile=profile;require(isinstance(profile,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,80}',profile),'Unsafe Zowe profile alias')
    def operation(self,op,value):
        require(op in ('list_data_sets','list_members','read_member'),'Zowe source operations are strictly read-only')
        require(isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9@$#.*()_-]{1,150}',value) and not value.startswith('-'),'Unsafe dataset/member value')
        if op!='list_data_sets':require('*' not in value,'Read/member operations require a discovered explicit dataset')
        command=['zowe','zos-files',*({'list_data_sets':['list','data-set'],'list_members':['list','all-members'],'read_member':['view','data-set']}[op]),value,'--base-profile',self.profile,'--response-format-json']
        allowed=['PATH','HOME','USERPROFILE','APPDATA','SystemRoot','ZOWE_CLI_HOME','NODE_EXTRA_CA_CERTS']
        env={k:os.environ[k] for k in allowed if k in os.environ}
        try:return bounded_command(command,env)
        except OSError as exc:raise ValidationError('Zowe CLI unavailable; configure its approved local installation/profile') from exc
    def list_datasets(self,hint='*'):return self.operation('list_data_sets',hint)
    def list_members(self,dataset):return self.operation('list_members',dataset)
    def read_member(self,member):return self.operation('read_member',member)


def read_only_discovery():
    result={'db2':{'status':'NOT_CONFIGURED'},'zowe':{'status':'NOT_CONFIGURED'}}
    if os.environ.get('WB_DB2_MCP_URL'):
        try:
            client=Db2MCP(os.environ['WB_DB2_MCP_URL'],os.environ.get('WB_DB2_MCP_TOKEN',''));status=client.initialize()
            schemas=discover_catalog(client,'schemas');tables=discover_catalog(client,'tables')
            result['db2']={**status,'schemas':schemas,'tables':tables,
                          'coverage':'COMPLETE' if schemas['coverage']==tables['coverage']=='COMPLETE' else 'PARTIAL',
                          'truncation':'Bounded keyset catalog traversal; continuation and limits are recorded per catalog. No table sample is fetched by default.'}
        except ValidationError as exc:result['db2']={'status':'UNAVAILABLE','message':str(exc)}
    if os.environ.get('WB_ZOWE_PROFILE'):
        try:result['zowe']={'status':'READ_COMPLETED','datasets':ZoweReader(os.environ['WB_ZOWE_PROFILE']).list_datasets(os.environ.get('WB_DATASET_HINT','*')),'truncation':'Response bounded to 1 MiB; catalogue completeness is not claimed.'}
        except ValidationError as exc:result['zowe']={'status':'UNAVAILABLE','message':str(exc)}
    return result
