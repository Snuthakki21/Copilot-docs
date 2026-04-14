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
