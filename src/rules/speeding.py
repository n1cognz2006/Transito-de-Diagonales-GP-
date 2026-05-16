from .base import Rule
from ..events import Event


class SpeedingRule(Rule):
    name = "exceso_velocidad"

    def __init__(self, default_limit_kmh=50, tolerance_kmh=15):
        self.default_limit = default_limit_kmh
        self.tolerance = tolerance_kmh

    def update(self, frame_idx, t_sec, active, history, cfg, log):
        for tid in active:
            speed = history.speed_kmh(tid)
            if speed is None or speed <= 0:
                continue
            latest = history.latest(tid)
            if not latest:
                continue
            lane = cfg.lane_of(latest["image_pt"]) if cfg.lanes else None
            limit = (lane.speed_limit_kmh if lane and lane.speed_limit_kmh else cfg.speed_limit_kmh) or self.default_limit
            if speed > limit + self.tolerance:
                excess = speed - limit
                severity = min(1.0, excess / max(limit, 1) )
                log.add(Event(
                    frame=frame_idx, t_sec=t_sec, track_id=tid,
                    type=self.name, severity=severity,
                    detail=f"{speed:.1f} km/h en zona de {limit:.0f}",
                    image_x=latest["image_pt"][0], image_y=latest["image_pt"][1],
                    speed_kmh=speed,
                ), cooldown_frames=60)
