#!/usr/bin/env bash
# Script to run both Gastroteacher Backend (FastAPI) and Frontend (Vue 3 + Vite)

echo "============================================================"
echo " 🚀 Iniciando Gastroteacher AI Assistant (Full-Stack)"
echo "============================================================"

# Navigate to project root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# 1. Start FastAPI Backend in background
echo "📦 Iniciando Backend FastAPI en http://localhost:8000..."
./backend/venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Trap Ctrl+C to kill backend when exiting
trap "echo 'Deteniendo servidores...'; kill $BACKEND_PID 2>/dev/null; exit" SIGINT SIGTERM EXIT

# 2. Wait 2 seconds for backend to initialize
sleep 2

# 3. Start Vue 3 Frontend
echo "✨ Iniciando Frontend Vue 3 en http://localhost:5173..."
cd frontend/Rage_frontend && npm run dev
