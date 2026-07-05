$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$env:TRADINGAGENTS_KOL_DB_PATH = "C:\Users\35230\.tradingagents\kol\local_kol_radar.sqlite"
$env:OBSIDIAN_VAULT_PATH = "C:\Users\35230\Documents\Obsidian Vault"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$port = 8501
$localUrl = "http://localhost:$port"
$lanIp = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } |
    Select-Object -First 1 -ExpandProperty IPAddress)
$lanUrl = if ($lanIp) { "http://$($lanIp):$port" } else { $localUrl }

try {
    if (-not (Get-NetFirewallRule -DisplayName "TradingAgents Local KOL UI" -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule `
            -DisplayName "TradingAgents Local KOL UI" `
            -Direction Inbound `
            -Action Allow `
            -Protocol TCP `
            -LocalPort $port `
            -Profile Private `
            -ErrorAction Stop `
            | Out-Null
    }
} catch {
    Write-Host "Firewall rule not added. Run PowerShell as Administrator if LAN devices cannot open the UI." -ForegroundColor Yellow
}

Write-Host "Starting TradingAgents local KOL UI..." -ForegroundColor Green
Write-Host "Local URL: $localUrl" -ForegroundColor Cyan
Write-Host "LAN URL: $lanUrl" -ForegroundColor Cyan
Write-Host "SQLite: $env:TRADINGAGENTS_KOL_DB_PATH"
Write-Host "Obsidian: $env:OBSIDIAN_VAULT_PATH\KOL-Radar"

Start-Process $localUrl
python -m streamlit run web/app.py --server.port $port --server.address 0.0.0.0
