"""Only fixed catalog reads and validated single-table SELECTs are expressible."""
import base64
from datetime import date, datetime, time
from decimal import Decimal
import json

from jsonschema import Draft202012Validator
from config import identifier

# ODBC's public sqlext.h defines SQL_MODE_READ_ONLY as 1UL. ibm_db exposes
# SQL_ATTR_ACCESS_MODE but does not consistently export SQL_MODE_READ_ONLY.
# This is advisory; DBA-enforced SELECT-only privileges are mandatory.
SQL_MODE_READ_ONLY = 1
MAX_REQUEST_BYTES = 16384
ID = {'type':'string', 'pattern':r'^[A-Z][A-Z0-9_@$#]{0,127}$', 'maxLength':128}
PAGING = {'limit':{'type':'integer','minimum':1,'maximum':500}, 'offset':{'type':'integer','minimum':0,'maximum':100000}}

def _schema(properties, required):
    return {'type':'object','properties':properties,'required':required,'additionalProperties':False}

TOOL_SCHEMAS = {
    'db2_allowed_scope': _schema({}, []),
    'db2_list_tables': _schema({'schema':ID,**PAGING}, ['schema']),
    'db2_describe_table': _schema({'schema':ID,'table':ID,**PAGING}, ['schema','table']),
    'db2_read_rows': _schema({
        'schema':ID,'table':ID,**PAGING,
        'columns':{'type':'array','items':ID,'minItems':1,'maxItems':32,'uniqueItems':True},
        'order_by':{'type':'array','items':ID,'minItems':1,'maxItems':8,'uniqueItems':True},
        'filters':{'type':'object','maxProperties':16,'propertyNames':ID,'additionalProperties':{
            'oneOf':[{'type':'string','maxLength':2048}, {'type':'integer','minimum':-(2**63),'maximum':2**63-1}, {'type':'null'}]}},
    }, ['schema','table','columns','order_by']),
}
MESSAGES = {
    'invalid_arguments':'Invalid tool arguments. Use the advertised schema and configured limits.',
    'not_allowed':'The requested schema or table is not explicitly allowed in the project .env.',
    'table_unavailable':'The allowed object is unavailable or is not a base table.',
    'unsupported_column':'A requested column is absent or uses an unsupported large/complex data type.',
    'driver_options_rejected':'The IBM driver did not accept required read-only or timeout options.',
    'database_error':'The database operation failed. Ask the DBA to check TLS, network, authorization, catalog and SQL compatibility.',
    'invalid_result':'The driver returned an unsupported result value or shape.',
    'row_too_large':'One complete row exceeds the response byte limit. Request fewer columns or narrower filters.',
    'timeout':'The operation exceeded its deadline; its local database worker was stopped.',
    'driver_unavailable':'Install the approved IBM ibm_db wheel and supported bundled CLI; no driver is installed automatically.',
    'driver_unverified':'The bundled IBM CLI version could not be verified as 11.5.6 or later; connection was not attempted.',
    'configuration_error':'Complete and validate the project .env and certs/db2-ca.cer before using database tools.',
    'scope_too_large':'Configured scope metadata exceeds the response limit. Narrow the local allowlists or increase the bounded byte limit.',
    'worker_failed':'The local database worker failed without returning a valid bounded result.',
}

class SafeError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(MESSAGES[code])


def error(code):
    return {'status':'error','code':code,'message':MESSAGES[code]}


def json_bytes(value):
    return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')


def validate_request(cfg, name, args):
    try:
        if name not in TOOL_SCHEMAS or not isinstance(args, dict) or len(json_bytes(args)) > MAX_REQUEST_BYTES:
            raise SafeError('invalid_arguments')
        if not Draft202012Validator(TOOL_SCHEMAS[name]).is_valid(args):
            raise SafeError('invalid_arguments')
        if name == 'db2_allowed_scope': return
        # Revalidate with fullmatch: JSON Schema's $ can accept a final newline.
        identifier(args['schema'])
        if 'table' in args: identifier(args['table'])
        for name_list in ('columns','order_by'):
            for name_value in args.get(name_list, []): identifier(name_value)
        for key in args.get('filters', {}): identifier(key)
        if args['schema'] not in cfg.allowed_schemas:
            raise SafeError('not_allowed')
        if 'table' in args and (args['schema'],args['table']) not in cfg.allowed_tables:
            raise SafeError('not_allowed')
        if not any(s == args['schema'] for s,t in cfg.allowed_tables):
            raise SafeError('not_allowed')
        if args.get('limit', min(100,cfg.max_rows)) > cfg.max_rows or args.get('offset',0) > cfg.max_offset:
            raise SafeError('invalid_arguments')
    except SafeError:
        raise
    except Exception:
        raise SafeError('invalid_arguments') from None


def allowed_scope(cfg):
    # Deliberately assemble an allowlist; never serialize the Config object.
    result = {'status':'ok','allowed_schemas':sorted(cfg.allowed_schemas),
              'allowed_tables':[s+'.'+t for s,t in sorted(cfg.allowed_tables)],
              'limits':{'max_rows':cfg.max_rows,'max_bytes':cfg.max_bytes,'max_offset':cfg.max_offset,
                        'query_timeout_seconds':cfg.query_timeout,'connect_timeout_seconds':cfg.connect_timeout}}
    return result if len(json_bytes(result)) <= cfg.max_bytes else error('scope_too_large')


def encode_value(value, driver_type=''):
    if value is None or isinstance(value, bool): return value
    if isinstance(value, Decimal): return {'type':'decimal','value':str(value)}
    if isinstance(value, int):
        return value if abs(value) <= 2**53-1 else {'type':'integer','value':str(value)}
    if isinstance(value, float): return {'type':'float','value':repr(value)}
    if isinstance(value, (bytes,bytearray,memoryview)):
        return {'type':'binary','encoding':'base64','value':base64.b64encode(bytes(value)).decode('ascii')}
    if isinstance(value, datetime): return {'type':'datetime','value':value.isoformat()}
    if isinstance(value, time): return {'type':'time','value':value.isoformat()}
    if isinstance(value, date): return {'type':'date','value':value.isoformat()}
    if isinstance(value, str):
        if driver_type.lower() in {'decimal','numeric','decfloat'}: return {'type':'decimal','value':value}
        return value
    raise SafeError('invalid_result')


def connection_string(cfg):
    # Every inserted field was validated; credentials are intentionally separate.
    return (f'DATABASE={cfg.database};HOSTNAME={cfg.hostname};PORT={cfg.port};PROTOCOL=TCPIP;'
            f'SECURITY=SSL;SSLServerCertificate={cfg.certificate};SSLClientHostnameValidation=Basic;'
            f'ConnectTimeout={cfg.connect_timeout};')


def _quoted(name):
    return '"' + identifier(name) + '"'


def _page_clause(offset, count):
    # Numeric literals are bounded validated integers, never caller-supplied SQL.
    return f' OFFSET {offset} ROWS FETCH FIRST {count} ROWS ONLY FOR READ ONLY WITH CS'


class QuerySession:
    def __init__(self, cfg, driver):
        self.cfg, self.driver, self.connection = cfg, driver, None
        self.statements = []
    def connect(self):
        self.connection = self.driver.connect(connection_string(self.cfg),self.cfg.username,self.cfg.password,
                                              {self.driver.SQL_ATTR_ACCESS_MODE:SQL_MODE_READ_ONLY})
        if not self.connection: raise SafeError('database_error')
        if self.driver.get_option(self.connection,self.driver.SQL_ATTR_ACCESS_MODE,1) != SQL_MODE_READ_ONLY:
            raise SafeError('driver_options_rejected')
    def query(self, sql, values=()):
        if len(sql.encode('utf-8')) > MAX_REQUEST_BYTES: raise SafeError('invalid_arguments')
        stmt = self.driver.prepare(self.connection,sql,{self.driver.SQL_ATTR_QUERY_TIMEOUT:self.cfg.query_timeout})
        if not stmt: raise SafeError('database_error')
        self.statements.append(stmt)
        actual = self.driver.get_option(stmt,self.driver.SQL_ATTR_QUERY_TIMEOUT,0)
        if type(actual) is not int or not 0 < actual <= self.cfg.query_timeout:
            raise SafeError('driver_options_rejected')
        if self.driver.execute(stmt,tuple(values)) is not True: raise SafeError('database_error')
        return stmt
    def rows(self, stmt):
        while True:
            row = self.driver.fetch_tuple(stmt)
            if row is False: return
            if not isinstance(row, tuple): raise SafeError('invalid_result')
            yield row
    def require_table(self, schema, table):
        stmt = self.query('SELECT TYPE FROM SYSIBM.SYSTABLES WHERE CREATOR = ? AND NAME = ? AND TYPE = \'T\''
                          + ' FETCH FIRST 1 ROW ONLY FOR READ ONLY WITH CS',(schema,table))
        if next(self.rows(stmt),None) != ('T',): raise SafeError('table_unavailable')
    def close(self):
        for stmt in reversed(self.statements):
            try: self.driver.free_stmt(stmt)
            except Exception: pass
        if self.connection:
            try: self.driver.close(self.connection)
            except Exception: pass


def page(session, stmt, limit, offset, data_page=False):
    driver, cfg = session.driver, session.cfg
    count = driver.num_fields(stmt)
    if type(count) is not int or not 1 <= count <= 32: raise SafeError('invalid_result')
    columns = [{'name':driver.field_name(stmt,i),'driver_type':driver.field_type(stmt,i)} for i in range(count)]
    if any(not isinstance(c['name'],str) or len(c['name'])>128 or not isinstance(c['driver_type'],str) or len(c['driver_type'])>64 for c in columns):
        raise SafeError('invalid_result')
    result = {'status':'ok','columns':columns,'rows':[],'row_count':0,'offset':offset,
              'has_more':False,'next_offset':None,'truncated_reason':None,
              'encoding':'Tagged decimal/large integer/float values use strings; binary uses base64; text is driver-decoded Unicode.'}
    if data_page:
        result['pagination_note'] = 'Use a unique order_by key and a stable dataset. Separate calls are not a consistent snapshot.'
    for row in session.rows(stmt):
        if len(row) != count: raise SafeError('invalid_result')
        if result['row_count'] == limit:
            result.update(has_more=True,truncated_reason='row_limit'); break
        encoded = [encode_value(v,columns[i]['driver_type']) for i,v in enumerate(row)]
        result['rows'].append(encoded); result['row_count'] += 1
        # Reserve the real continuation envelope before testing the UTF-8 byte cap.
        result.update(has_more=True,next_offset=offset+result['row_count'],truncated_reason='byte_limit')
        if len(json_bytes(result)) > cfg.max_bytes:
            result['rows'].pop(); result['row_count'] -= 1
            if not result['row_count']: raise SafeError('row_too_large')
            break
        result.update(has_more=False,next_offset=None,truncated_reason=None)
    if result['has_more']:
        next_offset = offset + result['row_count']
        if next_offset <= cfg.max_offset: result['next_offset'] = next_offset
        else: result.update(next_offset=None,truncated_reason='offset_limit')
    if len(json_bytes(result)) > cfg.max_bytes: raise SafeError('row_too_large')
    return result


# Large/complex columns are excluded before fetching to avoid materializing a
# multi-gigabyte LOB just to discover that it exceeds the response limit.
SCALAR_TYPES = {'SMALLINT','INTEGER','BIGINT','DECIMAL','NUMERIC','DECFLOAT','FLOAT',
                'CHAR','VARCHAR','GRAPHIC','VARG','VARGRAPH','DATE','TIME','TIMESTMP','TIMESTZ','BINARY','VARBIN'}


def execute_tool(cfg, driver, name, args):
    session = QuerySession(cfg,driver)
    try:
        validate_request(cfg,name,args)
        if name == 'db2_allowed_scope': return allowed_scope(cfg)
        schema, table = args['schema'], args.get('table')
        limit, offset = args.get('limit',min(100,cfg.max_rows)), args.get('offset',0)
        session.connect()
        if name == 'db2_list_tables':
            allowed = sorted(t for s,t in cfg.allowed_tables if s == schema)
            sql = ('SELECT NAME, DBNAME, TSNAME FROM SYSIBM.SYSTABLES WHERE CREATOR = ? AND NAME IN ('
                   + ','.join('?' for _ in allowed) + ") AND TYPE = 'T' ORDER BY NAME" + _page_clause(offset,limit+1))
            stmt = session.query(sql,(schema,*allowed))
        else:
            session.require_table(schema,table)
            if name == 'db2_describe_table':
                sql = ('SELECT NAME, COLTYPE, LENGTH, SCALE, NULLS, COLNO, CCSID, LENGTH2 FROM SYSIBM.SYSCOLUMNS '
                       'WHERE TBCREATOR = ? AND TBNAME = ? ORDER BY COLNO' + _page_clause(offset,limit+1))
                stmt = session.query(sql,(schema,table))
            else:
                requested = sorted(set(args['columns']+args['order_by']+list(args.get('filters',{}))))
                meta = session.query('SELECT NAME, COLTYPE FROM SYSIBM.SYSCOLUMNS WHERE TBCREATOR = ? AND TBNAME = ? '
                                     'AND NAME IN (' + ','.join('?' for _ in requested) + ')'
                                     + f' FETCH FIRST {len(requested)+1} ROWS ONLY FOR READ ONLY WITH CS',(schema,table,*requested))
                catalog = {}
                for i,row in enumerate(session.rows(meta)):
                    if i >= len(requested) or len(row)!=2: raise SafeError('invalid_result')
                    catalog[row[0]] = row[1].strip() if isinstance(row[1],str) else ''
                if set(catalog) != set(requested) or any(t not in SCALAR_TYPES for t in catalog.values()):
                    raise SafeError('unsupported_column')
                sql = 'SELECT ' + ', '.join(map(_quoted,args['columns'])) + ' FROM ' + _quoted(schema)+'.'+_quoted(table)
                predicates, values = [], []
                for column,value in args.get('filters',{}).items():
                    if value is None: predicates.append(_quoted(column)+' IS NULL')
                    else: predicates.append(_quoted(column)+' = ?'); values.append(value)
                if predicates: sql += ' WHERE ' + ' AND '.join(predicates)
                sql += ' ORDER BY ' + ', '.join(map(_quoted,args['order_by'])) + _page_clause(offset,limit+1)
                stmt = session.query(sql,values)
        return page(session,stmt,limit,offset,name == 'db2_read_rows')
    except SafeError as exc:
        return error(exc.code)
    except Exception:
        return error('database_error')
    finally:
        session.close()
