import importlib.util
from pathlib import Path
import unittest
class ExtractRules(unittest.TestCase):
 def module(self):
  f=Path(__file__).with_name('extract.py');self.assertTrue(f.exists(),'bounded reader not implemented')
  import sys;sys.path.insert(0,str(f.parent))
  spec=importlib.util.spec_from_file_location('extract',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_valid_dataset_and_member(self):
  m=self.module()
  for v in ['APP.COBOL','APP.COBOL(HELLO)','APP.DATA.D202601']:
   self.assertTrue(m.allowed_dataset(v,['APP']))
 def test_malicious_or_outside_scope(self):
  m=self.module()
  for v in ['OTHER.DATA','APPX.DATA',"APP.DATA';DROP",'APP.DATA\nNEXT','APP.DATA --password p','APP..DATA','APP.DATA(TOOLONG99)','APP.*','APP.DATA;DELETE']:
   self.assertFalse(m.allowed_dataset(v,['APP']),v)
  self.assertFalse(m.allowed_dataset('APP.DATA',[]))
 def test_list_pattern_narrow(self):
  m=self.module()
  self.assertEqual(m.read_arguments('datasets','APP.SRC.*',['APP.SRC']),['zos-files','list','data-set','APP.SRC.*'])
  for v in ['*','APP.*','OTHER.*','APP.SRC.*;x']:
   with self.assertRaises(ValueError):m.read_arguments('datasets',v,['APP.SRC'])
 def test_only_fixed_read_operations(self):
  m=self.module()
  self.assertEqual(m.read_arguments('members','APP.SRC',['APP']),['zos-files','list','all-members','APP.SRC'])
  self.assertEqual(m.read_arguments('view','APP.SRC(MAIN)',['APP']),['zos-files','view','data-set','APP.SRC(MAIN)'])
  for op in ['delete','submit','config','auth','execute']:
   with self.assertRaises(ValueError):m.read_arguments(op,'APP.SRC',['APP'])
if __name__=='__main__':unittest.main()
