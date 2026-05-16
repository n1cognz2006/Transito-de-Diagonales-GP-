from dataclasses import dataclass, asdict, field
import csv
from pathlib import Path


@dataclass
class Event:
    frame: int
    t_sec: float
    track_id: int
    type: str
    severity: float
    detail: str
    image_x: float
    image_y: float
    speed_kmh: float = 0.0


class EventLog:
    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)
        self.events: list[Event] = []
        self._by_track_type: dict[tuple[int, str], int] = {}

    def add(self, evt: Event, cooldown_frames: int = 30):
        key = (evt.track_id, evt.type)
        last = self._by_track_type.get(key)
        if last is not None and (evt.frame - last) < cooldown_frames:
            return False
        self._by_track_type[key] = evt.frame
        self.events.append(evt)
        return True

    def write(self):
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.csv_path, "w", newline="") as f:
            fields = ["frame", "t_sec", "track_id", "type", "severity", "detail",
                     "image_x", "image_y", "speed_kmh"]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for e in self.events:
                w.writerow(asdict(e))

    def per_track_summary(self):
        agg = {}
        for e in self.events:
            d = agg.setdefault(e.track_id, {"count": 0, "by_type": {}, "score": 0.0})
            d["count"] += 1
            d["by_type"][e.type] = d["by_type"].get(e.type, 0) + 1
            d["score"] += e.severity
        return agg
