import tempfile
import unittest
from pathlib import Path
from pptx import Presentation
import test_workflow
from workbench.reports import metrics

class ReportTests(unittest.TestCase):
    setUp=test_workflow.WorkflowTests.setUp
    create=test_workflow.WorkflowTests.create
    answer=test_workflow.WorkflowTests.answer
    def test_complete_only_after_real_ppt_and_snapshot(self):
        self.create();self.c.start('process-a');self.c.advance('process-a')
        self.c.import_answers('process-a',self.answer(),'Example reviewer')
        self.c.advance('process-a');self.c.advance('process-a')
        doc=self.c.ledger.get('process-a')
        self.assertEqual(doc['status'],'COMPLETED')
        deck=self.c.artifact('process-a','reports/report-0001/management.pptx')
        self.assertEqual(len(Presentation(deck).slides),5)
        m=metrics(self.c.ledger,doc)
        self.assertEqual(m['source_programs'],1)
        self.assertEqual(m['rules_verified'],m['rules_documented'])
        self.assertFalse(m['observed_mainframe_parity'])
        self.assertEqual(len(self.c.ledger.history('process-a')),1)

    def test_uncertainty_does_not_receive_verified_credit(self):
        self.create();self.c.start('process-a');self.c.advance('process-a')
        self.c.import_answers('process-a',self.answer(response='Not sure'),'Example reviewer')
        self.c.advance('process-a');self.c.advance('process-a')
        doc=self.c.ledger.get('process-a')
        self.assertEqual(doc['status'],'COMPLETED_WITH_BLOCKERS')
        self.assertEqual(metrics(self.c.ledger,doc)['rules_verified'],0)

if __name__=='__main__':unittest.main()
