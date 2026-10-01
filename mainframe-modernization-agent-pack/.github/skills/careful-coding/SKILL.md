---
name: careful-coding
description: "Before editing code, inspect the real behavior, reuse existing solutions and make the smallest correct authorized change. Use for coding, debugging and refactoring while preserving every required migration rule and test."
---

# Careful coding

A scoped, instruction-only Ponytail adaptation plus independently authored engineering checks. It does not install the Ponytail plugin, hooks or persistent modes. Exact source is recorded in SOURCE.md. It does not remove required migration behavior under a minimal-code slogan.

1. Read the requested outcome and affected flow first. State material assumptions and ask about unresolved behavior before implementing it.
2. Look for existing helpers, patterns, standard-library functionality and approved dependencies. Prefer reuse only when semantics, version and tests match; do not create a framework for a single speculative need.
3. Keep the change cohesive, readable and within the approved slice. One-line cleverness, deleting required behavior, or avoiding needed abstraction is not a goal. Do not refactor unrelated code.
4. Trace all relevant callers/consumers and fix the verified cause. Preserve declared interfaces and app/database ownership; changing business behavior returns to approval.
5. Check boundary validation, exact numeric/data handling, failures, security, accessibility and state recovery as relevant. Preserve all mandated tests, fixtures, human reviews and legacy comparisons; no one-line or trivial-change test exemption overrides these gates.
6. Define a verifiable expected result before editing. Run existing authorized tests and inspect the final diff. Report failed/not-run/blocked separately from passed.
7. Record evidence, assumptions and known limits once in canonical state. Reuse prior scoped answers and cache context by source/profile hash instead of repeated whole-repo reads.

The requested Karpathy repository is listed as a reference only because a complete redistribution license was not present at the pinned revision. Its text is not bundled. These general engineering checks are independently worded; no original author endorsement is implied.
