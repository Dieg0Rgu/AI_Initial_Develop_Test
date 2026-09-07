#!/usr/bin/env bash
# ============================================================
# Gastroteacher AI Assistant - Arranque (Linux/macOS)
# Verifica/crea el venv con Python 3.12, instala dependencias si
# faltan, copia .env.example -> .env y levanta backend + frontend.
# Uso:  ./start.sh
# ============================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "============================================================"
echo " 🚀 Gastroteacher AI Assistant - Arranque (Linux/macOS)"
echo "============================================================"

# ------------------------------------------------------------
# 1. Localizar Python 3.12
# ------------------------------------------------------------
PY=""
if command -v python3.12 >/dev/null 2>&1; then
    PY="python3.12"
elif command -v python3 >/dev/null 2>&1 && python3 --version 2>&1 | grep -q "3.12"; then
    PY="python3"
elif command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "3.12"; then
    PY="python"
fi

if [ -z "$PY" ]; then
    echo "[ERROR] No se encontró Python 3.12. Instálalo y vuelve a intentarlo." >&2
    exit 1
fi
echo "[OK] Python: $PY"

# ------------------------------------------------------------
# 2. Entorno virtual (backend/venv)
# ------------------------------------------------------------
VENV_DIR="$ROOT_DIR/backend/venv"
VENV_PY="$VENV_DIR/bin/python"

if [ ! -f "$VENV_PY" ]; then
    echo "[INFO] Creando entorno virtual en backend/venv ..."
    "$PY" -m venv "$VENV_DIR"
else
    echo "[OK] Entorno virtual presente (backend/venv)."
fi

# ------------------------------------------------------------
# 3. Dependencias de Python (instalar si faltan)
# ------------------------------------------------------------
if ! "$VENV_PY" -c "import fastapi, uvicorn, chromadb" >/dev/null 2>&1; then
    echo "[INFO] Instalando dependencias de Python (requirements.txt) ..."
    "$VENV_PY" -m pip install --upgrade pip
    "$VENV_PY" -m pip install -r "$ROOT_DIR/backend/requirements.txt"
else
    echo "[OK] Dependencias de Python presentes."
fi

# ------------------------------------------------------------
# 4. Variables de entorno (.env desde .env.example)
# ------------------------------------------------------------
if [ ! -f "$ROOT_DIR/.env" ]; then
    echo "[INFO] Creando .env desde .env.example ..."
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi
if [ ! -f "$ROOT_DIR/backend/.env" ]; then
    echo "[INFO] Creando backend/.env desde backend/.env.example ..."
    cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
fi

# ------------------------------------------------------------
# 5. Dependencias del frontend (npm install si faltan)
# ------------------------------------------------------------
FRONTEND_DIR="$ROOT_DIR/frontend/Rage_frontend"
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "[INFO] Instalando dependencias del frontend (npm install) ..."
    (cd "$FRONTEND_DIR" && npm install)
else
    echo "[OK] node_modules presente."
fi

# ------------------------------------------------------------
# 6. Levantar backend y frontend concurrentemente
# ------------------------------------------------------------
echo ""
echo "[INFO] Iniciando Backend FastAPI en http://localhost:8000 ..."
"$VENV_PY" -m uvicorn app.main:app --app-dir "$ROOT_DIR/backend" --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

echo "[INFO] Iniciando Frontend Vue 3 en http://localhost:5173 ..."
(cd "$FRONTEND_DIR" && npm run dev) &
FRONTEND_PID=$!

trap 'echo "Deteniendo servidores..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' INT TERM EXIT

echo ""
echo "============================================================"
echo " Servidores iniciados:"
echo "  Backend : http://localhost:8000   (Swagger en /docs)"
echo "  Frontend: http://localhost:5173"
echo "  Presiona Ctrl+C para detener ambos."
echo "============================================================"

wait