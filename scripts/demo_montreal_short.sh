#!/usr/bin/env bash
# Procesa solo los primeros 10 segundos del Montreal para iterar rápido.
set -euo pipefail

REPO=/home/gustipardo/Desktop/Transito-de-Diagonales-GP-
VENV=/media/gustipardo/OS/transito-workspace/venv
VIDEO=/media/gustipardo/DATA/transito-workspace/videos/raw/montreal_intersection.mp4
CONFIG="$REPO/configs/montreal.json"
OUT=/media/gustipardo/DATA/transito-workspace/videos/output/montreal_short.mp4
EVENTS=/media/gustipardo/DATA/transito-workspace/data/montreal_short.csv

export PYTHONPATH="$REPO"
export YOLO_CONFIG_DIR=/media/gustipardo/OS/transito-workspace/cache/yolo

mkdir -p "$(dirname "$OUT")" "$(dirname "$EVENTS")"

"$VENV/bin/python" -m src.pipeline \
    --video "$VIDEO" \
    --config "$CONFIG" \
    --model /media/gustipardo/OS/transito-workspace/models/yolo11m.pt \
    --out "$OUT" \
    --events "$EVENTS" \
    --device cpu \
    --start 0 \
    --duration 10 \
    --no-display

echo
echo "Listo (10s):"
echo "  Anotado: $OUT"
echo "  Eventos: $EVENTS"
