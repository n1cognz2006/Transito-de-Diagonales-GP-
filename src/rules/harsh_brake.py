from .base import Rule
from ..events import Event


class HarshBrakeRule(Rule):
    name = "frenada_brusca"

    def __init__(self, decel_kmh_per_s=30.0, min_speed_kmh=25.0):
        self.decel_threshold = decel_kmh_per_s
        self.min_speed = min_speed_kmh

    def update(self, frame_idx, t_sec, active, history, cfg, log):
        for tid in active:
            window = history.window(tid, 20)
            if len(window) < 15:
                continue
            mid = len(window) // 2
            v0 = history.speed_kmh(tid, window=mid) or 0.0
            v1 = history.speed_kmh(tid, window=len(window)) or 0.0
            dt = window[-1]["t"] - window[0]["t"]
            if dt <= 0 or v0 < self.min_speed or v1 > v0:
                continue
            decel = (v0 - v1) / dt
            if decel > self.decel_threshold and (v0 - v1) > 8:
                log.add(Event(
                    frame=frame_idx, t_sec=t_sec, track_id=tid,
                    type=self.name, severity=min(1.0, decel / 40.0),
                    detail=f"-{decel:.1f} km/h/s",
                    image_x=window[-1]["image_pt"][0], image_y=window[-1]["image_pt"][1],
                    speed_kmh=v1,
                ), cooldown_frames=60)
