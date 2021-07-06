#! /usr/bin/python3
import math
import numpy as np


class InvalidRegionConversion(BaseException):
    def __init__(self, src_type, dest_type):
        self.src_type = src_type
        self.dest_type = dest_type

    def __str__(self):
        return "Conversion From {} to {} is not defined.".format(self.src_type, self.dest_type)


class Region:
    available_region_type = [
        "point",      # point type {x:1, y:1}
        "polyline",   # polyline type np.array(dtype=float), shape=(2,N)
        # polygon tpye np.array(dtype=float), shape=(2,N+1). +1 is for closing the loop
        "polygon",
        "ellipse",    # ellipse type {x:1, y:1, rx:2, ry:1, theta:radian}
        "circle",     # circle type {x:1, y:1, r:1}
        "box"        # box type {x:1, y:1, w:1, h:1}
    ]
    _circle_poly = None
    # If this value is 180, then you will get polygon with 2 degree resolution.
    _circle_poly_divider = 180

    def __init__(self):
        self.data = None
        self.region_type = None
        if self._circle_points == None:
            res = self._circle_poly_divider
            self._circle_poly = np.zeros((2, res+1), dtype=float)
            for i in range(0, res):
                self._circle_poly[0, i] = np.math.cos(np.math.pi*2/res)
                self._circle_poly[1, i] = np.math.sin(np.math.pi*2/res)
            self._circle_poly[:, -1] = self._circle_poly[:, 0]

    def _circle2poly(self, x, y, r):
        trans = np.array([[x], [y]], dtype=float)
        return (self._circle_poly * r)+trans

    def _ellipse2poly(self, x, y, rx, ry, th):
        # theta is radian
        c = np.math.cos(th)
        s = np.mat.sin(th)
        rot = np.array(((c, -s), (s, c)), dtype=float)
        trans = np.array([[x], [y]], dtype=float)
        scale = np.array(((rx, 0), (0, ry)), dtype=float)
        return np.matmul(rot, np.matmul(scale, self._circle_poly)) + trans

    def _box2poly(self, x, y, w, h):
        points = np.zeros((2, 5), float)
        points[0, :] = np.array([x, x+w, x+w, x, x], dtype=float)
        points[1, :] = np.array([y, y, y+h, y+h, y], dtype=float)

    def set_point(self, x: float, y: float):
        self.data = {'x': x, 'y': y}
        self.region_type = 'point'

    def set_polyline(self, data: np.ndarray):
        self.data = data
        self.region_type = 'polyline'

    def set_polygon(self, data: np.ndarray):
        self.data = data
        if self.data[:, 0] != self.data[:, -1]:
            self.data = np.concatenate((self.data, self.data[:, 0]), axis=1)
        self.region_type = 'polyline'

    def set_ellipse(self, x: float, y: float, rx: float, ry: float, theta: float):
        self.data = {'x': x, 'y': y, 'rx': rx, 'ry': ry, 'theta': theta}
        self.region_type = 'ellipse'

    def set_circle(self, x: float, y: float, r: float):
        self.data = {'x': x, 'y': y, 'r': r}
        self.region_type = 'circle'

    def set_box(self, x: float, y: float, w: float, h: float):
        self.data = {'x': x, 'y': y, 'w': w, 'h': h}
        self.region_type = 'box'

    def get_region_type(self):
        return self.region_type

    def get_point(self):
        if self.region_type == "point":
            return self.data
        else:
            raise InvalidRegionConversion(self.region_type, "point")

    def get_polyline(self):
        if self.region_type == "polyline":
            return self.data
        else:
            raise InvalidRegionConversion(self.region_type, "polyline")

    def get_polygon(self):
        if self.region_type == "polygon":
            return self.data
        elif self.region_type == "ellipse":
            return self._ellipse2poly(self.data['x'], self.data['y'], self.data['rx'], self.data['ry'], self.data['theta'])
        elif self.region_type == "circle":
            return self._circle2poly(self.data['x'], self.data['y'], self.data['r'])
        elif self.region_type == "box":
            return self._box2poly(self.data['x'], self.data['y'], self.data['w'], self.data['h'])
        else:
            raise InvalidRegionConversion(self.region_type, "polygon")

    def get_ellipse(self):
        if self.region_type == "ellipse":
            return self.data
        elif self.region_type == "circle":
            return {'x': self.data['x'], 'y': self.data['y'], 'rx': self.data['r'], 'ry': self.data['r'], 'theta': 0.0}
        else:
            raise InvalidRegionConversion(self.region_type, "ellipse")

    def get_circle(self):
        if self.region_type == "circle":
            return self.data
        else:
            raise InvalidRegionConversion(self.region_type, "circle")

    def get_box(self):
        if self.region_type == "box":
            return self.data
        if (self.region_type == "polyline") or (self.region_type == "polygon"):
            min_xy = np.min(self.data, axis=1)
            max_xy = np.max(self.data, axis=1)
            wh = max_xy - min_xy
            return {'x': min_xy[0], 'y': min_xy[1], 'w': wh[0], 'h': wh[1]}
        if self.region_type == "ellipse":
            cx, cy = self.data['x'], self.data['y']
            rx, ry = self.data['rx'], self.data['ry']
            th = self.data['theta']
            # colculate singular points
            sth = np.math.sin(th)
            cth = np.math.cos(th)
            sx = np.math.atan(-ry*sth / (rx * cth))
            sy = np.math.atan(ry*cth / (rx * sth))
            ss = np.array(
                [[sx, sy+np.math.pi, sx+np.math.pi, sy]], dtype=float)
            pts_org = np.concatenate((np.cos(ss), np.sin(ss)), axis=0)
            rot = np.array(((cth, -sth), (sth, cth)), dtype=float)
            trans = np.array([[cx], [cy]], dtype=float)
            scale = np.array(((rx, 0), (0, ry)), dtype=float)
            points = np.matmul(rot, np.matmul(scale, pts_org)) + trans
            # generate box
            min_xy = np.min(points, axis=1)
            max_xy = np.max(points, axis=1)
            wh = max_xy - min_xy
            return {'x': min_xy[0], 'y': min_xy[1], 'w': wh[0], 'h': wh[1]}

        if self.region_type == "circle":
            x, y = self.data['x'], self.data['y']
            r = self.data['r']
            return {'x': x-r, 'y': y-r, 'w': 2*r, 'h': 2*r}

        else:
            raise InvalidRegionConversion(self.region_type, "box")
