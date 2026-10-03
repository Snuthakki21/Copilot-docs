$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv/Scripts/python.exe')) { py -3.12 -m venv .venv; if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 is required' } }
& .venv/Scripts/python.exe -m pip install -r requirements.lock
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
New-Item -ItemType Directory -Force Endeavor,knowledge/inbox | Out-Null
Write-Host 'Setup complete. Put sources in Endeavor; run scripts/Start.ps1.'
