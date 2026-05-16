"""Lee el CSV de eventos y muestra un resumen legible."""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    args = ap.parse_args()

    events = []
    with open(args.csv) as f:
        for row in csv.DictReader(f):
            events.append(row)

    print(f"\n=== {Path(args.csv).name} ===")
    print(f"Total eventos: {len(events)}")
    if not events:
        return

    by_type = Counter(e["type"] for e in events)
    print("\nPor tipo:")
    for t, n in by_type.most_common():
        print(f"  {n:4d}  {t}")

    by_track = defaultdict(lambda: {"types": Counter(), "score": 0.0, "speeds": []})
    for e in events:
        tid = int(e["track_id"])
        by_track[tid]["types"][e["type"]] += 1
        by_track[tid]["score"] += float(e["severity"])
        if float(e["speed_kmh"]) > 0:
            by_track[tid]["speeds"].append(float(e["speed_kmh"]))

    print("\nTop 10 patentes (tracks) con peor índice de conducta:")
    ranked = sorted(by_track.items(), key=lambda kv: -kv[1]["score"])[:10]
    for tid, d in ranked:
        types = ", ".join(f"{t}×{n}" for t, n in d["types"].most_common())
        max_speed = max(d["speeds"]) if d["speeds"] else 0
        print(f"  track #{tid:4d}  score={d['score']:.2f}  max_v={max_speed:.0f}km/h  → {types}")

    print("\nMuestra de eventos (primeros 10):")
    for e in events[:10]:
        print(f"  t={float(e['t_sec']):5.2f}s  #{e['track_id']:>4}  {e['type']:>22}  sev={float(e['severity']):.2f}  {e['detail']}")


if __name__ == "__main__":
    main()
