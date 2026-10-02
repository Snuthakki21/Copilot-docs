---
name: migration-implementation-qa
description: "Use when implementing or verifying an explicitly approved mainframe migration slice across application, database and adapters."
---

# Approved implementation and QA

Read [AGENTS.md](../../../docs/MIGRATION_CONTRACT.md), sections 0, 4–7, 9 and 11 as needed.

1. Confirm exact SME spec, approved profile/interface and explicit user slice authorization. Check dependency closure and target capabilities before editing.
2. Establish source-derived expected results and boundary/error tests before code. Record expected legacy behavior and intended changes separately.
3. Keep application, database/schema/data scripts and adapters under explicit ownership. Use the existing project stack and minimal dependencies; no automatic installs.
4. Preserve codecs, numeric operations, null/blank/empty, ordering, transactions, retries, state, errors and restart semantics. Keep one-to-one source occurrence mappings even when helpers are shared.
5. Run available authorized tests in the named environment. Compare matched legacy input/state/results with the actual approved target. Label mocks/reference runs and unrun or blocked checks.
6. Segment all generated code/config/schema/script/test artifacts for human review. Re-run affected tests after changes and reconcile every acceptance gate at current hashes.

Output: artifact and contract hashes, commands/results/diffs, coverage and review mappings, limitations and remaining decisions. A passing test does not grant human approval or deployment permission. This workflow supplies no runtime, ledger code or test runner.
