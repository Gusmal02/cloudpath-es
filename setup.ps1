# CloudPath ES — setup script (Windows PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== CloudPath ES — setup ===" -ForegroundColor Cyan

# Check uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[backend] Instalando uv..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
}

# Check Node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js no encontrado. Instala Node 20+ desde https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Backend
Write-Host "[backend] Creando entorno virtual con uv..." -ForegroundColor Yellow
Set-Location "$Root\backend"
uv python pin 3.12
uv venv
uv pip install -r pyproject.toml

# Crear directorios de datos del backend
New-Item -ItemType Directory -Force -Path "$Root\backend\data\questions" | Out-Null
New-Item -ItemType Directory -Force -Path "$Root\backend\data\chroma" | Out-Null

# Frontend
Write-Host "[frontend] Instalando dependencias npm..." -ForegroundColor Yellow
Set-Location "$Root\frontend"
npm install

Write-Host ""
Write-Host "=== Listo ===" -ForegroundColor Green
Write-Host ""
Write-Host "1. Inicia el backend:   cd backend; python main.py"
Write-Host "2. Inicia el frontend:  cd frontend; npm run dev"
Write-Host "   Las preguntas se cargan automaticamente al iniciar el backend."
Write-Host ""
Write-Host "Opcional — IA local (analisis What If + generacion de preguntas):"
Write-Host "   ollama pull llama3.2:3b"
