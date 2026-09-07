@echo off
setlocal enabledelayedexpansion
title Gastroteacher AI Assistant - Arranque
cd /d "%~dp0"

echo ============================================================
echo  Gastroteacher AI Assistant - Arranque (Windows CMD)
echo ============================================================

rem ------------------------------------------------------------
rem 1. Localizar Python 3.12
rem ------------------------------------------------------------
set "PYCMD="
where py >nul 2>nul
if !errorlevel!==0 (
    py -3.12 --version >nul 2>nul
    if !errorlevel!==0 set "PYCMD=py -3.12"
)
if not defined PYCMD (
    python --version 2>nul | findstr /C:"3.12" >nul
    if !errorlevel!==0 set "PYCMD=python"
)
if not defined PYCMD (
    echo [ERROR] No se encontro Python 3.12. Instalalo desde https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python: %PYCMD%

rem ------------------------------------------------------------
rem 2. Entorno virtual (backend\venv)
rem ------------------------------------------------------------
set "VENV_PY=%CD%\backend\venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo [INFO] Creando entorno virtual en backend\venv ...
    %PYCMD% -m venv backend\venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo [OK] Entorno virtual presente (backend\venv).
)

rem ------------------------------------------------------------
rem 3. Dependencias de Python (instalar si faltan)
rem ------------------------------------------------------------
"%VENV_PY%" -c "import fastapi, uvicorn, chromadb" >nul 2>nul
if errorlevel 1 (
    echo [INFO] Instalando dependencias de Python (requirements.txt) ...
    "%VENV_PY%" -m pip install --upgrade pip
    "%VENV_PY%" -m pip install -r backend\requirements.txt
) else (
    echo [OK] Dependencias de Python presentes.
)

rem ------------------------------------------------------------
rem 4. Variables de entorno (.env desde .env.example)
rem ------------------------------------------------------------
if not exist ".env" (
    echo [INFO] Creando .env desde .env.example ...
    copy /Y ".env.example" ".env" >nul
)
if not exist "backend\.env" (
    echo [INFO] Creando backend\.env desde backend\.env.example ...
    copy /Y "backend\.env.example" "backend\.env" >nul
)

rem ------------------------------------------------------------
rem 5. Dependencias del frontend (npm install si faltan)
rem ------------------------------------------------------------
if not exist "frontend\Rage_frontend\node_modules" (
    echo [INFO] Instalando dependencias del frontend (npm install) ...
    pushd frontend\Rage_frontend
    call npm install
    popd
) else (
    echo [OK] node_modules presente.
)

rem ------------------------------------------------------------
rem 6. Levantar backend y frontend concurrentemente
rem ------------------------------------------------------------
echo [INFO] Iniciando Backend FastAPI en http://localhost:8000 ...
start "Gastroteacher-Backend" cmd /k ""%VENV_PY%" -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000"

echo [INFO] Iniciando Frontend Vue 3 en http://localhost:5173 ...
start "Gastroteacher-Frontend" cmd /k "npm --prefix frontend\Rage_frontend run dev"

echo.
echo ============================================================
echo  Servidores iniciados:
echo   Backend : http://localhost:8000   (Swagger en /docs)
echo   Frontend: http://localhost:5173
echo ============================================================
echo  Cierra las dos ventanas para detener los servidores.
echo.
pause
endlocal