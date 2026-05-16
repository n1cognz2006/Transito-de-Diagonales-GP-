from .base import Rule
from ..events import Event


class TailgatingRule(Rule):
    name = "distancia_corta"

    def __init__(self, min_gap_seconds=0.7, min_speed_kmh=30.0):
        self.min_gap = min_gap_seconds
        self.min_speed = min_speed_kmh

    def update(self, frame_idx, t_sec, active, history, cfg, log):
        lane_to_tracks = {}
        for tid in active:
            latest = history.latest(tid)
            if not latest or latest["world_pt"] is None:
                continue
            lane = cfg.lane_of(latest["image_pt"]) if cfg.lanes else None
            if lane is None:
                continue
            lane_to_tracks.setdefault(lane.name, []).append((tid, latest))

        for lane_name, tracks in lane_to_tracks.items():
            if len(tracks) < 2:
                continue
            tracks.sort(key=lambda x: (x[1]["world_pt"][0], x[1]["world_pt"][1]))
            for i in range(len(tracks) - 1):
                tid_a, a = tracks[i]
                tid_b, b = tracks[i + 1]
                dx = b["world_pt"][0] - a["world_pt"][0]
                dy = b["world_pt"][1] - a["world_pt"][1]
                gap_m = (dx * dx + dy * dy) ** 0.5
                speed = history.speed_kmh(tid_b) or 0.0
                if speed < self.min_speed:
                    continue
                gap_s = gap_m / (speed / 3.6)
                if gap_s < self.min_gap:
                    log.add(Event(
                        frame=frame_idx, t_sec=t_sec, track_id=tid_b,
                        type=self.name, severity=min(1.0, (self.min_gap - gap_s) / self.min_gap),
                        detail=f"Gap {gap_s:.2f}s ({gap_m:.1f}m) detrás de #{tid_a}",
                        image_x=b["image_pt"][0], image_y=b["image_pt"][1],
                        speed_kmh=speed,
                    ), cooldown_frames=90)
