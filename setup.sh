#!/usr/bin/env bash
set -euo pipefail

# CloudPath ES — setup script (Linux/macOS)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== CloudPath ES — setup ==="

# Check uv
if ! command -v uv &>/dev/null; then
  echo "[backend] Instalando uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check Node
if ! command -v node &>/dev/null; then
  echo "[ERROR] Node.js no encontrado. Instala Node 20+ desde https://nodejs.org"
  exit 1
fi

# Backend
echo "[backend] Creando entorno virtual con uv..."
cd "$ROOT/backend"
uv python pin 3.12
uv venv
uv pip install -r pyproject.toml

# Crear directorios de datos del backend
mkdir -p "$ROOT/backend/data/questions" "$ROOT/backend/data/chroma"

# Frontend
echo "[frontend] Instalando dependencias npm..."
cd "$ROOT/frontend"
npm install

echo ""
echo "=== Listo ==="
echo ""
echo "1. Inicia el backend:   cd backend && python main.py"
echo "2. Inicia el frontend:  cd frontend && npm run dev"
echo "   Las preguntas se cargan automáticamente al iniciar el backend."
echo ""
echo "Opcional — IA local (análisis What If + generación de preguntas):"
echo "   ollama pull llama3.2:3b"
echo ""
echo "O usa Docker: docker compose up --build"
