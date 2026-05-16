#!/usr/bin/env bash
# Corre el pipeline sobre el video street-level de Montreal.
set -euo pipefail

REPO=/home/gustipardo/Desktop/Transito-de-Diagonales-GP-
VENV=/media/gustipardo/OS/transito-workspace/venv
VIDEO=/media/gustipardo/DATA/transito-workspace/videos/raw/montreal_intersection.mp4
CONFIG="$REPO/configs/montreal.json"
OUT=/media/gustipardo/DATA/transito-workspace/videos/output/montreal_annotated.mp4
EVENTS=/media/gustipardo/DATA/transito-workspace/data/montreal_events.csv

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
