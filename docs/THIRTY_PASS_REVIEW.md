# Thirty-area adversarial review — 3 October 2026

The final sweep passed **30 of 30 distinct review areas**, with **246 focused test executions** and no code changes during the sweep. The first sweep ran the same 30 areas, with 29 passes and one failed area (243 executions). Fixes were followed by a complete second sweep: **60 review-pass executions in total**. These are distinct focused checks with some overlapping gates, not 30 complete-suite runs, 30 independent reviewers, or proof of perfection.

## Reproduced findings and fixes

| Finding | Before | Correction and regression evidence |
|---|---|---|
| Hidden Excel scope | Declared dimensions could omit an actual job row or hide row 206. Two regression cases failed. | Validate actual XML row/cell bounds, uniqueness and agreement with the declared range before reading jobs. Both rejected cases and ordinary two-job intake pass. |
| Source accounting cost | Each line re-split the whole source. The bounded split-count test failed. | Reuse original and normalized line arrays; exact original line coverage remains intact. A 6,000-comment local sample decreased from 1.3823 s to 0.006196 s. Timings are illustrative, not a workstation SLA. |
| Encoded XML declarations | Baseline guard accepted UTF-16/32 declarations. | Guard rejects UTF-8/16/32 declaration/entity markers before workbook parsing. |
| Malformed workbook structure | Broken worksheet XML raised an unhandled ParseError. | Known parsing exceptions produce a named, actionable XLSX intake validation error. |

## All 30 areas

The initial/final status below is a test result, not a claim that every conceivable failure in that area was explored. Pass 03 also includes the additional source-accounting and XML regressions found during the review.

| Pass | Focus | Initial | Final | Final tests |
|---|---|---|---|---|
| 01 | Setup installation failures | PASS | PASS | 6 |
| 02 | Manifest row loss and identity collisions | PASS | PASS | 11 |
| 03 | Forged Excel dimensions and hidden scope | FAIL | PASS | 6 |
| 04 | Portable paths and enforced folder ownership | PASS | PASS | 17 |
| 05 | Offline preflight and resource bounds | PASS | PASS | 22 |
| 06 | Complete export and selected inventory | PASS | PASS | 2 |
| 07 | Structural mainframe file classification | PASS | PASS | 14 |
| 08 | Knowledge provenance and immutable snapshots | PASS | PASS | 7 |
| 09 | COPY closure and ambiguity | PASS | PASS | 3 |
| 10 | JCL grammar and ordered source reconciliation | PASS | PASS | 3 |
| 11 | Standard and custom utility contracts | PASS | PASS | 15 |
| 12 | COBOL storage and division lifetime | PASS | PASS | 2 |
| 13 | Statement boundaries and unsupported syntax | PASS | PASS | 4 |
| 14 | Numeric limits and fixed-width string semantics | PASS | PASS | 4 |
| 15 | Decision precedence and sequential effects | PASS | PASS | 2 |
| 16 | Synthetic witnesses and case-budget gaps | PASS | PASS | 2 |
| 17 | Independent expectations and forged oracles | PASS | PASS | 1 |
| 18 | Exported target input and executable capabilities | PASS | PASS | 11 |
| 19 | Every-rule mutations and masked effects | PASS | PASS | 2 |
| 20 | Job dispatch, record propagation and tampered templates | PASS | PASS | 3 |
| 21 | SME workbook identity and complete context | PASS | PASS | 12 |
| 22 | Single human return and deterministic agent continuation | PASS | PASS | 14 |
| 23 | Crash recovery, controls and retry limits | PASS | PASS | 26 |
| 24 | Full source coverage and revoked conversion credit | PASS | PASS | 17 |
| 25 | Target SQLite evidence and cancelled execution | PASS | PASS | 2 |
| 26 | MCP protocol, sessions and paginated discovery | PASS | PASS | 10 |
| 27 | Read-only gateway and SQL boundaries | PASS | PASS | 6 |
| 28 | LLM consent, usage and suggestion authority | PASS | PASS | 2 |
| 29 | Metrics, scope, report acceptance and PPT | PASS | PASS | 11 |
| 30 | Production HTTP workflow and visible UI contracts | PASS | PASS | 9 |

## Evidence and repeatability

[review-iterations.json](review-iterations.json) records every test selector, result, count, elapsed time and log SHA256, initial/final code fingerprints, reproduced findings and benchmark receipts. Private logs remain under `.implementation/tmp/`, outside the published tree. Code fingerprints cover implementation, tests, tools, scripts, knowledge and frontend source. They do not replace signed attestations or independently observed mainframe outputs.

Run from the repository using the locked Python environment:

```sh
PYTHONPATH=. python tools/review_iterations.py
python -m unittest discover -s tests -v
python -m workbench.layout --workspace .
```

The harness clears inherited `WB_` settings, uses local fictional fixtures, bounds each pass to 180 seconds, refuses to overwrite review evidence, and exits unsuccessfully if a pass fails or code changes during the run. This is an engineering check; normal process automation still uses the existing coordinator, single genuine SME return and per-process verification/report gates.

## Acceptance boundaries

Full source coverage tests include every exported file and original line, explicit scope, exact target mappings, uncovered behavior and integrity-based removal of conversion credit. A mainframe-specific omission requires documented verified replacement evidence; unknown or unsupported behavior remains blocked. Passing local fixtures does not prove observed legacy parity.

The workbench still implements the bounded flat LINKAGE record POC. General SQL/CICS, native dataset encodings/I/O, complex control flow, scheduler behavior and custom utilities require audited adapters. Read-only live Zowe/Db2/LLM sessions, native Windows/PowerShell, browser interaction and native PowerPoint remain unverified here. A single SME packet cannot guarantee resolution of all unknown business facts. No source writes, legacy execution or synthetic uploads occurred.

See [../VALIDATION.md](../VALIDATION.md) for the final full-suite and build receipts, and [OPERATIONS.md](OPERATIONS.md) for required setup and remediation.
