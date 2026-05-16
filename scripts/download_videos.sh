#!/usr/bin/env bash
# Descarga videos de prueba a /media/gustipardo/DATA/transito-workspace/videos/raw
# Usa yt-dlp del venv.
set -euo pipefail

VENV=/media/gustipardo/OS/transito-workspace/venv
RAW=/media/gustipardo/DATA/transito-workspace/videos/raw
YTDLP="$VENV/bin/yt-dlp"

mkdir -p "$RAW"

# Pasamos URLs como argumentos, o si no, usamos los defaults
URLS=("$@")
if [ ${#URLS[@]} -eq 0 ]; then
    cat <<EOF
Uso: $0 <url1> [url2 ...]

Tip: buscá en YouTube con keywords como:
  - "traffic intersection cam fixed"
  - "russian dashcam wrong way"
  - "stop sign violations compilation"
  - "yielding traffic camera"
EOF
    exit 1
fi

for url in "${URLS[@]}"; do
    echo "↓ Bajando: $url"
    "$YTDLP" \
        --no-playlist \
        -f "bv*[height<=720]+ba/b[height<=720]/b" \
        -o "$RAW/%(title).80s [%(id)s].%(ext)s" \
        --merge-output-format mp4 \
        "$url"
done

echo
echo "Listos en: $RAW"
ls -1 "$RAW"
