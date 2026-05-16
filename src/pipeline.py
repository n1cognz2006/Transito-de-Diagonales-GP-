import argparse
import json
import time
from pathlib import Path

import cv2

from .config import VIDEOS_OUT, EVENTS_DIR, SNAPSHOTS, YOLO_MODEL_DEFAULT
from .roi import IntersectionConfig
from .tracker import VehicleTracker, TrackHistory
from .events import EventLog
from .geom import bbox_bottom_center
from .rules import ALL_RULES
from .annotate import draw_config, draw_detections, draw_hud


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="Ruta al video de entrada")
    ap.add_argument("--config", required=True, help="JSON con ROIs / homografía / límites")
    ap.add_argument("--model", default=str(YOLO_MODEL_DEFAULT))
    ap.add_argument("--out", default=None, help="Video anotado de salida")
    ap.add_argument("--events", default=None, help="CSV de eventos de salida")
    ap.add_argument("--device", default=None, help="cuda, cuda:0, cpu, etc.")
    ap.add_argument("--start", type=float, default=0, help="Segundo inicial")
    ap.add_argument("--duration", type=float, default=None, help="Duración en segundos (None=todo)")
    ap.add_argument("--no-display", action="store_true")
    return ap.parse_args()


def main():
    args = parse_args()
    video_path = Path(args.video)
    cfg = IntersectionConfig.load(args.config)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise SystemExit(f"No pude abrir {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or cfg.fps or 30
    cfg.fps = fps
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    start_frame = int(args.start * fps)
    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    stop_frame = total_frames
    if args.duration is not None:
        stop_frame = min(total_frames, start_frame + int(args.duration * fps))

    out_dir = Path(args.out).parent if args.out else VIDEOS_OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else (VIDEOS_OUT / f"{video_path.stem}_annotated.mp4")
    events_path = Path(args.events) if args.events else (EVENTS_DIR / f"{video_path.stem}_events.csv")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W, H))

    tracker = VehicleTracker(model_path=args.model, device=args.device)
    history = TrackHistory(max_len=int(fps * 6))
    log = EventLog(events_path)
    rules = [R() for R in ALL_RULES]

    t0 = time.time()
    frame_idx = start_frame

    while True:
        ok, frame = cap.read()
        if not ok or frame_idx >= stop_frame:
            break

        detections = tracker(frame)

        active_ids = []
        if detections.tracker_id is not None:
            for i, tid in enumerate(detections.tracker_id):
                if tid is None:
                    continue
                tid = int(tid)
                cls_id = int(detections.class_id[i]) if detections.class_id is not None else 2
                xyxy = detections.xyxy[i]
                image_pt = bbox_bottom_center(xyxy)
                world_pt = cfg.homography.to_world(image_pt) if cfg.homography else None
                lane = cfg.lane_of(image_pt) if cfg.lanes else None
                history.update(
                    frame_idx=frame_idx,
                    t_sec=frame_idx / fps,
                    track_id=tid,
                    image_pt=image_pt,
                    world_pt=world_pt,
                    class_id=cls_id,
                    lane_name=lane.name if lane else None,
                )
                active_ids.append(tid)

        for rule in rules:
            rule.update(frame_idx, frame_idx / fps, active_ids, history, cfg, log)

        alerts_by_track = {}
        for e in log.events[-60:]:
            if (frame_idx - e.frame) <= int(fps * 2):
                alerts_by_track.setdefault(e.track_id, set()).add(e.type)

        annotated = draw_config(frame, cfg)
        annotated = draw_detections(annotated, detections, history, alerts_by_track)
        by_type = {}
        for e in log.events:
            by_type[e.type] = by_type.get(e.type, 0) + 1
        annotated = draw_hud(annotated, frame_idx, fps, len(log.events), by_type)
        writer.write(annotated)

        if not args.no_display:
            cv2.imshow("transito", annotated)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        frame_idx += 1
        if frame_idx % 100 == 0:
            elapsed = time.time() - t0
            eta = (stop_frame - frame_idx) * elapsed / max(frame_idx - start_frame, 1)
            print(f"frame {frame_idx}/{stop_frame}  events={len(log.events)}  elapsed={elapsed:.1f}s  ETA~{eta:.0f}s")

    cap.release()
    writer.release()
    if not args.no_display:
        cv2.destroyAllWindows()

    log.write()
    summary = log.per_track_summary()
    summary_path = events_path.with_suffix(".summary.json")
    with open(summary_path, "w") as f:
        json.dump({str(k): v for k, v in summary.items()}, f, indent=2)

    print(f"\nVideo anotado: {out_path}")
    print(f"CSV de eventos: {events_path}")
    print(f"Resumen por track: {summary_path}")
    print(f"Total de eventos: {len(log.events)}")


if __name__ == "__main__":
    main()
