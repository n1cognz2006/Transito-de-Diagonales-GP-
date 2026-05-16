#!/usr/bin/env bash
# Procesa los segundos 30-40 del Montreal como segunda escena.
set -euo pipefail

REPO=/home/gustipardo/Desktop/Transito-de-Diagonales-GP-
VENV=/media/gustipardo/OS/transito-workspace/venv
VIDEO=/media/gustipardo/DATA/transito-workspace/videos/raw/montreal_intersection.mp4
CONFIG="$REPO/configs/montreal.json"
OUT=/media/gustipardo/DATA/transito-workspace/videos/output/montreal_scene2.mp4
EVENTS=/media/gustipardo/DATA/transito-workspace/data/montreal_scene2.csv

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
    --start 30 \
    --duration 10 \
    --no-display
