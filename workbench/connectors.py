"""Typed, bounded read-only source access. No free-form shell or SQL tool."""
import json
import os
import re
import subprocess
import threading
import urllib.request
from urllib.parse import urlsplit
from .domain import require, decode, encode, ValidationError

READ_TOOLS={'db2_list_schemas','db2_list_tables','db2_describe_table','db2_sample_rows'}


def endpoint(url):
    parts=urlsplit(url)
    require(parts.scheme in ('http','https') and parts.hostname and not parts.username and not parts.password and not parts.fragment,'Use a configured HTTP(S) endpoint without embedded credentials')
    require(parts.scheme=='https' or parts.hostname in ('localhost','127.0.0.1','::1'),'Plain HTTP is allowed only on loopback')
    return url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValidationError('Endpoint redirects require explicit configuration; credentials will not be forwarded')


def post_json(url,body,token='',headers=None):
    endpoint(url)
    h={'Content-Type':'application/json','Accept':'application/json, text/event-stream',**(headers or {})}
    if token:h['Authorization']='Bearer '+token
    request=urllib.request.Request(url,data=encode(body),headers=h,method='POST')
    try:
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=20) as response:
            data=response.read(1024*1024+1);require(len(data)<=1024*1024,'Remote response exceeds bound')
            if not data:return {},dict(response.headers)
            if 'text/event-stream' in response.headers.get('Content-Type',''):
                events=[x[5:].strip().encode() for x in data.decode().splitlines() if x.startswith('data:')]
                require(events,'No JSON event returned');data=events[-1]
            return decode(data,1024*1024),dict(response.headers)
    except ValidationError:raise
    except Exception as exc:raise ValidationError('Configured endpoint could not complete the bounded request; check private endpoint/auth/trust settings') from exc


class Db2MCP:
    def __init__(self,url,token=''):
        self.url=endpoint(url);self.token=token;self.counter=0;self.session=None;self.tools=set()
    def rpc(self,method,params):
        self.counter+=1;headers={'MCP-Protocol-Version':'2025-03-26'}
        if self.session:headers['Mcp-Session-Id']=self.session
        result,h=post_json(self.url,{'jsonrpc':'2.0','id':self.counter,'method':method,'params':params},self.token,headers)
        self.session=h.get('Mcp-Session-Id',self.session)
        require(isinstance(result,dict) and result.get('id')==self.counter and 'result' in result and 'error' not in result,'Invalid MCP response identity or operation failure')
        return result['result']
    def initialize(self):
        self.rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'mainframe-workbench','version':'0.1.0'}})
        headers={'MCP-Protocol-Version':'2025-03-26'}
        if self.session:headers['Mcp-Session-Id']=self.session
        post_json(self.url,{'jsonrpc':'2.0','method':'notifications/initialized'},self.token,headers)
        tools=self.rpc('tools/list',{});require(isinstance(tools,dict) and isinstance(tools.get('tools'),list),'Invalid MCP tool listing')
        self.tools={x.get('name') for x in tools['tools'] if isinstance(x,dict)}
        require({'db2_list_schemas','db2_list_tables'}<=self.tools,'MCP server needs exploratory schema/table tools; configure the supplied read-only gateway or a compatible server')
        return {'status':'CONNECTED','read_tools':sorted(self.tools & READ_TOOLS)}
    def call(self,name,args):
        require(name in READ_TOOLS,'Only the explicit read-only Db2 operations are allowed')
        require(name in self.tools,'Required read capability is unavailable')
        result=self.rpc('tools/call',{'name':name,'arguments':args})
        require(isinstance(result,dict) and not result.get('isError'),'Db2 read failed')
        if 'structuredContent' in result:return result['structuredContent']
        for c in result.get('content',[]):
            if c.get('type')=='text':return decode(c['text'].encode(),1024*1024)
        raise ValidationError('Db2 tool returned no structured data')
    def list_schemas(self):return self.call('db2_list_schemas',{'limit':100})
    def list_tables(self,schema=None,after_schema='',after_table=''):
        return self.call('db2_list_tables',{'schema':schema,'after_schema':after_schema,'after_table':after_table,'limit':100})
    def describe(self,schema,table):return self.call('db2_describe_table',{'schema':schema,'table':table})
    def sample(self,schema,table,limit=10):return self.call('db2_sample_rows',{'schema':schema,'table':table,'limit':limit})


def sql_name(value):
    require(isinstance(value,str) and re.fullmatch(r'[A-Za-z@$#][A-Za-z0-9_@$#]{0,127}',value),'Unsupported/unsafe SQL identifier')
    return '"'+value+'"'


def catalog_sql(operation,args):
    require(operation in READ_TOOLS,'No arbitrary or mutating SQL operations are exposed')
    limit=args.get('limit',100);require(type(limit)is int and 1<=limit<=100,'Read row limit must be 1..100')
    if operation=='db2_list_schemas':return f'SELECT DISTINCT CREATOR FROM SYSIBM.SYSTABLES ORDER BY CREATOR FETCH FIRST {limit} ROWS ONLY WITH UR',[]
    if operation=='db2_list_tables':
        schema=args.get('schema');pattern=schema if schema else '%'
        require(isinstance(pattern,str) and len(pattern)<=128,'Invalid schema pattern')
        a,b=args.get('after_schema',''),args.get('after_table','')
        require(isinstance(a,str) and isinstance(b,str) and len(a)<=128 and len(b)<=128,'Invalid catalog cursor')
        return f"SELECT CREATOR,NAME,TYPE FROM SYSIBM.SYSTABLES WHERE CREATOR LIKE ? AND (CREATOR > ? OR (CREATOR = ? AND NAME > ?)) ORDER BY CREATOR,NAME FETCH FIRST {limit} ROWS ONLY WITH UR",[pattern,a,a,b]
    schema,table=args.get('schema'),args.get('table');s,t=sql_name(schema),sql_name(table)
    if operation=='db2_describe_table':return 'SELECT NAME,COLTYPE,LENGTH,SCALE,NULLS,COLNO FROM SYSIBM.SYSCOLUMNS WHERE TBCREATOR=? AND TBNAME=? ORDER BY COLNO WITH UR',[schema,table]
    return f'SELECT * FROM {s}.{t} FETCH FIRST {limit} ROWS ONLY WITH UR',[]


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
    def __init__(self,profile):self.profile=profile;require(re.fullmatch(r'[A-Za-z0-9_-]{1,80}',profile),'Unsafe Zowe profile alias')
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
            result['db2']={**status,'schemas':client.list_schemas(),'tables':client.list_tables(),'truncation':'At most 100 catalog rows per page; more pages require saved cursors. No table sample is fetched by default.'}
        except ValidationError as exc:result['db2']={'status':'UNAVAILABLE','message':str(exc)}
    if os.environ.get('WB_ZOWE_PROFILE'):
        try:result['zowe']={'status':'READ_COMPLETED','datasets':ZoweReader(os.environ['WB_ZOWE_PROFILE']).list_datasets(os.environ.get('WB_DATASET_HINT','*')),'truncation':'Response bounded to 1 MiB; catalogue completeness is not claimed.'}
        except ValidationError as exc:result['zowe']={'status':'UNAVAILABLE','message':str(exc)}
    return result
