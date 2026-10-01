# Source, scope, and review

- Upstream: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Immutable revision: `09170eec67eefd46a7ae85de61b40c194020f997`
- License: MIT, Copyright (c) 2024 Next Level Builder; full upstream license in `LICENSE`
- Retrieved: 2026-10-01
- Entry point adapted from `.claude/skills/ui-ux-pro-max/SKILL.md`; all four runtime files and 35 CSV catalogs are unchanged copies of `src/ui-ux-pro-max/scripts/` and `src/ui-ux-pro-max/data/` at this revision
- Two additional JSON files preserve upstream data provenance and Google Fonts license metadata. No fonts or icon binaries are included
- `UPSTREAM-MANIFEST.json` records every unchanged upstream file and its Git blob SHA for integrity verification

## Selection and changes

Only the local search runtime, catalogs required by its configured domains/stacks, and relevant provenance/license metadata are included. This is not the full upstream plugin. CLI distribution, marketplace manifests, hooks, installers, update tools, tests, bulk upstream icon metadata, and unrelated skills are excluded. No self-update or download mechanism is included.

`SKILL.md` is a rewritten adaptation with only portable name/description frontmatter. It removes plugin-root paths and installation instructions, adds approved-stack and mainframe-parity requirements, gates optional execution on existing Python and workplace approval, and defines a transparent manual-reference fallback. Catalogs are read on demand; never load the entire data directory into the model context.

## Static review and capability boundaries

The four selected Python files were read and parsed as AST without importing or executing them. Imports are standard-library modules plus local `core`, `design_system`, and `reasoning_contract`. No network client, shell execution, package install, credential access, or dynamic eval/exec was found. Local reads are CSV catalogs; `COLORTERM` is read for terminal presentation. Optional persistence writes Markdown, creates directories, and uses temporary files/atomic filesystem operations. Default documented commands do not request persistence and use `-B` to suppress bytecode caches.

All CSV and JSON files were parsed structurally; source hashes were checked against the pinned Git tree. This is a bounded static review, not a comprehensive security audit or runtime test. Upstream search/design generation and workplace compatibility remain untested. Python 3.12 was used to parse source syntax. Runtime requires an already available compatible Python 3 interpreter and permission to run repository scripts. No software was installed and no upstream script was executed.

Recommendations may mention external fonts, packages, or outdated/version-specific guidance. These are reference data, not download permission; apply only after checking the existing approved stack, licenses for actual assets, user requirements, and actual UI behavior. No automatic follow-up network requests occur in the selected runtime.
