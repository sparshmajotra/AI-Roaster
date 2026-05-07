$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot

foreach ($port in @(3000, 8000)) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)" -ErrorAction SilentlyContinue
        if ($process -and $process.CommandLine -like "*$Root*") {
            Stop-Process -Id $connection.OwningProcess -Force
            Write-Host "Stopped Roastly process $($connection.OwningProcess) on port $port"
        }
    }
}

Write-Host "Roastly dev servers stopped."
