# Mainframe Modernization Workbench

A local, guided POC: provide a process, review one checklist, receive one
executive report. Python/SQLite is the non-production target. Supported flat
COBOL record rules run automatically; other behavior is reported as blocked.

## 1. Install and open

Use CPython **3.12** and a writable folder on your local disk.

- **Windows:** run `./scripts/Setup.ps1`, then `./scripts/Start.ps1` in PowerShell.
- **Linux/macOS:** run `bash scripts/setup.sh`, then `.venv/bin/python -m workbench`.

Open **http://127.0.0.1:8765**. Setup installs the locked dependencies. The UI
is included; operators do not need Node. Follow any named setup error before
continuing. Native Windows execution still needs a workstation smoke test.

## 2. Answer six setup questions

The UI guides you through source location, manifest, Zowe, Db2, optional LLM
and reviewer availability. Choose “needs setup” when unsure; it gives the next
action. No passwords are entered in this questionnaire. Configuration does not
mean a live connection has been verified. The guide uses no LLM tokens.

For connections, set private shell variables from `.env.example` **before**
launch. That file is a template, not automatically loaded. You can begin with
local source and no LLM. [Technical reference](docs/TECHNICAL_REFERENCE.md)
contains the exact connection prerequisites and recovery actions.

## 3. Provide your process

Put the complete UTF-8 export in **`Endeavor/`**, or choose source files in the
UI. Keep original relative names. Supply Markdown following
[examples/process-input.md](examples/process-input.md), or download the Excel
intake template in the UI. It names the process, ordered jobs/steps, programs
and input/output groups. Use a new process ID for changed source.

Put background/Devin articles in **`knowledge/inbox/context.md`** (up to 16 KB).
Add custom utility facts to **`knowledge/application-knowledge.json`**, created
by setup. The **Knowledge** screen and [knowledge guide](knowledge/README.md)
explain file classification, utilities, required evidence and editable facts.

## 4. Click Start

The workbench checks the inputs, inventories every source file/line, analyzes
supported rules, generates provisional Python and creates one SME checklist.
The screen shows the current stage and next action. Pause, Resume and Cancel
retain evidence. Mainframe connections remain read-only; no jobs or synthetic
records are run or uploaded there.

## 5. Return the one SME checklist

Download `sme-checklist.xlsx`. The actual reviewer selects **Yes**, **No** or
**Not sure**, adds corrections and returns it. Import the workbook with their
name. Agents must never fill these answers. The workbench automatically runs
source-derived synthetic tests, comparisons, adversarial checks and reporting.
Unresolved answers remain blockers; it does not issue another questionnaire.

## 6. Open the executive report

One primary report shows before/after counts, verified coverage, gaps and next
actions. The six-slide PowerPoint and detailed source/target/test evidence are
available when requested. **Completed with blockers** means unresolved work.
Passing local tests does not establish observed mainframe parity.

For the current software's results, open [executive-report.html](docs/executive-report.html).

## Use Copilot or Claude Code

Give the agent **[prompts/START_MODERNIZATION.md](prompts/START_MODERNIZATION.md)**,
your manifest path and workspace path, then say Start. Repository instructions
point to that one workflow. The agent uses the same engine as the UI and waits
for the actual human checklist return. Stop the UI before running the CLI on
the same workspace. Folder checks keep output under each process.

For a safe trial, use **Run fictional example** in the UI. Its results are
excluded from real portfolio totals. No real process has been converted in the
software validation supplied with this repository.
