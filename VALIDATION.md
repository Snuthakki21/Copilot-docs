# Validation evidence

## Additional mainframe knowledge and setup revision — 3 October 2026

- Full fresh regression: **242 tests passed in 55.031 seconds**, including the
  production Uvicorn HTTP workflow, automatic continuation through PPT,
  all source/coverage integrity gates and setup-script failure handling.
- Catalog: **17 classifications, 17 utility families, 11 semantic topics**;
  standard/custom schema validation, extensionless/conflicting members,
  source-only utility calls, national-character names and immutable knowledge
  replay are tested. Custom facts appear in the one SME packet; optional LLM
  context is bounded and explicitly unverified.
- Independent review: 94 focused tests passed after reproducing and fixing
  intake row loss, job identity collisions, selected/discovered portfolio
  confusion, missing utility context and direct target input validation.
  Additional review closed the 100,000-line aggregate resource bound.
  A final independent pass ran **80 control/recovery/catalog/preflight/target
  tests in 13.378 seconds** and found no release-blocking issue in those changes.
- Generated version 2 targets reject malformed records themselves. Tests call
  the exported function on invalid containers, missing/extra fields, wrong
  types, booleans, numeric overflow and incorrect widths. Each validation guard
  receives an adversarial mutation. Historical version 1 emitter, fixture and
  mutation evidence hashes remain unchanged.
- A real HTTP deadline failure was reproduced after the extra guards. Code is
  now checked/compiled once per suite and separately per mutant; every record
  still executes, with the same cancellation checkpoint frequency. Durable
  control reads avoid materializing the full evidence document. The original
  HTTP deadline passes without increasing it or dropping tests.
- Fresh fictional two-process run: both **COMPLETED**, **256 cases each**, one
  selected program/copybook version, two memberships, two completed fixture
  processes, guarded Python and inspected six-slide PPT reports. These remain
  fictional source-derived receipts, never actual SME or legacy-run evidence.
- Frontend TypeScript and rebuilt bundle pass. Knowledge/Setup component server
  rendering, escaped custom text, current versus frozen catalog and API contracts
  were checked. Offline preflight returns local **READY**, conversion
  **UNVERIFIED**, zero network requests; workspace layout and diff checks pass.
- Native workstation, browser, PowerPoint and live connector limitations below
  still apply. The catalog documents missing semantic adapters; it does not add
  general-purpose COBOL/JCL/CICS/Db2 conversion support.

The checked-in `examples/processes/example-reuse/` is the immutable earlier
version 1 fixture and remains unchanged. Running `tools/demo_e2e.py` in a fresh
workspace exercises the current version 2 contract and freezes the catalog.
See [docs/OPERATIONS.md](docs/OPERATIONS.md) for required inputs and failure handling,
and [knowledge/README.md](knowledge/README.md) for the editable application catalog.

## Earlier foundation revision evidence

Validated on 3 October 2026 in a clean CPython 3.12.14 environment with the complete hash lock and Node 24.19.0. The public tree contains implementation, built React assets and explicitly fictional example evidence, with no operational sources, credentials, local dependency copies or runtime ledger.

- `python -m unittest discover -s tests -v`: **153 tests passed in 59.319 seconds** after all semantic/runtime/integrity revisions. Coverage includes full source accountability and tampering, source semantics/oracle/template boundaries, every-rule mutation, quota/review/truncation/crash recovery, transient controls/retries, legacy upgrades, folder gates, read-only MCP/provider fixtures, API validation, metrics and editable PPT.
- Actual **Uvicorn subprocess/lifespan HTTP**: the test starts the production server, creates a fictional process, waits for the packet, imports a fixture-only return, observes automatic verification/report completion, downloads the PPT, checks demo exclusion/second-return refusal and verifies same-workspace lock release after shutdown. Passed independently and in the full suite.
- Frontend `tsc --noEmit` and `node build.mjs`: passed using integrity-checked pinned dependencies; committed bundle rebuilt from current source. File selection uses strict UTF-8 decoding, duplicate/size validation, one-click intake/Start and visible errors.
- Clean `pip --require-hashes --only-binary=:all:` installation: all **21 exact packages / 419 allowed distribution SHA256 hashes** originate from official PyPI metadata. `pip check` passed. Full CPython 3.12 Windows AMD64 wheel set downloaded/hash-verified. Actual shell setup ran twice in a path containing spaces; bootstrap failures and version diagnostics have behavioral tests.
- `tools/demo_e2e.py --root NEW_TEST_WORKSPACE`: two fictional processes reached COMPLETED, **256 synthetic cases each**, one unique source program/copybook version, two memberships and two completed fixture processes. Their automatic Yes returns are **test fixtures only**. All generated deck slides say fictional test fixture.
- `python -m workbench.runner bundle example-reuse --workspace TEST_WORKSPACE`: generated the registered immutable bundle after full artifact/hash checks. Real subprocess CLI tests exercise Start/repeated Start, bounded watch, genuine-shaped return import, report/bundle reuse and rejected changed intake/second returns.
- `python -m workbench.layout --workspace .`: valid. Tests prove UI/core/programmatic operations cannot bypass process categories or root allowlists. Copilot/Claude share one prompt and enforce the folder contract.
- Sample PPT: reopened six editable-table slides, checked canvas bounds/required metric/hash consistency, imported into **Artifact Tool**, rendered and visually inspected all six slides. This is not native PowerPoint execution.
- Independent fresh adversarial review: 85 focused integration tests and 51 final recovery/runner/coverage tests passed. All independently reproduced high/medium findings were closed and rechecked. See `docs/RELEASE_REVIEW.md`.

Sample evidence is grouped under `examples/processes/example-reuse/`; the deck and all source coverage formats are in `reports/report-0001/`, targets in `target/run-0001/`, synthetic expectations/actuals in `synthetic/run-0001/`, and immutable shared Python under `examples/shared/target/python/`. The sample accounts for **3 files / 39 physical lines**, **30 verified applicable lines**, **14 verified applicable semantic units**, **4 verified extracted rules**, with **2 verified platform-replacement lines**. These are bounded synthetic example metrics, not real mainframe inventory.

## Limits of the evidence

Live Zowe/Db2/LLM credentials and real source/baseline outputs were not supplied; only local connector/provider fixtures were exercised. Native Windows/PowerShell and PowerPoint were unavailable. Chromium was obtained with a verified official package digest, but this environment terminated browser launch before page rendering; responsive/browser/accessibility certification is not claimed. The production HTTP flow and React type/build checks do not replace browser interaction tests.

Conversion remains the bounded flat LINKAGE record profile in `docs/MIGRATION_CONTRACT.md`. SQL/CICS, native I/O/encodings, storage lifetime, complex control flow and scheduler semantics require additional audited adapters. Unsupported behavior, missing witnesses, unobserved legacy parity and integrity gaps remain blocked. Source-derived expectations share the extraction parser, so neither the suite nor the deck proves zero defects or every possible legacy input. No mainframe writes, legacy execution or synthetic uploads occurred.
