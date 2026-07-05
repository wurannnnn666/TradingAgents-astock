$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$env:TRADINGAGENTS_KOL_DB_PATH = "C:\Users\35230\.tradingagents\kol\local_kol_radar.sqlite"
$env:OBSIDIAN_VAULT_PATH = "C:\Users\35230\Documents\Obsidian Vault"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$url = "http://localhost:8501"
Write-Host "Starting TradingAgents local KOL UI..." -ForegroundColor Green
Write-Host "URL: $url" -ForegroundColor Cyan
Write-Host "SQLite: $env:TRADINGAGENTS_KOL_DB_PATH"
Write-Host "Obsidian: $env:OBSIDIAN_VAULT_PATH\KOL-Radar"

Start-Process $url
python -m streamlit run web/app.py --server.port 8501
