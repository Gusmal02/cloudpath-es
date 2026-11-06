#!/usr/bin/env bash
# CloudPath ES — instalación de dependencias (Linux/macOS)
set -euo pipefail

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
uv sync

# Crear directorios de datos
mkdir -p "$ROOT/backend/data/questions" "$ROOT/backend/data/chroma" "$ROOT/backend/data"

# Frontend
echo "[frontend] Instalando dependencias npm..."
cd "$ROOT/frontend"
npm install

echo ""
echo "=== Listo ==="
echo ""
echo "Para iniciar la aplicación, ejecuta desde la raíz del proyecto:"
echo ""
echo "  ./start.sh"
echo ""
echo "O con Docker:"
echo ""
echo "  docker compose up --build"
echo ""
echo "Opcional — IA local (análisis What If + generación de preguntas):"
echo "  ollama pull llama3.2:3b"
echo ""
