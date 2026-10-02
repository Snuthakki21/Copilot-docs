---
name: frontend-design
description: Plan and refine distinctive, coherent frontend visuals within an existing approved stack and design system while preserving source behavior and accessible interaction.
---

# Frontend Design: repository-native adaptation

Adapted on 2026-10-01 from Anthropic's Apache-2.0-licensed `frontend-design` skill. This is a modified, text-only entrypoint: deployment-specific assumptions are removed and mainframe-parity, approved-stack, no-install, and evidence boundaries are added. See [SOURCE.md](SOURCE.md) and [LICENSE.txt](LICENSE.txt).

## Ground the design in the actual work

Read the brief, existing screens/components/tokens, user workflows, approved stack, and source behavior before choosing aesthetics. If the brief is unclear, ask for the missing decision instead of inventing a business domain, audience, or requirement. Retain established brand rules and interaction conventions unless the user requests a change.

For modernization, preserve field semantics, labels where meaningful, validation, transaction behavior, data formatting/precision, keyboard/PF-key equivalents, authorization, and error/recovery paths. Separate evidence-backed parity requirements from proposed improvements. Do not make a legacy workflow prettier by silently removing needed information or actions.

## Plan, review, build, critique

1. Identify the primary task and information hierarchy. Choose a visual direction specific to the product and its operators. Operational tools may need compact tables and efficient scanning; a marketing hero is not a universal pattern.
2. Propose a small token system using existing approved assets: palette roles, type hierarchy, spacing/density, alignment, and component states. Explain the few choices that materially affect readability or workflow. Preserve existing tokens instead of duplicating them.
3. Review the plan against the brief before coding. Remove decoration and repetitive cards, labels, gradients, or motion that do not communicate meaning. A deliberate familiar pattern is valid when it fits the task; uniqueness is not a requirement that overrides usability or the user's brief.
4. Build within the approved stack and installed dependencies. Check CSS specificity and inheritance so selectors do not silently cancel intended spacing, focus, or state styling.
5. Critique the rendered result with existing tools when available. Inspect relevant small and large viewports, realistic long content, dense data, and empty/loading/error states. Capture evidence when permitted. Say what remains untested.

## Visual and interaction principles

- Typography carries hierarchy: choose existing approved families intentionally, keep roles and scales coherent, and avoid tiny operational text. Readable line length and spacing matter more than novelty.
- Structure communicates meaning: numbering belongs to actual sequences, borders to real grouping, and labels to necessary context. Avoid decorating every region identically.
- Keep one clear visual emphasis per view. Align related controls and data, reserve space for status changes, and make the primary action easy to locate without burying secondary workflows.
- Use motion to explain state changes, sparingly and with reduced-motion support. Immediate updates can be appropriate; do not animate every interaction or add an animation dependency by default.
- Use clear, stable action names, visible field labels, specific errors, and useful recovery instructions. Keep vocabulary consistent from action to confirmation. Never invent metrics, customer claims, or business copy and present it as fact.
- Build visible focus, semantic structure, keyboard interaction, accessible names, contrast, non-color cues, zoom/reflow, and understandable disabled states into the actual components. Verify rather than asserting accessibility from appearance.

## Execution boundaries

This skill has no executable files or plugin dependency. Do not install packages, fonts, icon libraries, browser tools, or extensions; do not add remote fonts/CDNs or change the stack. If an asset or tool is missing, use approved existing assets and report the limitation. UI/UX Pro Max is an optional local companion for reference-based decisions, never a requirement to run scripts. Ask before changing business behavior or making a material design-system departure.

Deliver the implemented or proposed changes, source behavior retained, relevant design rationale, checks actually performed, and remaining uncertainties. Do not call an interface production-ready or parity-complete without evidence.
