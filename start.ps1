# CloudPath ES — arranca backend + frontend con un solo comando (Windows PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PortFile = Join-Path $Root "backend\data\.port"

# Remove stale port file
if (Test-Path $PortFile) { Remove-Item $PortFile -Force }

# Start backend in a new hidden job
Write-Host "[backend] Iniciando..." -ForegroundColor Cyan
$BackendJob = Start-Job -ScriptBlock {
    param($Root)
    Set-Location "$Root\backend"
    uv run python main.py
} -ArgumentList $Root

# Wait for port file (max 30 s)
Write-Host "[backend] Esperando que el backend este listo..." -ForegroundColor Cyan
$Waited = 0
while (-not (Test-Path $PortFile) -and $Waited -lt 30) {
    Start-Sleep -Seconds 1
    $Waited++
    if ($BackendJob.State -eq "Failed" -or $BackendJob.State -eq "Completed") {
        Write-Host "[ERROR] El backend se detuvo inesperadamente." -ForegroundColor Red
        Receive-Job $BackendJob
        exit 1
    }
}
if (-not (Test-Path $PortFile)) {
    Write-Host "[ERROR] El backend no respondio en 30 segundos." -ForegroundColor Red
    Stop-Job $BackendJob
    exit 1
}

$Port = Get-Content $PortFile -Raw
Write-Host "[backend] Listo en http://localhost:$($Port.Trim())" -ForegroundColor Green

# Start frontend in a new hidden job
Write-Host "[frontend] Iniciando en http://localhost:5173" -ForegroundColor Cyan
$FrontendJob = Start-Job -ScriptBlock {
    param($Root)
    Set-Location "$Root\frontend"
    npm run dev
} -ArgumentList $Root

Write-Host ""
Write-Host "  Backend:  http://localhost:$($Port.Trim())" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "  Presiona Ctrl+C para detener todo." -ForegroundColor Yellow
Write-Host ""

# Stream output from both jobs and wait
try {
    while ($true) {
        Receive-Job $BackendJob, $FrontendJob 2>&1 | Write-Host
        if ($BackendJob.State -notin "Running","NotStarted" -or
            $FrontendJob.State -notin "Running","NotStarted") { break }
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "[cloudpath] Deteniendo..." -ForegroundColor Yellow
    Stop-Job $BackendJob, $FrontendJob -ErrorAction SilentlyContinue
    Remove-Job $BackendJob, $FrontendJob -Force -ErrorAction SilentlyContinue
    if (Test-Path $PortFile) { Remove-Item $PortFile -Force }
}
