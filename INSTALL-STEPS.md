# How to Use These Prompts with GitHub Copilot in VS Code

You have **two files** on this machine:

1. `copilot-instructions.md` — The system prompt (always-on rules for Copilot).
2. `remediation-prompt.md` — The task prompt (paste into chat to start the run).

Follow these steps on your **work laptop**, inside the repo that contains the synthetic data generator.

---

## STEP 1 — Copy both files to a USB stick / OneDrive / email to yourself

You need both files available on your work laptop.

Files to copy:
- `C:\Users\highg\OneDrive\Desktop\AI Lalithya\copilot-instructions.md`
- `C:\Users\highg\OneDrive\Desktop\AI Lalithya\remediation-prompt.md`

---

## STEP 2 — On the work laptop: place `copilot-instructions.md` in the repo

1. Open File Explorer.
2. Navigate to your synthetic data generator repo root (the folder that contains `.git`).
3. If a folder named `.github` does **not** exist at the repo root, **create it**.
   - Right-click → New → Folder → name it exactly `.github` (with the leading dot).
4. Drop `copilot-instructions.md` into `.github\`.

**Final path must be:** `<repo-root>\.github\copilot-instructions.md`

> GitHub Copilot automatically reads this file and applies it to every chat in that workspace. You don't need to do anything else to "install" it.

---

## STEP 3 — Verify VS Code is set up for custom instructions

1. Open VS Code.
2. Open the repo folder (File → Open Folder → pick your repo root).
3. Press `Ctrl + ,` to open Settings.
4. In the search box, type: `copilot instruction`
5. Make sure this setting is **checked/enabled**:
   - **GitHub › Copilot › Chat › Code Generation: Use Instruction Files** — ✅ ON
   - (It's usually on by default. If not, tick the box.)

> If you don't see this setting, update the GitHub Copilot Chat extension to the latest version (Extensions panel → GitHub Copilot Chat → Update).

---

## STEP 4 — Open Copilot Chat and start a new thread

1. In VS Code, press `Ctrl + Alt + I` (or click the Copilot Chat icon in the left sidebar).
2. In the chat panel, click the **"+"** (New Chat) button at the top to start a **fresh thread**.
3. Pick the **Agent mode** dropdown (usually labeled "Ask" / "Edit" / "Agent") and select **Agent**.
   - Agent mode lets Copilot read files, run commands, and edit across the repo. You need this.
4. In the model picker at the bottom of the chat panel, select **GPT-4.1**. Do NOT use GPT-4o, Haiku, or GPT-5 nano — those will collapse on this prompt's length.

> **GPT-4.1 note:** GPT-4.1 is stricter about literal instructions and may hand back early or occasionally skip the TEST-RUN step. The continuation prompts in STEP 6 and the troubleshooting table at the end of this file are built to catch these failure modes. Keep them open in a second window.

---

## STEP 5 — Paste the remediation prompt and send

1. Open `remediation-prompt.md` in any text editor.
2. Select **all** content (`Ctrl + A`), copy (`Ctrl + C`).
3. Paste it into the Copilot Chat input box (`Ctrl + V`).
4. Press **Enter** (or click Send).

Copilot will now:
- Read `.github/copilot-instructions.md` automatically (rules are applied).
- Execute the 8-step protocol.
- Run discovery, build test scaffolds, iterate rows #1–#35, run gates, clean up dead files, and emit the final report.

---

## WHILE IT RUNS

- Copilot will ask permission before running terminal commands or editing files — click **Allow** each time, or tick **"Always allow for this workspace"** once if you trust it to run the full loop unattended.
- If it stalls or loses context, use one of the STEP 6 continuation prompts below.

---

## STEP 6 — GPT-4.1 Continuation Prompts (copy these into a sticky note)

GPT-4.1 has five predictable failure modes. Here are the one-line fixes — paste the matching prompt back into the same chat thread:

1. **Early stop / waiting for user:**
   > `Continue. Do not yield until all 35 rows + 21 gates + Output Contract are done. You are an autonomous agent.`

2. **Claimed `[PASS]` without showing the pytest output:**
   > `Show the exact pytest command and the green output line for test_req_<n>. If you cannot paste it, change the row to [FAIL].`

3. **Describing instead of executing:**
   > `Stop describing. Execute. Use your file-edit and terminal tools now.`

4. **Hallucinated file contents (it described a file it never opened):**
   > `You just described that file without reading it. Call the file-read tool on <path> and paste the first 30 lines. Then redo the step.`

5. **Lost context mid-run:**
   > `Resume from row <n>. Re-read .github/copilot-instructions.md first. Then continue under the 8-step protocol.`

---

## WHEN IT FINISHES

You'll see the **final report** (per the Output Contract section in `copilot-instructions.md`). Every row #1–#35 should read `[PASS|FIXED]` with a cited test id.

If any row reads `[FAIL]`, paste: **"Row #<n> is FAIL. Apply the 8-step protocol to diagnose and fix. Report back only when the test is green."**

---

## QUICK SANITY CHECK (before you trust the final report)

Run these manually in the VS Code terminal:

```powershell
# 1. All tests pass
pytest -q

# 2. Coverage files exist
dir coverage_report.html coverage_report.csv coverage_report.json

# 3. No RAG toggles left
findstr /S /I "use_rag enable_rag rag_enabled RAG_ENABLED" *.py

# 4. Determinism: two runs with same seed match
# (Copilot should have already verified this in GATE 9)
```

If any sanity check fails, feed the exact failing output back to Copilot and it will loop.

---

## TROUBLESHOOTING — GPT-4.1-Specific Failure Modes

Keep this table visible while the run executes. When a symptom appears, paste the matching response back into chat.

| Symptom | Paste this back |
|---|---|
| Says "I would now do X" | `Stop describing. Execute X now with the tool.` |
| Claims `[PASS]`, no pytest output visible | `Paste the pytest command and the green line. Without it, mark the row [FAIL].` |
| Stops at row 10/20/30 with a summary | `That's not the Output Contract. Continue from row <n+1>. All 35 rows are required.` |
| Guessed at xlsx contents | `Open Synthetic Data Generator Rules Inputs.xlsx with the file-read tool. Paste the tab list and headers. Then redo.` |
| Wrote instructions for the user instead of code | `You are the agent. Do it yourself. Use write/edit tools.` |
| Skipped TEST-FIRST step (wrote production code first) | `You wrote production code before a failing test. Revert that edit. Write the failing test first, confirm RED, then re-apply.` |
| Produced a final report with prose / emojis | `The Output Contract forbids prose, emojis, and congratulations. Re-emit the report with only the required lines.` |
| Claims the coverage threshold is 65% without citing the PDF | `Open AI Power Synthetic Data Generation.pdf, search for "coverage" / "threshold". If silent, log the fallback per N4.` |

---

## THAT'S IT

- **File 1** (`copilot-instructions.md`) → goes into `.github\` folder. Never changes.
- **File 2** (`remediation-prompt.md`) → paste into chat to trigger a run. Re-paste any time you want to re-run remediation (e.g., after a merge).
- **STEP 6 + Troubleshooting** → keep visible while GPT-4.1 runs so you can nudge it back on track in one paste.
