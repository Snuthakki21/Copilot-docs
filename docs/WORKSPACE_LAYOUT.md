# Workspace and repository organization

The agent entrypoints [AGENTS.md](../AGENTS.md) and [CLAUDE.md](../CLAUDE.md) both
reference [prompts/START_MODERNIZATION.md](../prompts/START_MODERNIZATION.md).
[.github/copilot-instructions.md](../.github/copilot-instructions.md) gives
Copilot its recognized repository-wide entrypoint to those same instructions.
The CLI and HTTP UI use the same persistent Coordinator and single-writer
ledger. Validate placement before intake and after work:

```sh
python -m workbench.layout --workspace WORKSPACE
```

The validator reports all found placement problems and exits 2 on failure. It
does not reorganize or rewrite evidence, inspect secrets, or follow symlinks.
The CLI refuses intake/continuation when placement is invalid. Programmatic
writers can use `workbench.layout.output_path(root, process_id, relative)` to
reject escapes, sibling process writes and misplaced output before writing.

| Location | Contents and ownership |
|---|---|
| `Endeavor/` | Selected read-only local mainframe text export. Never execute or overwrite it. |
| `process-input.md`, `intake-template.xlsx` | Optional root intake inputs. `--manifest` may explicitly select a Markdown manifest elsewhere. |
| `processes/PROCESS_ID/input/process-input.md` | Immutable manifest snapshot; supplied and snapshot bytes must match the ledger's creation-time manifest SHA-256. |
| `processes/PROCESS_ID/input/sources/` | Immutable source snapshot with recorded file hashes. Preserve original relative names. |
| `processes/PROCESS_ID/input/sme-return-inbox.xlsx` | The single designated automatic return inbox. Requires explicit actual `--reviewer` attribution. |
| `processes/PROCESS_ID/input/sme-return.xlsx` | Service-preserved accepted return. Never place a workbook here manually. |
| `processes/PROCESS_ID/analysis/` | Structured analysis and source accounting, including reasons for unknown/unsupported/omitted lines. |
| `processes/PROCESS_ID/analysis/mainframe-knowledge.json` | Immutable standard/application knowledge snapshot used for that process; validated against its creation-time hash. |
| `processes/PROCESS_ID/review/` | Frozen `packet.json` and the one `sme-checklist.xlsx`, `.docx`, `.html`. |
| `processes/PROCESS_ID/synthetic/run-NNNN/` | Versioned source-derived expected outputs, actual results and comparisons. |
| `processes/PROCESS_ID/target/run-NNNN/` | Versioned generated programs, job orchestration and local target database. |
| `processes/PROCESS_ID/reports/report-NNNN/` | Immutable inspected metrics, coverage/accountability files, comparison summaries and management PowerPoint. |
| `processes/PROCESS_ID/reports/bundle-HASH.zip` | Registered immutable bundle, fingerprinted from its entries and reused on repeated bundle. |
| `processes/PROCESS_ID/tests/` | Process-specific structured regression evidence. Repository test implementations stay in `tests/`. |
| `shared/target/python/HASH.py` | Content-addressed shared target versions. A version is never replaced in place. |
| `knowledge/inbox/context.md` | Optional bounded unverified background; never approval or verification. |
| `knowledge/mainframe-catalog.json`, `knowledge/README.md` | Versioned standard classifications, utilities, native-semantic checklist and official references. |
| `knowledge/application-knowledge.json` | Editable private application/vendor utility knowledge, initialized from `examples/application-knowledge.json`; future intakes freeze edits. |
| `knowledge/records.json`, `knowledge/INDEX.md` | Canonical provenance-bound SME-confirmed interpretations and one compact index; target verification is separate. |
| `workbench/`, `frontend/`, `tests/`, `tools/`, `scripts/`, `docs/`, `prompts/`, `examples/`, `.github/` | Repository implementation, verification, entrypoints, instructions, synthetic examples and GitHub/Copilot metadata. |

Process IDs are stable, validated identifiers beginning with a letter. Process
roots may contain only `input`, `analysis`, `review`, `synthetic`, `target`,
`reports`, `tests`. Root-level process files, miscellaneous process folders,
path traversal and symlinks are refused. Generated Python/database artifacts
belong in `target` or `tests`, not analysis/review/input. Input allows only the
manifest, source snapshot and two designated return paths. Use structured
coverage records; never create a Markdown file per rule or per source line.
The only process Markdown is the input manifest or an original source-export
Markdown file preserved under `input/sources`.

Root files are allowlisted: `.env`, `.env.example`, `.gitignore`, `.gitattributes`, `AGENTS.md`,
`CLAUDE.md`, `README.md`, `START_HERE.md`, `VALIDATION.md`, `requirements.lock`,
`requirements.txt`, `pyproject.toml`, `process-input.md`, `intake-template.xlsx`.
Put new documentation in `docs/` and new prompts in `prompts/`; deliberately
update the validator and this contract if another root file is needed.

Private/local paths are `.env`, `.migration/`, `.implementation/`,
`.superpowers/`, `release-private/`, `.venv/`, `node_modules/`, `__pycache__/`,
and `.implementation/tmp/` scratch. Root directories beginning with `tmp` are
refused; an ignored name does not authorize misplaced process output.
`.git/` is repository metadata.
The existing ignore policy also excludes operational `Endeavor/`, `processes/`,
`shared/`, generated knowledge and `knowledge/inbox/`. Keep these exclusions;
only synthetic `examples/Endeavor/`, `examples/processes/` and `examples/shared/` evidence is intentionally tracked. Do not read or
publish secrets/private diagnostics as an artifact. The validator checks root
placement without reading any private contents.

Existing runs are never cleaned up to improve their status. Repeated Start
with the same process ID/recorded manifest hash reuses its current state and packet.
Changing both the supplied manifest and snapshot cannot change that baseline.
Bundle validates the snapshot against the ledger baseline even for terminal
runs. Historical runs missing the baseline fail closed; Resume never silently
pins whatever bytes currently exist.
Resume is explicit for paused/failed stages. The one accepted SME return is
identified by hash; neither a retry nor an inbox change creates another quota.
Publishable deliverables are generated report/bundle paths, with blockers and
the source-derived evidence boundary clearly stated.

GitHub's official documentation identifies `.github/copilot-instructions.md`
as repository-wide instructions and lists which environments support agent
`AGENTS.md`/`CLAUDE.md` instructions. Keep repository-wide instructions enabled
in the chosen Copilot environment; confirm the file appears in a response's
References list or in Copilot CLI `/instructions`. Instruction discovery guides
the agent; Coordinator validation enforces the actual write boundary.

References (verified 2026-10-03):

- [Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
- [Instruction support by environment](https://docs.github.com/en/copilot/reference/custom-instructions-support)
- [Copilot CLI instruction discovery](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
