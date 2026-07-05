$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$env:TRADINGAGENTS_KOL_DB_PATH = "C:\Users\35230\.tradingagents\kol\local_kol_radar.sqlite"
$env:OBSIDIAN_VAULT_PATH = "C:\Users\35230\Documents\Obsidian Vault"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

python -m cli.main kol ingest --jsonl examples\kol\local_smoke_posts.jsonl
python -m cli.main kol sync-obsidian --full

Write-Host "KOL local smoke complete." -ForegroundColor Green
Write-Host "SQLite: $env:TRADINGAGENTS_KOL_DB_PATH"
Write-Host "Obsidian: $env:OBSIDIAN_VAULT_PATH\KOL-Radar"
