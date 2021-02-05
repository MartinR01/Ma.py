import cv2

import mapsource
from units import realm_to_pixels


class Map:

    def __init__(self, scale, bounding_box):
        self.scale = scale
        self.bounding_box = bounding_box
        self.__img = None

    def download_map(self):
        self.__img = mapsource.MapSource(self.scale, self.bounding_box).download_map()

    def save_img(self, filename):
        cv2.imwrite(filename, self.__img)

    def mark_points(self, points, scale=1, radius_realm=20, color=(0, 0, 255), thickness=3, print_text=True, extra_offset=5, font_face=cv2.FONT_HERSHEY_DUPLEX):
        for point in points:
            coords = realm_to_pixels(point["coord"][0] - self.bounding_box.left, self.scale), realm_to_pixels(self.bounding_box.top - point["coord"][1], self.scale)
            radius = realm_to_pixels(radius_realm, self.scale)
            cv2.circle(self.__img, coords, radius, color, thickness)

            if print_text:
                cv2.putText(self.__img, point["name"], tuple(radius + c + extra_offset for c in coords), font_face, scale, color, thickness=2)

    def add_grid(self, meters=1000):
        km = realm_to_pixels(meters, self.scale)
        # vertical
        n_lines, rem = divmod(self.__img.shape[1], km)
        rem //= 2
        for line in range(n_lines + 1):
            cv2.line(self.__img, (rem + line * km, 0), (rem + line * km, self.__img.shape[0]), (0, 0, 0))
        # horizontal
        n_lines, rem = divmod(self.__img.shape[0], km)
        rem //= 2
        for line in range(n_lines + 1):
            cv2.line(self.__img, (0, rem + line * km), (self.__img.shape[1], rem + line * km), (0, 0, 0))

    def get_printsize(self):
        return self.bounding_box.get_width() / self.scale, self.bounding_box.get_height() / self.scale


class BoundingBox:

    def __init__(self, points, padding=2):
        self.right = max(points, key=lambda x: x["coord"]['x'])["coord"]['x']
        self.left = min(points, key=lambda x: x["coord"]['x'])["coord"]['x']

        self.top = max(points, key=lambda x: x["coord"]['y'])["coord"]['y']
        self.bottom = min(points, key=lambda x: x["coord"]['y'])["coord"]['y']

        if padding:
            # todo not functional for all coord systems
            self.add_padding(padding)

    def add_padding(self, padding):
        self.right += padding
        self.top += padding
        self.left -= padding
        self.bottom -= padding

    def get_top_left(self):
        return self.left, self.top

    def get_bottom_right(self):
        return self.right, self.bottom

    def get_bottom_left(self):
        return self.left, self.bottom

    def get_top_right(self):
        return self.right, self.top

    def get_width(self):
        return self.right - self.left

    def get_height(self):
        return self.top - self.bottom
