#!/usr/bin/env python3
"""Optional loopback Streamable-HTTP MCP gateway with four fixed read-only Db2 tools.

Requires an approved pyodbc/Db2 driver installation and a read-only account.
Credentials stay in WB_DB2_ODBC_CONNECTION. No arbitrary SQL endpoint exists.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from workbench.connectors import READ_TOOLS,catalog_sql
from workbench.domain import decode,encode,require,ValidationError


def execute(name,args):
    import pyodbc
    connection=os.environ.get('WB_DB2_ODBC_CONNECTION');require(connection,'Configure a private read-only Db2 ODBC connection')
    sql,params=catalog_sql(name,args)
    with pyodbc.connect(connection,autocommit=True,attrs_before={101:1},timeout=10) as db:
        cursor=db.cursor();cursor.timeout=15;cursor.execute(sql,*params)
        names=[x[0] for x in cursor.description];rows=cursor.fetchmany(100)
        return {'rows':[dict(zip(names,[v if v is None or type(v)in(str,int,float,bool) else str(v) for v in row])) for row in rows],'bounded':True,'read_only':True}


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        try:
            token=os.environ.get('WB_DB2_MCP_TOKEN');require(token and self.headers.get('Authorization')=='Bearer '+token,'Authentication required')
            length=int(self.headers.get('Content-Length','0'));require(0<length<=64000,'Invalid request length')
            body=decode(self.rfile.read(length));method=body.get('method')
            if method=='initialize':result={'protocolVersion':'2025-03-26','capabilities':{'tools':{}},'serverInfo':{'name':'workbench-db2-read-only','version':'0.1.0'}}
            elif method=='notifications/initialized':self.send_response(202);self.end_headers();return
            elif method=='tools/list':result={'tools':[{'name':name,'description':'Bounded read-only Db2 metadata/sample operation','inputSchema':{'type':'object','properties':{},'additionalProperties':True},'annotations':{'readOnlyHint':True,'destructiveHint':False}} for name in sorted(READ_TOOLS)]}
            elif method=='tools/call':result={'structuredContent':execute(body['params']['name'],body['params'].get('arguments',{})),'content':[]}
            else:raise ValidationError('Unsupported protocol operation')
            data=encode({'jsonrpc':'2.0','id':body.get('id'),'result':result});self.send_response(200)
        except Exception:
            data=encode({'jsonrpc':'2.0','id':None,'error':{'code':-32000,'message':'Read operation failed. Check private driver/account settings.'}});self.send_response(400)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)


if __name__=='__main__':
    require(os.environ.get('WB_DB2_MCP_TOKEN'),'Set WB_DB2_MCP_TOKEN before launching the gateway')
    ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('WB_DB2_MCP_PORT','8766'))),Handler).serve_forever()
