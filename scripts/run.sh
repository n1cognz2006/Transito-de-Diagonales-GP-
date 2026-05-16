#!/usr/bin/env bash
# Atajo para correr el pipeline con el venv correcto.
set -euo pipefail

VENV=/media/gustipardo/OS/transito-workspace/venv
REPO=/home/gustipardo/Desktop/Transito-de-Diagonales-GP-
export PYTHONPATH="$REPO"
export HF_HOME=/media/gustipardo/DATA/transito-workspace/cache/hf
export TORCH_HOME=/media/gustipardo/DATA/transito-workspace/cache/torch
export YOLO_CONFIG_DIR=/media/gustipardo/DATA/transito-workspace/cache/yolo

exec "$VENV/bin/python" -m src.pipeline "$@"
