from .base import Rule
from ..events import Event


class NoStopRule(Rule):
    name = "no_detener_en_stop"

    def update(self, frame_idx, t_sec, active, history, cfg, log):
        for tid in active:
            prev = history.previous(tid)
            curr = history.latest(tid)
            if not prev or not curr:
                continue
            speed = history.speed_kmh(tid) or 0.0
            for sl in cfg.stop_lines:
                if not sl.crossed_by(prev["image_pt"], curr["image_pt"]):
                    continue
                if sl.applies_to_lane:
                    lane = cfg.lane_of(curr["image_pt"])
                    if lane is None or lane.name != sl.applies_to_lane:
                        continue
                if speed > sl.stop_threshold_kmh:
                    severity = min(1.0, speed / 40.0)
                    log.add(Event(
                        frame=frame_idx, t_sec=t_sec, track_id=tid,
                        type=self.name, severity=severity,
                        detail=f"Cruzó {sl.name} a {speed:.1f} km/h sin detenerse",
                        image_x=curr["image_pt"][0], image_y=curr["image_pt"][1],
                        speed_kmh=speed,
                    ), cooldown_frames=120)
