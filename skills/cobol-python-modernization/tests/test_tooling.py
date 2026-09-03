import json
import tempfile
import unittest
from pathlib import Path

from scripts.modernization_tools import normalize_headers, safe_job_name, validate_job_artifacts, workbook_rows


class ToolingTests(unittest.TestCase):
    def test_normalize_headers_accepts_common_excel_variants(self):
        headers = ["Job Name", "STEP", "Program", "Input Files", "Outputs"]
        self.assertEqual(
            normalize_headers(headers),
            ["job", "step", "program", "inputs", "outputs"],
        )

    def test_safe_job_name_rejects_path_traversal_and_normalizes(self):
        self.assertEqual(safe_job_name(" AR.DAILY-01 "), "AR.DAILY-01")
        with self.assertRaises(ValueError):
            safe_job_name("../escape")

    def test_validator_fails_closed_when_required_artifact_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "traceability.json").write_text(json.dumps({"rules": []}))
            result = validate_job_artifacts(root)
            self.assertFalse(result["passed"])
            self.assertIn("lineage.md", "\n".join(result["errors"]))

    def test_validator_requires_every_source_rule_to_have_python_and_test_trace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ["lineage.md", "job.py", "run.jil", "oracle.sql", "sqlite.sql", "validation_report.md"]:
                (root / name).write_text("placeholder")
            (root / "tests").mkdir()
            (root / "tests" / "test_job.py").write_text("def test_x(): assert True")
            manifest = {
                "rules": [
                    {"id": "R1", "source": "COBOL:P1:100-120", "python": ["job.py:10-20"], "tests": []}
                ],
                "coverage_percent": 90,
                "security_findings": [],
                "defects": [],
                "unresolved": [],
            }
            (root / "traceability.json").write_text(json.dumps(manifest))
            result = validate_job_artifacts(root)
            self.assertFalse(result["passed"])
            self.assertTrue(any("R1" in e for e in result["errors"]))

    def test_validator_accepts_complete_zero_finding_manifest_at_80_percent_or_more(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ["lineage.md", "job.py", "run.jil", "oracle.sql", "sqlite.sql", "validation_report.md"]:
                (root / name).write_text("placeholder")
            (root / "tests").mkdir()
            (root / "tests" / "test_job.py").write_text("def test_x(): assert True")
            manifest = {
                "rules": [
                    {"id": "R1", "source": "JCL:STEP01", "python": ["job.py:10"], "tests": ["tests/test_job.py::test_r1"]}
                ],
                "coverage_percent": 80,
                "security_findings": [],
                "defects": [],
                "unresolved": [],
            }
            (root / "traceability.json").write_text(json.dumps(manifest))
            result = validate_job_artifacts(root)
            self.assertTrue(result["passed"], result)

    def test_workbook_rows_reads_expected_columns_and_skips_blank_rows(self):
        from openpyxl import Workbook
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "jobs.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.append(["Jobs", "Steps", "Programs", "Input Files", "Outputs"])
            ws.append(["JOB1", "STEP1", "PGM1", "IN1", "OUT1"])
            ws.append([None, None, None, None, None])
            wb.save(path)
            rows = workbook_rows(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["job"], "JOB1")
            self.assertEqual(rows[0]["program"], "PGM1")

    def test_workbook_rows_rejects_missing_required_columns(self):
        from openpyxl import Workbook
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "jobs.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.append(["Job", "Step", "Program"])
            ws.append(["JOB1", "STEP1", "PGM1"])
            wb.save(path)
            with self.assertRaisesRegex(ValueError, "missing required Excel columns"):
                workbook_rows(path)

    def test_workbook_rows_empty_sheet_returns_empty_list(self):
        from openpyxl import Workbook
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "jobs.xlsx"
            wb = Workbook()
            wb.save(path)
            self.assertEqual(workbook_rows(path), [])

    def test_validator_rejects_invalid_json_and_empty_rules(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "traceability.json").write_text("not json")
            result = validate_job_artifacts(root)
            self.assertFalse(result["passed"])
            self.assertTrue(any("invalid traceability.json" in e for e in result["errors"]))

    def test_validator_rejects_rule_without_source_and_low_coverage_and_findings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ["lineage.md", "job.py", "run.jil", "oracle.sql", "sqlite.sql", "validation_report.md"]:
                (root / name).write_text("placeholder")
            (root / "tests").mkdir()
            (root / "tests" / "test_job.py").write_text("def test_x(): assert True")
            manifest = {
                "rules": [{"id": "R2", "python": ["job.py:1"], "tests": ["tests/test_job.py::test_r2"]}],
                "coverage_percent": 79.9,
                "security_findings": ["unsafe subprocess"],
                "defects": ["mismatch"],
                "unresolved": ["COPYBOOK missing"],
            }
            (root / "traceability.json").write_text(json.dumps(manifest))
            result = validate_job_artifacts(root)
            text = "\n".join(result["errors"])
            self.assertIn("no source trace", text)
            self.assertIn("below 80%", text)
            self.assertIn("security findings", text)
            self.assertIn("defects", text)
            self.assertIn("unresolved source behavior", text)


if __name__ == "__main__":
    unittest.main()
