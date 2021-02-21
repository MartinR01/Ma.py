import pyproj
import math


class BoundingBox:

    def __init__(self, points, padding=200):
        self.geodesic = pyproj.Geod(ellps='WGS84')

        self.top = max(points, key=lambda x: x["coord"]['lat'])["coord"]['lat']
        self.bottom = min(points, key=lambda x: x["coord"]['lat'])["coord"]['lat']

        self.right = max(points, key=lambda x: x["coord"]['lon'])["coord"]['lon']
        self.left = min(points, key=lambda x: x["coord"]['lon'])["coord"]['lon']

        self.add_padding(padding)

    def add_padding(self, padding):
        self.left, self.top, _ = self.geodesic.fwd(self.left, self.top, -45, math.sqrt(2 * (padding ** 2)))
        self.right, self.bottom, _ = self.geodesic.fwd(self.right, self.bottom, 135, math.sqrt(2 * (padding ** 2)))

    def top_left(self):
        return self.left, self.top

    def bottom_right(self):
        return self.right, self.bottom

    def bottom_left(self):
        return self.left, self.bottom

    def top_right(self):
        return self.right, self.top

    def get_width(self):
        fwd_azimuth, back_azimuth, distance = self.geodesic.inv(self.left, self.top, self.right, self.top)
        return distance

    def get_height(self):
        fwd_azimuth, back_azimuth, distance = self.geodesic.inv(self.left, self.top, self.left, self.bottom)
        return distance
