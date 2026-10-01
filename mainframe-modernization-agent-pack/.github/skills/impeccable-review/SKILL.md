---
name: impeccable-review
description: "Audit and refine an approved interface using an instruction-only Impeccable-inspired review workflow. Use for UI critique, polish, responsive behavior and accessibility review without installing detectors, hooks or browsers."
---

# Impeccable review, no-runtime subset

Use the existing design system and approved source behavior. This is an adapted review procedure, not the full Impeccable runtime/plugin, browser extension or detector. Never download or run its launcher, install browser tools, activate hooks or assume measurements exist.

Choose one requested mode:
- Audit: identify evidence-backed implementation issues without changing files
- Critique: assess hierarchy, task clarity, density, type, spacing and product-specific coherence
- Polish: make only approved small consistency fixes and recheck their effects
- Harden: examine empty/loading/error/permission/offline/overflow and interrupted-action states

Inspect actual screens/code using existing approved tools. For web interfaces, check semantic labels/headings, keyboard and focus behavior, contrast when measurable, reduced motion, error recovery, responsive overflow/touch use and visible feedback. Native UI needs its own platform criteria, not a claim that web checks establish native compliance.

Separate static-code evidence, observed browser behavior, measurements and design judgment. Do not issue a compliance certificate or invented health score. An unavailable browser/detector is an untested dimension, not a passed check. Report the top three issues first with severity, location, user impact, evidence and proposed remedy. Keep complete findings in the canonical review record.

Preserve CICS transaction/session semantics and approved migration rules. Behavior changes need SME/user decisions. After authorized edits, repeat relevant interaction/visual checks and link code segments/tests. Do not add fonts, animation libraries, services or external assets just for polish.

Adapted from the pinned audit, critique, polish and harden guidance. Removed runtime detectors, package/download instructions, browser setup, global hooks and generic score claims. See SOURCE.md and retained license/notice.
