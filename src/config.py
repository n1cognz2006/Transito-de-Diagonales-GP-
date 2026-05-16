from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKSPACE = Path("/media/gustipardo/OS/transito-workspace")
DATA = Path("/media/gustipardo/DATA/transito-workspace")

MODELS = WORKSPACE / "models"
VIDEOS_RAW = DATA / "videos/raw"
VIDEOS_OUT = DATA / "videos/output"
EVENTS_DIR = DATA / "data"
SNAPSHOTS = DATA / "snapshots"
CONFIGS = REPO / "configs"

YOLO_MODEL_DEFAULT = MODELS / "yolo11m.pt"
VEHICLE_CLASS_IDS = [2, 3, 5, 7]
CLASS_NAMES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

for p in [MODELS, VIDEOS_RAW, VIDEOS_OUT, EVENTS_DIR, SNAPSHOTS]:
    p.mkdir(parents=True, exist_ok=True)
