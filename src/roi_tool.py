"""Herramienta interactiva para definir ROIs (carriles, líneas de stop, zonas de
conflicto) y homografía sobre un frame del video.

Uso:
    python -m src.roi_tool --video <ruta> --out configs/<nombre>.json [--frame 0]

Teclas:
    l   -> nuevo carril (polígono).
    s   -> nueva línea de stop (2 clicks).
    c   -> nueva zona de conflicto (polígono).
    h   -> 4 puntos de homografía (pide coords en metros por consola).
    n   -> nombre del objeto actual (por consola).
    d   -> direccion de carril (deg, world frame).
    p   -> setear prioridad del carril (toggle).
    Enter -> cerrar polígono actual.
    u   -> deshacer último punto.
    w   -> guardar JSON.
    r   -> reset.
    q   -> salir.

Mouse: click izquierdo añade punto al objeto actual.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np


class ROIEditor:
    def __init__(self, frame, out_path):
        self.frame = frame
        self.h, self.w = frame.shape[:2]
        self.out_path = Path(out_path)
        self.data = {
            "fps": None,
            "speed_limit_kmh": 40,
            "homography": None,
            "lanes": [],
            "stop_lines": [],
            "conflict_zones": [],
        }
        self.mode = None
        self.current_points = []
        self.current_name = None
        self.current_direction = None
        self.current_priority = False
        self.help_visible = True

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_points.append((int(x), int(y)))
            if self.mode == "stop" and len(self.current_points) == 2:
                self._commit_stop()
            elif self.mode == "homography" and len(self.current_points) == 4:
                self._commit_homography()

    def _commit_stop(self):
        name = self.current_name or f"stop_{len(self.data['stop_lines'])}"
        self.data["stop_lines"].append({
            "name": name,
            "line": [list(self.current_points[0]), list(self.current_points[1])],
        })
        print(f"  ✓ stop line '{name}' guardada")
        self._reset_current()

    def _commit_polygon(self):
        if len(self.current_points) < 3:
            print("  ⚠ un polígono necesita 3+ puntos")
            return
        pts = [list(p) for p in self.current_points]
        if self.mode == "lane":
            name = self.current_name or f"lane_{len(self.data['lanes'])}"
            entry = {"name": name, "polygon": pts}
            if self.current_direction is not None:
                entry["direction_deg"] = self.current_direction
            if self.current_priority:
                entry["priority"] = True
            self.data["lanes"].append(entry)
            print(f"  ✓ lane '{name}' (dir={self.current_direction}, prio={self.current_priority}) guardada")
        elif self.mode == "conflict":
            name = self.current_name or f"zone_{len(self.data['conflict_zones'])}"
            self.data["conflict_zones"].append({
                "name": name,
                "polygon": pts,
                "priority_lanes": [],
                "yielding_lanes": [],
            })
            print(f"  ✓ conflict zone '{name}' guardada (asignale priority/yielding lanes editando el JSON)")
        self._reset_current()

    def _commit_homography(self):
        print("\nIngresá las coords mundo (metros) para los 4 puntos clickeados:")
        world_pts = []
        for i, p in enumerate(self.current_points):
            while True:
                raw = input(f"  punto {i + 1} (img={p}) — formato 'x_m y_m': ").strip()
                try:
                    x_m, y_m = map(float, raw.split())
                    world_pts.append([x_m, y_m])
                    break
                except Exception:
                    print("    formato inválido, reintentá")
        self.data["homography"] = {
            "image_points": [list(p) for p in self.current_points],
            "world_points": world_pts,
        }
        print("  ✓ homografía guardada")
        self._reset_current()

    def _reset_current(self):
        self.mode = None
        self.current_points = []
        self.current_name = None
        self.current_direction = None
        self.current_priority = False

    def _draw(self):
        canvas = self.frame.copy()
        for lane in self.data["lanes"]:
            pts = np.array(lane["polygon"], dtype=np.int32)
            color = (60, 200, 60) if lane.get("priority") else (60, 60, 200)
            cv2.polylines(canvas, [pts], True, color, 2)
            c = pts.mean(axis=0).astype(int)
            txt = f"{lane['name']}"
            if "direction_deg" in lane:
                txt += f" {lane['direction_deg']}°"
            cv2.putText(canvas, txt, tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        for sl in self.data["stop_lines"]:
            p1, p2 = tuple(sl["line"][0]), tuple(sl["line"][1])
            cv2.line(canvas, p1, p2, (60, 200, 200), 2)
            cv2.putText(canvas, sl["name"], p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 200, 200), 1)
        for zone in self.data["conflict_zones"]:
            pts = np.array(zone["polygon"], dtype=np.int32)
            cv2.polylines(canvas, [pts], True, (180, 80, 220), 2)
            c = pts.mean(axis=0).astype(int)
            cv2.putText(canvas, zone["name"], tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 80, 220), 1)
        if self.data.get("homography"):
            for p in self.data["homography"]["image_points"]:
                cv2.circle(canvas, tuple(p), 6, (0, 255, 255), -1)
        for p in self.current_points:
            cv2.circle(canvas, tuple(p), 4, (255, 255, 255), -1)
        if self.current_points:
            color = {"lane": (60, 60, 200), "conflict": (180, 80, 220), "stop": (60, 200, 200),
                     "homography": (0, 255, 255)}.get(self.mode, (255, 255, 255))
            pts = np.array(self.current_points, dtype=np.int32)
            if len(pts) >= 2:
                cv2.polylines(canvas, [pts], False, color, 1)

        if self.help_visible:
            help_lines = [
                f"mode: {self.mode or '-'} | name: {self.current_name or '-'} | dir: {self.current_direction or '-'} | prio: {self.current_priority}",
                "l=lane  s=stop  c=conflict  h=homog  n=name  d=dir  p=prio  Enter=close  u=undo  w=save  r=reset  q=quit",
            ]
            for i, line in enumerate(help_lines):
                cv2.rectangle(canvas, (0, i * 22), (self.w, (i + 1) * 22), (0, 0, 0), -1)
                cv2.putText(canvas, line, (8, i * 22 + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return canvas

    def run(self):
        win = "roi-editor"
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(win, self.on_mouse)
        while True:
            cv2.imshow(win, self._draw())
            k = cv2.waitKey(20) & 0xFF
            if k == ord("q"):
                break
            elif k == ord("l"):
                self._reset_current(); self.mode = "lane"; print("→ modo lane (polígono)")
            elif k == ord("s"):
                self._reset_current(); self.mode = "stop"; print("→ modo stop line (2 clicks)")
            elif k == ord("c"):
                self._reset_current(); self.mode = "conflict"; print("→ modo conflict zone (polígono)")
            elif k == ord("h"):
                self._reset_current(); self.mode = "homography"; print("→ modo homografía (4 clicks)")
            elif k == ord("n"):
                self.current_name = input("nombre: ").strip() or None
            elif k == ord("d"):
                try:
                    self.current_direction = float(input("direccion deg (0=+X, 90=+Y mundo): ").strip())
                except Exception:
                    self.current_direction = None
            elif k == ord("p"):
                self.current_priority = not self.current_priority
                print(f"  prioridad = {self.current_priority}")
            elif k == 13:  # Enter
                if self.mode in ("lane", "conflict"):
                    self._commit_polygon()
            elif k == ord("u"):
                if self.current_points:
                    self.current_points.pop()
            elif k == ord("r"):
                self._reset_current()
            elif k == ord("w"):
                self.save()
        cv2.destroyAllWindows()
        self.save()

    def save(self):
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.out_path, "w") as f:
            json.dump(self.data, f, indent=2)
        print(f"\n💾 guardado: {self.out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frame", type=int, default=0)
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.video)
    cap.set(cv2.CAP_PROP_POS_FRAMES, args.frame)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise SystemExit("no pude leer el frame")
    editor = ROIEditor(frame, args.out)
    editor.run()


if __name__ == "__main__":
    main()
