# Mainframe modernization workspace

Start with [START_HERE.md](START_HERE.md). Read [PROJECT.yaml](PROJECT.yaml), the compact [MEMORY.md](MEMORY.md), and only the necessary sections of [the migration contract](docs/MIGRATION_CONTRACT.md).

Native role profiles are in .github/agents and task skills in .github/skills. Use automatic task routing from .github/copilot-instructions.md; do not load every skill or data catalog. Preserve source evidence, all eight categories plus utilities, SME/profile/user approvals, segmented human review and actual-target comparison gates.

Secrets belong only in local untracked .env. Never read or echo it into model context; use safe validators. Do not index certs, credentials, raw sensitive extracts or runtime stores. No silent installation, trust bypass, production writes, or acceptance from missing evidence. Follow the real tools and prerequisites; report unavailable capabilities honestly.
