$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$LogDir = Join-Path $Root ".logs"
$Python = Join-Path $Backend ".venv\Scripts\python.exe"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Stop-WorkspacePort {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)" -ErrorAction SilentlyContinue
        if ($process -and $process.CommandLine -like "*$Root*") {
            Stop-Process -Id $connection.OwningProcess -Force
        }
    }
}

function Wait-Url {
    param(
        [string]$Url,
        [string]$Name
    )

    for ($i = 0; $i -lt 30; $i++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                Write-Host "$Name is ready: $Url"
                return
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    throw "$Name did not start. Check logs in $LogDir."
}

if (!(Test-Path $Python)) {
    Write-Host "Creating backend virtual environment..."
    python -m venv (Join-Path $Backend ".venv")
}

Write-Host "Installing backend dependencies..."
& $Python -m pip install -q -r (Join-Path $Backend "requirements.txt")

Write-Host "Installing frontend dependencies..."
Push-Location $Frontend
npm install --silent
Pop-Location

Write-Host "Applying backend migrations..."
Push-Location $Backend
& $Python manage.py migrate --noinput
Pop-Location

Stop-WorkspacePort -Port 3000
Stop-WorkspacePort -Port 8000

Write-Host "Starting backend on http://127.0.0.1:8000 ..."
Start-Process -FilePath $Python `
    -ArgumentList @("manage.py", "runserver", "127.0.0.1:8000") `
    -WorkingDirectory $Backend `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $LogDir "backend.log") `
    -RedirectStandardError (Join-Path $LogDir "backend.err.log")

Write-Host "Starting frontend on http://127.0.0.1:3000 ..."
Start-Process -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory $Frontend `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $LogDir "frontend.log") `
    -RedirectStandardError (Join-Path $LogDir "frontend.err.log")

Wait-Url -Url "http://127.0.0.1:8000/api/docs/" -Name "Backend"
Wait-Url -Url "http://127.0.0.1:3000" -Name "Frontend"

Write-Host ""
Write-Host "Roastly is running."
Write-Host "Frontend: http://127.0.0.1:3000"
Write-Host "API docs:  http://127.0.0.1:8000/api/docs/"
Write-Host "Logs:      $LogDir"
