---
name: migration-evidence-review
description: "Use when deriving mainframe source rules, preparing human review, or checking evidence and approval traceability."
---

# Evidence and human review

Read only the relevant parts of [AGENTS.md](../../../docs/MIGRATION_CONTRACT.md), sections 0–3, 9 and 11.

1. Identify baseline/scope and exact source path, range and content hash. Keep physical file, logical object and runtime occurrence distinct.
2. Retrieve only necessary source plus declarations/dependencies; preserve full evidence outside model context. Mark facts, inference and unknowns separately.
3. Account for every line in a primary segment. Derive atomic rules/utility effects without losing compound logic, ordering, state or consumer identity.
4. Write plain-English cards: condition, action, otherwise, labeled example, exception and evidence. Track observed legacy behavior separately from approved desired behavior.
5. Reuse scoped, version-matching decisions; collect exact human identity/role/decision/version and impacted IDs. SME, architecture, implementation and code review are separate gates.
6. Reopen impacted approvals when hashes or relevant context change. Return changed IDs, gaps and evidence; coordinator owns shared ledger writes.

Output: bounded review packet entries and decision deltas. No invented approvals, source execution, installs, or unrestricted extracts. This file is an instruction workflow, not a parser, review backend or executable script.
