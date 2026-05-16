from .base import Rule
from ..events import Event


class ErraticDrivingRule(Rule):
    name = "conduccion_erratica"

    def __init__(self, window=45, lateral_std_threshold=0.9):
        self.window = window
        self.thr = lateral_std_threshold

    def update(self, frame_idx, t_sec, active, history, cfg, log):
        for tid in active:
            window = history.window(tid, self.window)
            if len(window) < self.window // 2:
                continue
            pts = [r["world_pt"] or r["image_pt"] for r in window]
            if any(p is None for p in pts):
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            mean_x = sum(xs) / len(xs)
            mean_y = sum(ys) / len(ys)
            var = sum(((x - mean_x) ** 2 + (y - mean_y) ** 2) for x, y in zip(xs, ys)) / len(xs)
            dx = pts[-1][0] - pts[0][0]
            dy = pts[-1][1] - pts[0][1]
            displacement = (dx * dx + dy * dy) ** 0.5
            if displacement < 1e-3:
                continue
            ratio = (var ** 0.5) / displacement
            if ratio > self.thr:
                latest = window[-1]
                log.add(Event(
                    frame=frame_idx, t_sec=t_sec, track_id=tid,
                    type=self.name, severity=min(1.0, ratio),
                    detail=f"std/disp={ratio:.2f}",
                    image_x=latest["image_pt"][0], image_y=latest["image_pt"][1],
                    speed_kmh=history.speed_kmh(tid) or 0.0,
                ), cooldown_frames=150)
