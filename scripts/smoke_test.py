"""Smoke test: verifica que el venv tenga todo y CUDA funcione."""
import sys


def main():
    print("== Python ==")
    print(f"  {sys.version}")
    print()
    print("== Imports ==")
    import torch
    print(f"  torch       {torch.__version__}")
    print(f"  cuda?       {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  device      {torch.cuda.get_device_name(0)}")
        print(f"  cuda ver    {torch.version.cuda}")
    import torchvision
    print(f"  torchvision {torchvision.__version__}")
    import cv2
    print(f"  opencv      {cv2.__version__}")
    import numpy as np
    print(f"  numpy       {np.__version__}")
    import supervision as sv
    print(f"  supervision {sv.__version__}")
    from ultralytics import YOLO
    import ultralytics
    print(f"  ultralytics {ultralytics.__version__}")
    import yt_dlp
    print(f"  yt-dlp      {yt_dlp.version.__version__}")
    import pandas as pd
    print(f"  pandas      {pd.__version__}")
    print()
    print("== YOLO inference de prueba ==")
    model = YOLO("yolo11n.pt")
    dummy = np.zeros((640, 640, 3), dtype=np.uint8)
    r = model(dummy, verbose=False)[0]
    print(f"  detections en imagen vacía: {len(r.boxes)} (esperado 0)")
    print()
    print("✓ todo OK")


if __name__ == "__main__":
    main()
