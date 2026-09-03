import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_skill_declares_fail_closed_and_required_references(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for token in [
            "Use when",
            "fail closed",
            "traceability.json",
            "validation_report.md",
            "run.jil",
            "Ponytail v4.9.0",
            "80%",
            "SQLite",
            "Oracle",
        ]:
            self.assertIn(token, text)

    def test_output_contract_names_required_job_artifacts(self):
        text = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
        for token in ["lineage.md", "job.py", "run.jil", "oracle.sql", "sqlite.sql", "tests/test_job.py"]:
            self.assertIn(token, text)

    def test_invocation_prompt_is_self_contained(self):
        text = (ROOT / "PROMPT.md").read_text(encoding="utf-8")
        for token in ["Excel", "branch", "job", "COBOL", "JCL", "DB2", "100%"]:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
