"""Process boundary and preflight tests; never import an actual IBM driver."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from config import load_config
from test_config import fixture


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('runtime'), 'runtime.py must enforce subprocess deadlines and driver preflight')
        import runtime
        self.r=runtime
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); fixture(self.root); self.cfg=load_config(self.root)
    def test_child_environment_strips_ambient_credentials_and_driver_overrides(self):
        with patch.dict(os.environ,{'DB2_PASSWORD':'private-secret','SONAR_TOKEN':'private-secret','PYTHONPATH':'/bad','IBM_DB_HOME':'/bad','LD_LIBRARY_PATH':'/bad'}):
            env=self.r.child_environment()
        for key in ['DB2_PASSWORD','SONAR_TOKEN','PYTHONPATH','IBM_DB_HOME','LD_LIBRARY_PATH']: self.assertNotIn(key,env)
        self.assertEqual(env['PYTHONIOENCODING'],'utf-8')
    def test_bundled_driver_version_gate_rejects_old_missing_and_unrecognized(self):
        for text in ['DB2 v11.5.5.0','DB2 v10.5.9','unknown','DB2 v11.5.100.0','DB2 v11.5.0500.0']:
            with self.subTest(text=text):
                self.assertFalse(self.r.supports_hostname_validation(text))
        self.assertTrue(self.r.supports_hostname_validation('Informational tokens are "DB2 v11.5.9.0", "x"'))
        self.assertTrue(self.r.supports_hostname_validation('DB2 v12.1.0.0'))
    def test_timeout_kills_and_reaps_child_without_exposing_stdin(self):
        class FakeProcess:
            returncode=None
            def __init__(self): self.killed=False; self.waited=False; self.calls=0
            def communicate(self,input=None,timeout=None):
                self.calls+=1
                if self.calls==1: raise subprocess.TimeoutExpired('secret-command',timeout,output=b'private-secret')
                self.returncode=-9; return b'',None
            def kill(self): self.killed=True
            def wait(self,timeout=None): self.waited=True; self.returncode=-9
        fake=FakeProcess()
        with patch.object(self.r.subprocess,'Popen',return_value=fake) as popen:
            result=self.r.invoke(self.root,'db2_list_tables',{'schema':'APP'})
        self.assertEqual(result['code'],'timeout'); self.assertTrue(fake.killed)
        self.assertTrue(fake.waited or fake.calls==2)
        call=popen.call_args
        self.assertFalse(call.kwargs.get('shell',False)); self.assertNotIn('private-test-secret',repr(call.args))
        self.assertIn('-I',call.args[0]); self.assertNotIn('DB2_PASSWORD',call.kwargs['env'])
        self.assertNotIn('private-secret',json.dumps(result))
    def test_bad_config_and_invalid_arguments_never_spawn(self):
        with patch.object(self.r.subprocess,'Popen') as popen:
            self.assertEqual(self.r.invoke(self.root,'run_sql',{})['code'],'invalid_arguments')
            (self.root/'.env').unlink()
            self.assertEqual(self.r.invoke(self.root,'db2_list_tables',{'schema':'APP'})['code'],'configuration_error')
            popen.assert_not_called()
    def test_child_bad_output_crash_and_oversize_are_redacted(self):
        for output,code in [(b'private-secret',0),(b'{}',0),(b'a'*70000,0),(b'{"status":"ok"}',7)]:
            fake=SimpleNamespace(returncode=code,communicate=lambda **kw:(output,None))
            with patch.object(self.r.subprocess,'Popen',return_value=fake):
                result=self.r.invoke(self.root,'db2_list_tables',{'schema':'APP'})
            self.assertEqual(result['code'],'worker_failed'); self.assertNotIn('private-secret',json.dumps(result))
    def test_actual_worker_without_driver_returns_sanitized_prerequisite(self):
        # Real short-lived subprocess, but this environment intentionally has no IBM driver.
        if importlib.util.find_spec('ibm_db') is not None: self.skipTest('IBM driver present; never connect in offline suite')
        result=self.r.invoke(self.root,'db2_list_tables',{'schema':'APP'})
        self.assertEqual(result['code'],'driver_unavailable')
    def test_allowed_scope_is_local_and_omits_connection_details(self):
        with patch.object(self.r.subprocess,'Popen') as popen:
            result=self.r.invoke(self.root,'db2_allowed_scope',{})
            popen.assert_not_called()
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['allowed_schemas'],['APP'])
        self.assertEqual(result['allowed_tables'],['APP.ITEMS','APP.OTHER'])
        for forbidden in ['private-test-secret','test_user','db2.example.invalid','certificate','DATABASE','448']:
            self.assertNotIn(forbidden,json.dumps(result))
        self.assertEqual(result['limits']['max_rows'],100)

    def test_recorded_bundled_driver_runs_only_absolute_offline_version_check(self):
        pkg=self.root/'site-packages'; pkg.mkdir()
        origin=pkg/'ibm_db.pyd'; origin.write_bytes(b'test-placeholder')
        exe=pkg/'clidriver/bin'/('db2level.exe' if os.name=='nt' else 'db2level')
        exe.parent.mkdir(parents=True); exe.write_bytes(b'test-placeholder')
        dist=SimpleNamespace(version='3.3.0',files=['ibm_db.pyd',str(exe.relative_to(pkg))],locate_file=lambda f:pkg/f)
        with patch.object(self.r.importlib.util,'find_spec',return_value=SimpleNamespace(origin=str(origin))), patch.object(self.r.importlib.metadata,'distribution',return_value=dist), patch.object(self.r.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout=b'DB2 v12.1.0.0')) as run:
            self.assertEqual(self.r.preflight_driver(),(pkg/'clidriver').resolve())
            self.assertEqual(run.call_args.args[0],[str(exe.resolve())])
            self.assertFalse(run.call_args.kwargs['shell'])
            self.assertEqual(run.call_args.kwargs['timeout'],5)
            self.assertNotIn('DB2_PASSWORD',run.call_args.kwargs['env'])
            run.return_value.stdout=b'DB2 v11.5.5.0'
            with self.assertRaises(self.r.SafeError): self.r.preflight_driver()

    def test_unverified_driver_layout_refused_before_version_command(self):
        with patch.object(self.r.importlib.util,'find_spec',return_value=SimpleNamespace(origin=str(self.root/'ibm_db.so'))), patch.object(self.r.subprocess,'run') as run:
            with self.assertRaises(self.r.SafeError): self.r.preflight_driver()
            run.assert_not_called()

if __name__=='__main__': unittest.main()
