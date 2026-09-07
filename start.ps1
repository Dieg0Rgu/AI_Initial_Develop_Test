# ============================================================
# Gastroteacher AI Assistant - Arranque multiplataforma (PowerShell)
# Verifica/crea el venv con Python 3.12, instala dependencias si
# faltan, copia .env.example -> .env y levanta backend + frontend.
# Uso:  powershell -ExecutionPolicy Bypass -File .\start.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host "============================================================" -ForegroundColor DarkYellow
Write-Host " Gastroteacher AI Assistant - Arranque (Windows)" -ForegroundColor DarkYellow
Write-Host "============================================================" -ForegroundColor DarkYellow

# ------------------------------------------------------------
# 1. Localizar Python 3.12
# ------------------------------------------------------------
$PythonExe = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $probe = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
    if ($LASTEXITCODE -eq 0 -and $probe) { $PythonExe = $probe.Trim() }
}
if (-not $PythonExe -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $ver = & python --version 2>&1 | Out-String
    if ($ver -match "3\.12") { $PythonExe = (& python -c "import sys; print(sys.executable)").Trim() }
}
if (-not $PythonExe) {
    Write-Host "[ERROR] No se encontró Python 3.12. Instálalo desde https://www.python.org/downloads/ y vuelve a intentarlo." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python 3.12: $PythonExe" -ForegroundColor Green

# ------------------------------------------------------------
# 2. Entorno virtual (backend/venv)
# ------------------------------------------------------------
$VenvDir = Join-Path $Root "backend\venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[INFO] Creando entorno virtual en backend\venv ..." -ForegroundColor Cyan
    & $PythonExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] No se pudo crear el entorno virtual." -ForegroundColor Red; exit 1 }
} else {
    Write-Host "[OK] Entorno virtual presente (backend\venv)." -ForegroundColor Green
}

# ------------------------------------------------------------
# 3. Dependencias de Python (instalar si faltan)
# ------------------------------------------------------------
& $VenvPython -c "import fastapi, uvicorn, chromadb" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Instalando dependencias de Python (requirements.txt) ..." -ForegroundColor Cyan
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r (Join-Path $Root "backend\requirements.txt")
} else {
    Write-Host "[OK] Dependencias de Python presentes." -ForegroundColor Green
}

# ------------------------------------------------------------
# 4. Variables de entorno (.env desde .env.example)
# ------------------------------------------------------------
if (-not (Test-Path (Join-Path $Root ".env"))) {
    Write-Host "[INFO] Creando .env desde .env.example ..." -ForegroundColor Cyan
    Copy-Item (Join-Path $Root ".env.example") (Join-Path $Root ".env")
}
if (-not (Test-Path (Join-Path $Root "backend\.env"))) {
    Write-Host "[INFO] Creando backend\.env desde backend\.env.example ..." -ForegroundColor Cyan
    Copy-Item (Join-Path $Root "backend\.env.example") (Join-Path $Root "backend\.env")
}

# ------------------------------------------------------------
# 5. Dependencias del frontend (npm install si faltan)
# ------------------------------------------------------------
$FrontendDir = Join-Path $Root "frontend\Rage_frontend"
if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Host "[INFO] Instalando dependencias del frontend (npm install) ..." -ForegroundColor Cyan
    Push-Location $FrontendDir
    try { & npm install } finally { Pop-Location }
} else {
    Write-Host "[OK] node_modules presente." -ForegroundColor Green
}

# ------------------------------------------------------------
# 6. Levantar backend y frontend concurrentemente
# ------------------------------------------------------------
Write-Host ""
Write-Host "[INFO] Iniciando Backend FastAPI en http://localhost:8000 ..." -ForegroundColor Cyan
$BackendProc = Start-Process -FilePath $VenvPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000") `
    -WorkingDirectory $Root -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host "[INFO] Iniciando Frontend Vue 3 en http://localhost:5173 ..." -ForegroundColor Cyan
$FrontendProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c", "npm --prefix `"$FrontendDir`" run dev" `
    -WorkingDirectory $Root -PassThru -WindowStyle Hidden

Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkYellow
Write-Host " Servidores iniciados:" -ForegroundColor DarkYellow
Write-Host "  Backend : http://localhost:8000   (Swagger en /docs)" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor DarkYellow
Write-Host ""
Write-Host "Presiona [Enter] para detener ambos servidores..." -ForegroundColor Gray
Read-Host | Out-Null

if ($BackendProc -and -not $BackendProc.HasExited) { Stop-Process -Id $BackendProc.Id -Force }
if ($FrontendProc -and -not $FrontendProc.HasExited) { Stop-Process -Id $FrontendProc.Id -Force }
Write-Host "Servidores detenidos." -ForegroundColor Green