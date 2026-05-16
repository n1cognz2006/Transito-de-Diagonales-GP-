import numpy as np
import cv2


def point_in_polygon(polygon_pts, pt):
    poly = np.array(polygon_pts, dtype=np.int32)
    return cv2.pointPolygonTest(poly, (float(pt[0]), float(pt[1])), False) >= 0


def segments_intersect(p1, p2, p3, p4):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def bbox_bottom_center(xyxy):
    x1, y1, x2, y2 = xyxy
    return (float((x1 + x2) / 2), float(y2))


class Homography:
    def __init__(self, image_pts, world_pts):
        src = np.array(image_pts, dtype=np.float32)
        dst = np.array(world_pts, dtype=np.float32)
        self.H, _ = cv2.findHomography(src, dst)

    def to_world(self, pt):
        p = np.array([[pt]], dtype=np.float32)
        w = cv2.perspectiveTransform(p, self.H)
        return (float(w[0, 0, 0]), float(w[0, 0, 1]))

    def to_world_batch(self, pts):
        if not pts:
            return []
        arr = np.array(pts, dtype=np.float32).reshape(-1, 1, 2)
        w = cv2.perspectiveTransform(arr, self.H)
        return [(float(x), float(y)) for x, y in w.reshape(-1, 2)]
