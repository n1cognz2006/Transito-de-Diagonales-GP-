#!/usr/bin/env bash
# Sirve la landing en local: http://localhost:8000
set -e
cd "$(dirname "$0")"
PORT="${1:-8000}"
echo "→ http://localhost:$PORT"
python3 -m http.server "$PORT"
