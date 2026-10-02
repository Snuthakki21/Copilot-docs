---
name: accessible-interface-review
description: "Use when designing or reviewing modernization screens, stateful UI flows, accessibility and CICS-to-target behavior."
---

# Accessible interface design and review

Read [AGENTS.md](../../../docs/MIGRATION_CONTRACT.md), sections 3, 4, 7 and 13 as needed. This checklist is original project guidance.

1. Identify the user task, current screen/session/backend contract and existing design system. Avoid choosing a new framework without approval.
2. Map navigation, field validation, submit/cancel/back, keyboard/AID equivalents, authorization and transactional effects. Distinguish evidence-backed parity from proposed changes.
3. Specify layout, semantic controls/labels, focus order/visibility, error association, contrast and non-color feedback. Cover narrow screens and keyboard operation.
4. Include loading, empty, success, invalid, unavailable and permission states, repeated submissions and recovery after interruptions.
5. Present a small coherent design for review. Implement only within approved profile/slice scope; assign UI artifact ownership with Architecture and Application roles.
6. With available authorized browser/test tools, inspect rendered behavior and navigation history; capture actual results. If unavailable, mark visual/interaction checks not run.

Output: flow/state/component specification, acceptance checks, evidence and open design/behavior decisions. Do not claim accessibility certification, install tools, fetch remote assets or copy third-party material automatically. The included [UI/UX Pro Max](../ui-ux-pro-max/SKILL.md) and [Frontend Design](../frontend-design/SKILL.md) adaptations can supplement this original workflow after reading their provenance/limits, without changing approval gates. Use UI/UX Pro Max manual-reference mode if an approved existing Python runtime or script permission is absent.
