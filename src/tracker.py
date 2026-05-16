import numpy as np
import supervision as sv
from ultralytics import YOLO
from collections import defaultdict, deque
from .config import YOLO_MODEL_DEFAULT, VEHICLE_CLASS_IDS, CLASS_NAMES
from .geom import bbox_bottom_center


class VehicleTracker:
    def __init__(self, model_path=None, conf=0.25, iou=0.5, device=None, imgsz=1280):
        self.model = YOLO(str(model_path or YOLO_MODEL_DEFAULT))
        self.tracker = sv.ByteTrack(frame_rate=30)
        self.conf = conf
        self.iou = iou
        self.device = device
        self.imgsz = imgsz

    def __call__(self, frame):
        kwargs = dict(conf=self.conf, iou=self.iou, classes=VEHICLE_CLASS_IDS,
                      verbose=False, imgsz=self.imgsz)
        if self.device is not None:
            kwargs["device"] = self.device
        result = self.model(frame, **kwargs)[0]
        detections = sv.Detections.from_ultralytics(result)
        return self.tracker.update_with_detections(detections)


class TrackHistory:
    """Per-track rolling history of position, speed, lane."""

    def __init__(self, max_len=120):
        self.max_len = max_len
        self.records = defaultdict(lambda: deque(maxlen=max_len))
        self.classes = {}

    def update(self, frame_idx, t_sec, track_id, image_pt, world_pt, class_id, lane_name=None):
        self.records[track_id].append({
            "frame": frame_idx,
            "t": t_sec,
            "image_pt": image_pt,
            "world_pt": world_pt,
            "lane": lane_name,
        })
        self.classes[track_id] = class_id

    def latest(self, track_id):
        h = self.records[track_id]
        return h[-1] if h else None

    def previous(self, track_id):
        h = self.records[track_id]
        return h[-2] if len(h) >= 2 else None

    def window(self, track_id, n):
        h = self.records[track_id]
        return list(h)[-n:]

    def class_name(self, track_id):
        return CLASS_NAMES.get(self.classes.get(track_id), "veh")

    def speed_kmh(self, track_id, window=15):
        h = self.window(track_id, window)
        if len(h) < 4:
            return 0.0
        a, b = h[0], h[-1]
        if a["world_pt"] is None or b["world_pt"] is None:
            return None
        dt = b["t"] - a["t"]
        if dt <= 0:
            return 0.0
        dx = b["world_pt"][0] - a["world_pt"][0]
        dy = b["world_pt"][1] - a["world_pt"][1]
        dist_m = (dx * dx + dy * dy) ** 0.5
        kmh = (dist_m / dt) * 3.6
        return min(kmh, 90.0)

    def heading_deg(self, track_id, window=10):
        h = self.window(track_id, window)
        if len(h) < 2:
            return None
        a, b = h[0], h[-1]
        pa = a["world_pt"] or a["image_pt"]
        pb = b["world_pt"] or b["image_pt"]
        dx = pb[0] - pa[0]
        dy = pb[1] - pa[1]
        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return None
        return (np.degrees(np.arctan2(dy, dx)) + 360) % 360
