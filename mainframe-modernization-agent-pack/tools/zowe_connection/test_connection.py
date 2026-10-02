import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock

HERE=Path(__file__).parent
class Contract(unittest.TestCase):
    def module(self):
        self.assertTrue((HERE/'connection.py').exists(),'connection helper not implemented')
        spec=importlib.util.spec_from_file_location('connection',HERE/'connection.py')
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
    def test_secrets_not_in_argv_and_no_unrelated_env(self):
        m=self.module()
        args,env=m.build_command({'host':'zosmf.example.com','port':443,'user':'testuser','password':'S3cr3t;quoted','certificate':'/approved/certs/zosmf-ca.cer','node':'/approved/node','cli_js':'/approved/zowe/lib/main.js'}, {'PATH':'/bin','DB2_PASSWORD':'must-not-leak','NODE_TLS_REJECT_UNAUTHORIZED':'0','ZOWE_OPT_REJECT_UNAUTHORIZED':'false'})
        self.assertNotIn('S3cr3t',repr(args)); self.assertNotIn('testuser',repr(args))
        self.assertEqual(args,['/approved/node','/approved/zowe/lib/main.js','zosmf','check','status','--response-format-json','--reject-unauthorized','true'])
        self.assertEqual(env['ZOWE_OPT_PASSWORD'],'S3cr3t;quoted')
        self.assertEqual(env['ZOWE_OPT_REJECT_UNAUTHORIZED'],'true')
        self.assertNotIn('DB2_PASSWORD',env); self.assertNotIn('NODE_TLS_REJECT_UNAUTHORIZED',env)
    def test_driver_error_does_not_reveal_output(self):
        m=self.module(); runner=Mock(return_value=type('R',(),{'returncode':1,'stdout':'SECRET','stderr':'SECRET'})())
        result=m.check({'host':'host','port':443,'user':'u','password':'SECRET','certificate':'/a','node':'/node','cli_js':'/zowe/lib/main.js'},runner=runner)
        self.assertEqual(result,{'ok':False,'code':'ZOWE_CHECK_FAILED'})
        self.assertNotIn('SECRET',repr(result))
    def test_success_is_only_connection_check(self):
        m=self.module(); runner=Mock(return_value=type('R',(),{'returncode':0})())
        self.assertEqual(m.check({'host':'host','port':443,'user':'u','password':'p','certificate':'/a','node':'/node','cli_js':'/zowe/lib/main.js'},runner=runner),{'ok':True,'code':'ZOSMF_STATUS_SUCCEEDED','scope':'connection_status_only'})
    def test_timeout_redacted(self):
        m=self.module(); import subprocess
        runner=Mock(side_effect=subprocess.TimeoutExpired('SECRET',30,output='SECRET'))
        self.assertEqual(m.check({'host':'host','port':443,'user':'u','password':'p','certificate':'/a','node':'/node','cli_js':'/zowe/lib/main.js'},runner=runner),{'ok':False,'code':'ZOWE_TIMEOUT'})
    def test_invalid_values(self):
        m=self.module()
        for value in ['','host;evil','https://host','host\nother','-host','host/path']:
            with self.subTest(value=value): self.assertFalse(m.valid_host(value))
        self.assertTrue(m.valid_host('zosmf.example.com'))
        self.assertFalse(m.valid_port('0')); self.assertFalse(m.valid_port('65536')); self.assertFalse(m.valid_port('443;evil'))
        self.assertTrue(m.valid_port('443'))
if __name__=='__main__': unittest.main()

class ConfigBoundary(Contract):
    def setUp(self):
        import tempfile,json,os
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'certs').mkdir(); (self.root/'approved/zowe/lib').mkdir(parents=True)
        self.node=self.root/'approved'/('node.exe' if os.name=='nt' else 'node'); self.node.write_text('test fixture never executed')
        self.js=self.root/'approved/zowe/lib/main.js'; self.js.write_text('// test fixture never executed')
        (self.js.parent.parent/'package.json').write_text(json.dumps({'name':'@zowe/cli','bin':{'zowe':'./lib/main.js'}}))
        public_ca=HERE.parent/'db2_zos_mcp/tests/fixtures/test-only-ca.pem'
        (self.root/'certs/zosmf-ca.cer').write_bytes(public_ca.read_bytes())
        self.values={'ZOWE_HOST':'zosmf.example.com','ZOWE_PORT':'443','ZOWE_USERNAME':'user','ZOWE_PASSWORD':'private-secret', 'ZOWE_CA_CERTIFICATE':'certs/zosmf-ca.cer','ZOWE_NODE_EXECUTABLE':str(self.node),'ZOWE_CLI_JS':str(self.js)}
    def write(self,**changes):
        vals={**self.values,**changes}
        (self.root/'.env').write_text('\n'.join(k+"='"+v.replace("'","\\'")+"'" for k,v in vals.items()))
    def test_file_only_credentials_no_interpolation(self):
        from unittest.mock import patch
        import os
        m=self.module();self.write(ZOWE_PASSWORD='${HOME}#;literal')
        with patch.dict(os.environ,{'ZOWE_PASSWORD':'ambient-secret','DB2_PASSWORD':'never-copy'}):
            cfg=m.read_configuration(self.root)
        self.assertEqual(cfg['password'],'${HOME}#;literal')
        args,env=m.build_command(cfg,{'PATH':'/malicious','NODE_OPTIONS':'--require /evil','NODE_PATH':'/evil'})
        self.assertNotIn('/malicious',env['PATH']);self.assertNotIn('NODE_OPTIONS',env);self.assertNotIn('NODE_PATH',env)
        self.assertEqual(env['ZOWE_APP_LOG_LEVEL'],'OFF')
    def test_duplicate_and_malformed_env_refused(self):
        m=self.module()
        for extra in ["\nZOWE_HOST='other'", "\nBROKEN='unterminated"]:
            self.write();path=self.root/'.env';path.write_text(path.read_text()+extra)
            with self.assertRaises(m.ConfigurationError):m.read_configuration(self.root)
    def test_bad_fields_and_shim_refused(self):
        m=self.module()
        for k,v in [('ZOWE_HOST','bad;other'),('ZOWE_PORT','0'),('ZOWE_PASSWORD',''),('ZOWE_PASSWORD','p\nq'),('ZOWE_NODE_EXECUTABLE','zowe.cmd'),('ZOWE_CLI_JS','main.js'),('ZOWE_CA_CERTIFICATE','../outside.cer')]:
            self.write(**{k:v})
            with self.subTest(key=k), self.assertRaises(m.ConfigurationError) as ctx:m.read_configuration(self.root)
            self.assertNotIn('private-secret',str(ctx.exception))
    def test_bad_ca_or_private_key_refused(self):
        m=self.module();self.write()
        for data in [b'bad DER',b'-----BEGIN PRIVATE KEY-----',b'-----BEGIN CERTIFICATE-----\nnot-valid\n-----END CERTIFICATE-----']:
            (self.root/'certs/zosmf-ca.cer').write_bytes(data)
            with self.assertRaises(m.ConfigurationError):m.read_configuration(self.root)
    def test_wrong_package_refused(self):
        m=self.module();self.write(); (self.js.parent.parent/'package.json').write_text('{"name":"not-zowe","bin":{"zowe":"./lib/main.js"}}')
        with self.assertRaises(m.ConfigurationError):m.read_configuration(self.root)
    def test_env_symlink_refused(self):
        m=self.module();self.write();path=self.root/'.env';path.rename(self.root/'other.env')
        try:path.symlink_to(self.root/'other.env')
        except OSError:self.skipTest('OS does not permit creating symlinks for this account')
        with self.assertRaises(m.ConfigurationError):m.read_configuration(self.root)
