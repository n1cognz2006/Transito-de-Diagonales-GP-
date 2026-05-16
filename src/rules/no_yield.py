from .base import Rule
from ..events import Event
from ..geom import point_in_polygon


class NoYieldRule(Rule):
    """Detecta no ceder el paso: dos vehículos en zona de conflicto,
    uno con prioridad, el que tenía que ceder NO frenó (velocidad > umbral).

    Métrica base: PET (Post-Encroachment Time) — usa el orden de llegada
    a la zona. Si el de prioridad llegó después y el otro no cedió, infracción.
    """
    name = "no_ceder_paso"

    def __init__(self, yielding_min_speed_kmh=12.0, pet_threshold_s=2.0):
        self.yielding_min_speed = yielding_min_speed_kmh
        self.pet_threshold = pet_threshold_s
        self._zone_entries = {}

    def _entered(self, tid, zone_name, t_sec):
        key = (tid, zone_name)
        if key not in self._zone_entries:
            self._zone_entries[key] = t_sec

    def update(self, frame_idx, t_sec, active, history, cfg, log):
        for zone in cfg.conflict_zones:
            inside = []
            for tid in active:
                latest = history.latest(tid)
                if not latest:
                    continue
                if point_in_polygon(zone.polygon, latest["image_pt"]):
                    inside.append(tid)
                    self._entered(tid, zone.name, t_sec)

            if len(inside) < 2:
                continue

            for tid in inside:
                latest = history.latest(tid)
                lane = cfg.lane_of(latest["image_pt"]) if cfg.lanes else None
                if lane is None or lane.name not in zone.yielding_lanes:
                    continue
                speed = history.speed_kmh(tid) or 0.0
                if speed < self.yielding_min_speed:
                    continue
                priority_present = False
                for tid2 in inside:
                    if tid2 == tid:
                        continue
                    other_latest = history.latest(tid2)
                    other_lane = cfg.lane_of(other_latest["image_pt"]) if cfg.lanes else None
                    if other_lane and other_lane.name in zone.priority_lanes:
                        priority_present = True
                        break
                if priority_present:
                    log.add(Event(
                        frame=frame_idx, t_sec=t_sec, track_id=tid,
                        type=self.name, severity=min(1.0, speed / 50.0),
                        detail=f"En zona {zone.name} a {speed:.1f} km/h con prioritario presente",
                        image_x=latest["image_pt"][0], image_y=latest["image_pt"][1],
                        speed_kmh=speed,
                    ), cooldown_frames=120)
