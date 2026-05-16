import cv2
import numpy as np

LANE_COLOR = (60, 60, 200)
STOP_LINE_COLOR = (60, 200, 200)
CONFLICT_COLOR = (180, 80, 220)
TRACK_COLOR = (0, 200, 0)
ALERT_COLOR = (0, 0, 255)
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)


def _put(img, text, org, scale=0.5, color=TEXT_COLOR, thickness=1):
    s = max(1, int(img.shape[1] / 960))
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale * s, SHADOW_COLOR, 3 * s, cv2.LINE_AA)
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale * s, color, thickness * s, cv2.LINE_AA)


def draw_config(frame, cfg):
    overlay = frame.copy()
    for lane in cfg.lanes:
        pts = np.array(lane.polygon, dtype=np.int32)
        cv2.polylines(overlay, [pts], True, LANE_COLOR, 1, cv2.LINE_AA)
        c = pts.mean(axis=0).astype(int)
        _put(overlay, lane.name, tuple(c), 0.45, LANE_COLOR)
    for sl in cfg.stop_lines:
        p1 = tuple(map(int, sl.line[0]))
        p2 = tuple(map(int, sl.line[1]))
        cv2.line(overlay, p1, p2, STOP_LINE_COLOR, 2, cv2.LINE_AA)
        _put(overlay, sl.name, p1, 0.45, STOP_LINE_COLOR)
    for zone in cfg.conflict_zones:
        pts = np.array(zone.polygon, dtype=np.int32)
        cv2.polylines(overlay, [pts], True, CONFLICT_COLOR, 1, cv2.LINE_AA)
        c = pts.mean(axis=0).astype(int)
        _put(overlay, f"⚠ {zone.name}", tuple(c), 0.45, CONFLICT_COLOR)
    return cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)


def draw_detections(frame, detections, history, alerts_by_track):
    if detections.tracker_id is None:
        return frame
    for i, tid in enumerate(detections.tracker_id):
        if tid is None:
            continue
        x1, y1, x2, y2 = map(int, detections.xyxy[i])
        alerted = tid in alerts_by_track
        color = ALERT_COLOR if alerted else TRACK_COLOR
        s = max(1, int(frame.shape[1] / 960))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 * s)
        speed = history.speed_kmh(int(tid))
        cls = history.class_name(int(tid))
        label = f"#{int(tid)} {cls}"
        if speed is not None and speed > 0:
            label += f" {speed:.0f}km/h"
        _put(frame, label, (x1, max(15, y1 - 6)), 0.5, color)
        if alerted:
            tags = ",".join(sorted(alerts_by_track[tid]))
            _put(frame, f"! {tags}", (x1, y2 + 16), 0.45, ALERT_COLOR)
    return frame


def draw_hud(frame, frame_idx, fps, event_count, by_type):
    h, w = frame.shape[:2]
    s = max(1, int(w / 960))
    bar_h = 70 * s
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, bar_h), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)
    _put(frame, f"frame {frame_idx}  t={frame_idx / max(fps, 1):.2f}s  eventos={event_count}", (10 * s, 22 * s), 0.55)
    top = sorted(by_type.items(), key=lambda kv: -kv[1])[:5]
    line = "  ".join(f"{k}:{v}" for k, v in top) if top else "—"
    _put(frame, line, (10 * s, 50 * s), 0.5)
    return frame
