$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv/Scripts/python.exe')) { throw 'Run scripts/Setup.ps1 first' }
Start-Process 'http://127.0.0.1:8765'
& .venv/Scripts/python.exe -m workbench --root (Get-Location).Path
