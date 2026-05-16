from .base import Rule
from ..events import Event


def _angle_diff(a, b):
    d = abs((a - b + 180) % 360 - 180)
    return d


class WrongWayRule(Rule):
    name = "contramano"

    def __init__(self, min_speed_kmh=5.0, max_deviation_deg=110.0):
        self.min_speed_kmh = min_speed_kmh
        self.max_deviation = max_deviation_deg

    def update(self, frame_idx, t_sec, active, history, cfg, log):
        for tid in active:
            curr = history.latest(tid)
            if not curr:
                continue
            speed = history.speed_kmh(tid) or 0.0
            if speed < self.min_speed_kmh:
                continue
            heading = history.heading_deg(tid)
            if heading is None:
                continue
            lane = cfg.lane_of(curr["image_pt"])
            if not lane or lane.direction_deg is None:
                continue
            dev = _angle_diff(heading, lane.direction_deg)
            if dev > self.max_deviation:
                log.add(Event(
                    frame=frame_idx, t_sec=t_sec, track_id=tid,
                    type=self.name, severity=min(1.0, dev / 180.0),
                    detail=f"Heading {heading:.0f}° vs carril {lane.direction_deg:.0f}° (Δ {dev:.0f}°)",
                    image_x=curr["image_pt"][0], image_y=curr["image_pt"][1],
                    speed_kmh=speed,
                ), cooldown_frames=90)
