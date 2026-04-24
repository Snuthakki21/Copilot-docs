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
4. Confirm the model is **Claude (Sonnet 4 or higher)** or **GPT-4.1** in the model picker — do not run this on a smaller model.

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
- If it stalls or loses context, paste this follow-up: **"Continue from where you left off. Stay under the 8-step protocol. Evidence or nothing."**
- If you want to stop and ask it to report progress so far: **"Emit the Output Contract for all completed rows. Do not skip the evidence column."**

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

## THAT'S IT

- **File 1** (`copilot-instructions.md`) → goes into `.github\` folder. Never changes.
- **File 2** (`remediation-prompt.md`) → paste into chat to trigger a run. Re-paste any time you want to re-run remediation (e.g., after a merge).
