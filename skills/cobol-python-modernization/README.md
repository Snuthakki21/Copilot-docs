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

From a repository checkout, Devin can use the root plugin structure when installed as a plugin; the skill itself is `skills/cobol-python-modernization/SKILL.md`. Copy the text from `PROMPT.md`, fill in repository/branch/Excel/output-root values, and attach the workbook in the Devin session.

The only required runtime dependency for the skill helper is `openpyxl` for `.xlsx` input. Install it from the organization's approved Artifactory/package index. The helper uses `read_only=True`, `data_only=True`, and values-only row iteration for low-memory ingestion. Job implementations should remain stdlib-first (`sqlite3`, `csv`, `decimal`, `pathlib`, etc.) unless discovered semantics justify an approved dependency.

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
