# Copilot-docs

Both files are ready and tested. Here's exactly how to use them:

**Step 1 — Drop `copilot-instructions.md` into your repo's `.github/` folder.** Copilot Chat reads this automatically and will now follow proper Word doc formatting rules in every conversation.

**Step 2 — Copy `docgen.js` into any project where you need to generate a doc.** Then run once:
```bash
npm install docx
```

**Step 3 — To generate a document:** Edit only the `CONFIG` block at the top and the `content` array in the middle. Add a comment describing what you want, and Copilot will autocomplete the sections for you. Then:
```bash
node docgen.js
# → outputs output.docx
```

The script includes ready-made helpers (`h1()`, `h2()`, `p()`, `bullet()`, `table()`, etc.) so Copilot has clean building blocks to work with rather than generating raw docx boilerplate from scratch — that's what was making it produce bad output before.

[View example output.docx](computer://C%3A%5CUsers%5Chighg%5CAppData%5CRoaming%5CClaude%5Clocal-agent-mode-sessions%5C71c693a2-1cf1-4fb0-845f-831e3e42983f%5Cfb6e76cb-a8c9-4fd3-af0c-1b808d2d9aa2%5Clocal_51e29465-0c68-4eb8-a1ff-2559bdf4a6fa%5Coutputs%5Coutput.docx)
[View docgen.js](computer://C%3A%5CUsers%5Chighg%5CAppData%5CRoaming%5CClaude%5Clocal-agent-mode-sessions%5C71c693a2-1cf1-4fb0-845f-831e3e42983f%5Cfb6e76cb-a8c9-4fd3-af0c-1b808d2d9aa2%5Clocal_51e29465-0c68-4eb8-a1ff-2559bdf4a6fa%5Coutputs%5Cdocgen.js)
[View copilot-instructions.md](computer://C%3A%5CUsers%5Chighg%5CAppData%5CRoaming%5CClaude%5Clocal-agent-mode-sessions%5C71c693a2-1cf1-4fb0-845f-831e3e42983f%5Cfb6e76cb-a8c9-4fd3-af0c-1b808d2d9aa2%5Clocal_51e29465-0c68-4eb8-a1ff-2559bdf4a6fa%5Coutputs%5Ccopilot-instructions.md)
