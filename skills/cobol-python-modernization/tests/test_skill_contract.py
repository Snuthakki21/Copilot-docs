import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_skill_declares_fail_closed_and_required_references(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for token in ["Use when", "fail closed", "traceability.json", "validation_report.md", "run.jil", "Ponytail v4.9.0", "80%", "SQLite", "Oracle"]:
            self.assertIn(token, text)

    def test_output_contract_names_required_job_artifacts(self):
        text = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
        for token in ["lineage.md", "job.py", "run.jil", "oracle.sql", "sqlite.sql", "tests/test_job.py"]:
            self.assertIn(token, text)

    def test_invocation_prompt_is_self_contained(self):
        text = (ROOT / "PROMPT.md").read_text(encoding="utf-8")
        for token in ["Excel", "branch", "job", "COBOL", "JCL", "DB2", "100%"]:
            self.assertIn(token, text)

    def test_python_documentation_contract_is_explicit(self):
        text = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
        for token in ["plain English", "Purpose:", "Inputs:", "Outputs:", "Side effects:", "Failure behavior:", "Rule IDs:"]:
            self.assertIn(token, text)

    def test_skill_requires_behavioral_preservation_even_for_suspicious_logic(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        for token in ["behavioral preservation", "including defects", "do not correct", "source behavior", "quirk"]:
            self.assertIn(token, text)

    def test_prompt_prohibits_logic_correction_during_migration(self):
        text = (ROOT / "PROMPT.md").read_text(encoding="utf-8").lower()
        for token in ["do not fix", "incorrect", "quirks", "mirror", "source behavior"]:
            self.assertIn(token, text)

    def test_output_contract_separates_suspicious_behavior_from_migration_changes(self):
        text = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8").lower()
        self.assertIn("observed legacy behavior", text)
        self.assertIn("do not change", text)
        self.assertIn("suspicious", text)

    def test_validation_report_requires_side_by_side_plain_english_parity(self):
        text = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
        for token in ["Rule Parity Matrix", "Source code evidence", "Source behavior — plain English", "Python code evidence", "Python behavior — plain English", "Parity result", "Exact discrepancy", "Root cause", "Required remediation", "Revalidation required", "UNKNOWN — UNVERIFIED"]:
            self.assertIn(token, text)

    def test_review_requires_evidence_only_and_no_unsupported_claims(self):
        text = (ROOT / "references" / "adversarial-review.md").read_text(encoding="utf-8")
        for token in ["evidence only", "UNKNOWN — UNVERIFIED", "unsupported_claims", "Never fill an evidence gap"]:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
