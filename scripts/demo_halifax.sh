#!/usr/bin/env bash
# Corre el pipeline sobre el video aéreo de Halifax con la config inicial.
set -euo pipefail

REPO=/home/gustipardo/Desktop/Transito-de-Diagonales-GP-
VENV=/media/gustipardo/OS/transito-workspace/venv
VIDEO=/media/gustipardo/DATA/transito-workspace/videos/raw/halifax_intersection_aerial.mp4
CONFIG="$REPO/configs/halifax_aerial.json"
OUT=/media/gustipardo/DATA/transito-workspace/videos/output/halifax_annotated.mp4
EVENTS=/media/gustipardo/DATA/transito-workspace/data/halifax_events.csv

export PYTHONPATH="$REPO"
export HF_HOME=/media/gustipardo/DATA/transito-workspace/cache/hf
export TORCH_HOME=/media/gustipardo/DATA/transito-workspace/cache/torch
export YOLO_CONFIG_DIR=/media/gustipardo/OS/transito-workspace/cache/yolo

mkdir -p "$(dirname "$OUT")" "$(dirname "$EVENTS")"

"$VENV/bin/python" -m src.pipeline \
    --video "$VIDEO" \
    --config "$CONFIG" \
    --model /media/gustipardo/OS/transito-workspace/models/yolo11m.pt \
    --out "$OUT" \
    --events "$EVENTS" \
    --device cpu \
    --no-display

echo
echo "Listo:"
echo "  Anotado: $OUT"
echo "  Eventos: $EVENTS"
