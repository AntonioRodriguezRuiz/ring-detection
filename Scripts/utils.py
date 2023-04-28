import math

class PointsSet:
    def __init__(self, points, center, radius, circ_no):
        self.points = points
        self.center = center
        self.radius = radius
        self.circ_no = circ_no

    def parse(points, center, radius, circ_no):
        points = points
        center = center if not math.isnan(circ_no) else None
        radius = radius if not math.isnan(circ_no) else None
        circ_no = int(circ_no) if not math.isnan(circ_no) else None
        return PointsSet(points, center, radius, circ_no)

    def add_point(self, point):
        self.points.append(point)

    def is_noise(self):
        return self.circ_no is None

    def unpack(self):
        if self.is_noise():
            return [[p[0], p[1], None, None, None] for p in self.points]
        else:
            return [[p[0], p[1], self.center[0], self.center[1], self.radius, self.circ_no] for p in self.points]

    def __str__(self):
        if self.is_noise():
            return f"{len(self.points)} of Noise"
        else:
            return f"Circunference {self.circ_no} has {len(self.points)} points and center in {self.center}"