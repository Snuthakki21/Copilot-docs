# COBOL Python Modernization Skill

Devin-compatible layout mirrors the plugin/skill convention used by Ponytail v4.9.0.

```text
Copilot-docs/
  .devin-plugin/
    plugin.json
  skills/
    cobol-python-modernization/
      SKILL.md
      PROMPT.md
      README.md
      scripts/
        __init__.py
        modernization_tools.py
      references/
        output-contract.md
        adversarial-review.md
        mainframe-edge-cases.md
      tests/
        test_tooling.py
        test_skill_contract.py
```

From a repository checkout, Devin can use the root plugin structure when installed as a plugin; the skill itself is `skills/cobol-python-modernization/SKILL.md`. Copy `PROMPT.md`, fill in repository/branch/Excel/output-root values, and attach the workbook.

The helper requires `openpyxl` for `.xlsx` input; install it from the organization's approved Artifactory/package index. It uses read-only, values-only workbook access. Generated jobs remain stdlib-first (`sqlite3`, `csv`, `decimal`, `pathlib`, etc.) unless discovered semantics justify an approved dependency.

The governing migration rule is behavioral preservation: generated Python mirrors proven source behavior exactly, including legacy defects and quirks. Suspicious source behavior is documented, not repaired. The validator gates required artifacts, source→Python→test traceability, exact source/workbook provenance, structured function documentation, ≥80% Python coverage, and zero unresolved migration/security defects.

Run skill self-tests:

```bash
cd skills/cobol-python-modernization
python -m unittest discover -s tests -v
python -m coverage run -m unittest discover -s tests
python -m coverage report -m scripts/modernization_tools.py
```

Validate a generated job folder:

```bash
python scripts/modernization_tools.py modernized/<JOB_NAME>
```
