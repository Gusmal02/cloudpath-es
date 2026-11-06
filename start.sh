#!/usr/bin/env bash
# CloudPath ES — arranca backend + frontend con un solo comando
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT_FILE="$ROOT/backend/data/.port"

# Cleanup handler: kills backend and frontend on Ctrl+C
BACKEND_PID=""
FRONTEND_PID=""
cleanup() {
  echo ""
  echo "[cloudpath] Deteniendo..."
  [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  rm -f "$PORT_FILE"
  exit 0
}
trap cleanup INT TERM

# Remove stale port file so the wait loop doesn't read an old value
rm -f "$PORT_FILE"

# Start backend in background
echo "[backend] Iniciando..."
cd "$ROOT/backend"
uv run python main.py &
BACKEND_PID=$!

# Wait for port file (backend writes it once it binds)
echo "[backend] Esperando que el backend esté listo..."
WAIT=0
while [ ! -f "$PORT_FILE" ] && [ $WAIT -lt 30 ]; do
  sleep 1
  WAIT=$((WAIT + 1))
  # Check backend didn't crash
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "[ERROR] El backend se detuvo inesperadamente."
    exit 1
  fi
done

if [ ! -f "$PORT_FILE" ]; then
  echo "[ERROR] El backend no respondió en 30 segundos."
  kill "$BACKEND_PID" 2>/dev/null || true
  exit 1
fi

PORT=$(cat "$PORT_FILE")
echo "[backend] Listo en http://localhost:$PORT"

# Start frontend in foreground (so Ctrl+C is natural)
echo "[frontend] Iniciando en http://localhost:5173"
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:$PORT"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  Presiona Ctrl+C para detener todo."
echo ""

# Wait for either process to exit
wait "$FRONTEND_PID" "$BACKEND_PID"
