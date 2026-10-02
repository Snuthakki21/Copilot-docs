import importlib.util
from pathlib import Path
import unittest
class HeadroomEnvironment(unittest.TestCase):
 def mod(self):
  p=Path(__file__).with_name('headroom_stdio.py');self.assertTrue(p.exists(),'isolating launcher missing')
  s=importlib.util.spec_from_file_location('headroom_stdio',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_no_ambient_credentials_or_injection(self):
  m=self.mod(); e=m.safe_environment({'DB2_PASSWORD':'secret','ZOWE_OPT_PASSWORD':'secret','OPENAI_API_KEY':'secret','PYTHONPATH':'bad','NODE_OPTIONS':'bad','PATH':'bad','HOME':'/home/test'})
  for k in ['DB2_PASSWORD','ZOWE_OPT_PASSWORD','OPENAI_API_KEY','PYTHONPATH','NODE_OPTIONS']:self.assertNotIn(k,e)
  self.assertNotIn('bad',e['PATH']);self.assertEqual(e['HEADROOM_BEACON'],'off');self.assertEqual(e['HEADROOM_UPDATE_CHECK'],'off')
 def test_only_existing_official_entrypoint_contract(self):
  m=self.mod();self.assertEqual(m.command_for(Path('/env/headroom')),['/env/headroom','mcp','serve','--transport','stdio'])
if __name__=='__main__':unittest.main()
