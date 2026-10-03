#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
mkdir -p Endeavor knowledge/inbox
printf '%s\n' 'Run .venv/bin/python -m workbench from this directory.'
