import json
from pathlib import Path
from .geom import point_in_polygon, segments_intersect, Homography


class Lane:
    def __init__(self, d):
        self.name = d["name"]
        self.polygon = d["polygon"]
        self.direction_deg = d.get("direction_deg")
        self.priority = d.get("priority", False)
        self.speed_limit_kmh = d.get("speed_limit_kmh")

    def contains(self, pt):
        return point_in_polygon(self.polygon, pt)


class StopLine:
    def __init__(self, d):
        self.name = d["name"]
        self.line = d["line"]
        self.applies_to_lane = d.get("applies_to_lane")
        self.stop_threshold_kmh = d.get("stop_threshold_kmh", 5.0)

    def crossed_by(self, p_prev, p_curr):
        return segments_intersect(p_prev, p_curr, self.line[0], self.line[1])


class ConflictZone:
    def __init__(self, d):
        self.name = d["name"]
        self.polygon = d["polygon"]
        self.priority_lanes = d.get("priority_lanes", [])
        self.yielding_lanes = d.get("yielding_lanes", [])

    def contains(self, pt):
        return point_in_polygon(self.polygon, pt)


class IntersectionConfig:
    def __init__(self, data):
        self.video = data.get("video")
        self.fps = data.get("fps")
        self.speed_limit_kmh = data.get("speed_limit_kmh", 40)
        self.lanes = [Lane(l) for l in data.get("lanes", [])]
        self.stop_lines = [StopLine(s) for s in data.get("stop_lines", [])]
        self.conflict_zones = [ConflictZone(c) for c in data.get("conflict_zones", [])]
        hg = data.get("homography")
        self.homography = Homography(hg["image_points"], hg["world_points"]) if hg else None

    @classmethod
    def load(cls, path):
        with open(path) as f:
            return cls(json.load(f))

    def lane_of(self, pt):
        for lane in self.lanes:
            if lane.contains(pt):
                return lane
        return None
