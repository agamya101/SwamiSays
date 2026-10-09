# SwamiSays Startup Script (PowerShell)
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  SwamiSays — Timeless Wisdom for Gen Z & Alpha  " -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# Find Local IP address for phone testing
$localIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback|vEthernet|Virtual' -and $_.IPAddress -match '^192\.|^10\.|^172\.' } | Select-Object -First 1).IPAddress
if (-not $localIp) { $localIp = "127.0.0.1" }

Write-Host "`n📱 Phone Access URL:   http://${localIp}:8000" -ForegroundColor Green
Write-Host "💻 Laptop Access URL:  http://localhost:8000" -ForegroundColor Green
Write-Host "`nStarting SwamiSays Server on port 8000..." -ForegroundColor Cyan

$env:PYTHONPATH = "$PSScriptRoot\backend"
python -m uvicorn server:app --app-dir "$PSScriptRoot\backend" --host 0.0.0.0 --port 8000 --reload
