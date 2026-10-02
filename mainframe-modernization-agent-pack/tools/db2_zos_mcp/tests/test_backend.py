"""Adversarial contract tests with a deterministic, in-memory IBM driver double."""
from dataclasses import replace
from datetime import date, datetime, time
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_config import fixture
from config import load_config


class FakeDriver:
    SQL_ATTR_ACCESS_MODE = 101
    SQL_ATTR_QUERY_TIMEOUT = 0
    def __init__(self):
        self.calls = []; self.closed = False; self.freed = []
        self.data = [(1, 'first'), (2, 'second'), (3, 'third')]
        self.columns = {'ID':'INTEGER', 'NAME':'VARCHAR', 'VALUE':'DECIMAL', 'BYTES':'VARBIN'}
        self.fail = None; self.timeouts = []; self.access_mode = 1
    def connect(self, dsn, user, password, options):
        self.calls.append(('connect', dsn, user, password, options))
        if self.fail == 'connect': raise RuntimeError('PWD=private-test-secret; private database details')
        return self
    def get_option(self, handle, key, kind):
        return self.access_mode if kind == 1 else handle['timeout']
    def prepare(self, conn, sql, options):
        self.calls.append(('prepare', sql, options))
        if self.fail == 'prepare': raise RuntimeError('private-test-secret')
        self.timeouts.append(options[self.SQL_ATTR_QUERY_TIMEOUT])
        return {'sql':sql, 'timeout':options[self.SQL_ATTR_QUERY_TIMEOUT]}
    def execute(self, stmt, params):
        self.calls.append(('execute', stmt['sql'], params))
        if self.fail == 'execute': raise RuntimeError('private-test-secret')
        sql = stmt['sql']
        if 'SELECT TYPE FROM SYSIBM.SYSTABLES' in sql:
            names, types, rows = ['TYPE'], ['string'], [('T',)]
        elif 'SELECT NAME, COLTYPE FROM SYSIBM.SYSCOLUMNS' in sql:
            names, types, rows = ['NAME','COLTYPE'], ['string','string'], [(n,self.columns[n]) for n in params[2:] if n in self.columns]
        elif 'FROM SYSIBM.SYSTABLES' in sql:
            names, types, rows = ['NAME','DBNAME','TSNAME'], ['string']*3, [('ITEMS','PHYSDB','TS1')]
        elif 'FROM SYSIBM.SYSCOLUMNS' in sql:
            names, types, rows = ['NAME','COLTYPE','LENGTH','SCALE','NULLS','COLNO','CCSID','LENGTH2'], ['string']*8, [('ID','INTEGER',4,0,'N',1,0,4)]
        else:
            names = stmt['sql'].split(' FROM ')[0].removeprefix('SELECT ').replace('"','').split(', ')
            types = [{'INTEGER':'int','VARCHAR':'string','DECIMAL':'decimal','VARBIN':'binary'}.get(self.columns.get(n),'string') for n in names]
            import re
            bounds=re.search(r'OFFSET (\d+) ROWS FETCH FIRST (\d+) ROWS',sql)
            offset,count=map(int,bounds.groups())
            rows = self.data[offset:offset+count]
        stmt.update(names=names, types=types, rows=iter(rows))
        return False if self.fail == 'execute_false' else True
    def fetch_tuple(self, stmt):
        if self.fail == 'fetch': raise RuntimeError('private-test-secret')
        return next(stmt['rows'], False)
    def num_fields(self, stmt): return len(stmt['names'])
    def field_name(self, stmt, i): return stmt['names'][i]
    def field_type(self, stmt, i): return stmt['types'][i]
    def free_stmt(self, stmt): self.freed.append(stmt); return True
    def close(self, conn): self.closed = True; return True


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('backend'), 'backend.py must implement the constrained Db2 tools')
        import backend
        self.b = backend
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); fixture(self.root)
        self.cfg = load_config(self.root); self.driver = FakeDriver()
    def run_tool(self, name='db2_read_rows', args=None):
        if args is None: args = dict(schema='APP',table='ITEMS',columns=['ID','NAME'],order_by=['ID'],limit=2)
        return self.b.execute_tool(self.cfg, self.driver, name, args)
    def test_only_four_tools_and_read_only_annotations(self):
        self.assertEqual(set(self.b.TOOL_SCHEMAS), {'db2_allowed_scope','db2_list_tables','db2_describe_table','db2_read_rows'})
        for schema in self.b.TOOL_SCHEMAS.values(): self.assertFalse(schema['additionalProperties'])
    def test_tls_separate_credentials_read_only_and_cleanup(self):
        result = self.run_tool()
        self.assertEqual(result['status'],'ok'); self.assertEqual(result['rows'], [[1,'first'],[2,'second']])
        call = self.driver.calls[0]; dsn = call[1]
        for keyword in ['SECURITY=SSL;', 'SSLClientHostnameValidation=Basic;', 'SSLServerCertificate='+str(self.cfg.certificate)+';', 'DATABASE=TESTLOC;', 'ConnectTimeout=5;']:
            self.assertIn(keyword, dsn)
        self.assertNotIn('private-test-secret',dsn); self.assertNotIn('UID=',dsn); self.assertNotIn('PWD=',dsn)
        self.assertEqual(call[2:4],('test_user','private-test-secret'))
        self.assertEqual(call[4][101],1); self.assertTrue(self.driver.closed)
        self.assertEqual(len(self.driver.freed),3)
        self.assertEqual(result['next_offset'],2); self.assertTrue(result['has_more'])
        self.assertTrue(all(x==10 for x in self.driver.timeouts))
    def test_fixed_catalog_parameterized_queries(self):
        result = self.run_tool('db2_list_tables', dict(schema='APP'))
        self.assertEqual(result['status'],'ok')
        executed = [c for c in self.driver.calls if c[0]=='execute']
        self.assertIn('CREATOR = ?',executed[0][1]); self.assertNotIn("'APP'", executed[0][1])
        self.assertEqual(executed[0][2],('APP','ITEMS','OTHER'))
        self.assertIn("TYPE = 'T'",executed[0][1])
    def test_metadata_description_scope_and_pagination(self):
        result = self.run_tool('db2_describe_table',dict(schema='APP',table='ITEMS',limit=1,offset=2))
        self.assertEqual(result['status'],'ok')
        queries = [x for x in self.driver.calls if x[0]=='execute']
        self.assertIn('OFFSET 2 ROWS FETCH FIRST 2 ROWS ONLY',queries[-1][1])
        self.assertEqual(queries[-1][2],('APP','ITEMS'))
    def test_filter_injection_stays_bound_and_null_uses_is_null(self):
        payload="x'; DELETE FROM APP.ITEMS; --"
        args=dict(schema='APP',table='ITEMS',columns=['ID','NAME'],order_by=['ID'], filters={'NAME':payload,'ID':None})
        self.assertEqual(self.run_tool(args=args)['status'],'ok')
        sql, params=[x[1:] for x in self.driver.calls if x[0]=='execute'][-1]
        self.assertNotIn(payload,sql); self.assertEqual(params,(payload,)); self.assertIn('"ID" IS NULL',sql)
    def test_rejects_identifier_injection_unknown_tools_and_bad_params_before_connect(self):
        good=dict(schema='APP',table='ITEMS',columns=['ID'],order_by=['ID'])
        cases=[{'schema':'SYSIBM'}, {'table':'OTHER_NOT_ALLOWED'}, {'table':'ITEMS";DROP TABLE X;--'},
               {'schema':'APP.BAD'}, {'columns':['*']}, {'columns':['ID) FROM SECRET--']},
               {'columns':[]}, {'columns':['ID','ID']}, {'order_by':[]}, {'order_by':['ID DESC']},
               {'limit':True},{'limit':0},{'limit':101},{'limit':'2'},{'offset':-1},{'offset':10001},
               {'sql':'DELETE FROM APP.ITEMS'},{'filters':{'ID':float('nan')}},{'filters':{'ID':{'x':1}}},
               {'filters':{'NAME':'x'*2049}},{'filters':{'ID':True}}]
        for change in cases:
            with self.subTest(change=change):
                self.driver.calls.clear(); result=self.run_tool(args={**good,**change})
                self.assertEqual(result['status'],'error'); self.assertFalse(self.driver.calls)
        self.assertEqual(self.run_tool('run_sql',{})['status'],'error')
        self.assertEqual(self.run_tool(args=['APP'])['status'],'error')
    def test_empty_allowlists_never_connect(self):
        self.cfg=replace(self.cfg,allowed_schemas=frozenset(),allowed_tables=frozenset())
        self.assertEqual(self.run_tool()['status'],'error'); self.assertFalse(self.driver.calls)
    def test_unknown_or_lob_columns_fail_before_data_query(self):
        for name, kind in [('MISSING',None),('NAME','CLOB'),('NAME','XML'),('NAME','DISTINCT')]:
            if kind: self.driver.columns[name]=kind
            result=self.run_tool(args=dict(schema='APP',table='ITEMS',columns=[name],order_by=['ID']))
            self.assertEqual(result['status'],'error')
            self.assertFalse(any('FROM "APP"' in c[1] for c in self.driver.calls if c[0]=='prepare'))
    def test_driver_errors_are_static_and_cleanup_runs(self):
        for mode in ['connect','prepare','execute','execute_false','fetch']:
            self.driver=FakeDriver(); self.driver.fail=mode
            result=self.run_tool(); self.assertEqual(result['status'],'error')
            self.assertNotIn('private-test-secret', json.dumps(result)); self.assertNotIn('private database',json.dumps(result))
            if mode!='connect': self.assertTrue(self.driver.closed)
    def test_read_only_mode_must_be_accepted(self):
        self.driver.access_mode=0
        result=self.run_tool(); self.assertEqual(result['code'],'driver_options_rejected')
        self.assertFalse(any(c[0]=='prepare' for c in self.driver.calls))
    def test_output_numbers_binary_null_and_unicode_are_lossless(self):
        values=[Decimal('12345678901234567890.123400'),2**63-1,b'\x00\xff',None,'  \u00e9\u96ea  ',1.125,date(2026,1,2),time(1,2,3),datetime(2026,1,2,3,4,5),float('inf')]
        encoded=[self.b.encode_value(v) for v in values]
        self.assertEqual(encoded[:5],[{'type':'decimal','value':'12345678901234567890.123400'}, {'type':'integer','value':str(2**63-1)}, {'type':'binary','encoding':'base64','value':'AP8='},None,'  \u00e9\u96ea  '])
        self.assertEqual(encoded[5],{'type':'float','value':'1.125'})
        self.assertEqual(encoded[-1],{'type':'float','value':'inf'})
        json.dumps(encoded,allow_nan=False)
    def test_decimal_driver_strings_are_tagged(self):
        self.driver.data=[('12345678901234567890.1200',)]
        result=self.run_tool(args=dict(schema='APP',table='ITEMS',columns=['VALUE'],order_by=['ID']))
        self.assertEqual(result['rows'],[[{'type':'decimal','value':'12345678901234567890.1200'}]])
    def test_byte_cap_returns_partial_without_silent_cell_truncation(self):
        self.cfg=replace(self.cfg,max_bytes=2048)
        self.driver.data=[(1,'a'*1000),(2,'b'*1000),(3,'c'*1000)]
        result=self.run_tool(args=dict(schema='APP',table='ITEMS',columns=['ID','NAME'],order_by=['ID'],limit=3))
        self.assertLessEqual(len(self.b.json_bytes(result)),2048)
        self.assertEqual(result['rows'],[[1,'a'*1000]])
        self.assertEqual(result['truncated_reason'],'byte_limit'); self.assertEqual(result['next_offset'],1)
    def test_oversized_first_row_and_unknown_values_fail_without_repr(self):
        self.cfg=replace(self.cfg,max_bytes=2048); self.driver.data=[(1,'a'*10000)]
        self.assertEqual(self.run_tool()['code'],'row_too_large')
        class Bad:
            def __repr__(self): return 'private-test-secret'
        self.driver.data=[(1,Bad())]
        result=self.run_tool(); self.assertEqual(result['status'],'error'); self.assertNotIn('private-test-secret',json.dumps(result))
    def test_byte_page_continuations_preserve_rows_without_gaps_or_duplicates(self):
        self.cfg=replace(self.cfg,max_bytes=2048)
        self.driver.data=[(1,'a'*1000),(2,'b'*1000),(3,'c'*1000)]
        rows=[]; offset=0
        for _ in range(3):
            result=self.run_tool(args=dict(schema='APP',table='ITEMS',columns=['ID','NAME'],order_by=['ID'],limit=3,offset=offset))
            self.assertEqual(result['status'],'ok')
            rows.extend(result['rows'])
            if not result['has_more']: break
            self.assertGreater(result['next_offset'],offset)
            offset=result['next_offset']
        self.assertEqual(rows,[list(row) for row in self.driver.data])
        self.assertFalse(result['has_more'])

    def test_empty_result_reports_no_next_page(self):
        self.driver.data=[]; result=self.run_tool()
        self.assertEqual(result['rows'],[]); self.assertFalse(result['has_more']); self.assertIsNone(result['next_offset'])

if __name__=='__main__': unittest.main()
