import cv2

import mapsource
from units import realm_to_pixels

class Map:

    def __init__(self, scale, bounding_box, img):
        self.scale = scale
        self.bounding_box = bounding_box
        # self.img = img
        self.__img = img

    # def download_map(self):
    #     self.__img = mapsource.MapSource(self.scale, self.bounding_box).download_map()

    def save_img(self, filename):
        cv2.imwrite(filename, self.__img)

    def mark_points(self, points, scale=1, radius_realm=20, color=(0, 0, 255), thickness=3, print_text=True, extra_offset=5, font_face=cv2.FONT_HERSHEY_DUPLEX):
        for point in points:

            _, _, dist_x = self.bounding_box.geodesic.inv(self.bounding_box.left, self.bounding_box.top, point["coord"]['lon'], self.bounding_box.top)
            _, _, dist_y = self.bounding_box.geodesic.inv(self.bounding_box.left, self.bounding_box.top, self.bounding_box.left,  point["coord"]['lat'])

            # coords = realm_to_pixels(point["coord"]['lon'] - self.bounding_box.left, self.scale), realm_to_pixels(self.bounding_box.top - point["coord"]['lat'], self.scale)
            print(dist_x, dist_y)
            coords = realm_to_pixels(dist_x, self.scale, 300), realm_to_pixels(dist_y, self.scale, 300)
            radius = realm_to_pixels(radius_realm, self.scale, 300)
            cv2.circle(self.__img, coords, radius, color, thickness)

            if print_text:
                cv2.putText(self.__img, point["name"], tuple(radius + c + extra_offset for c in coords), font_face, scale, color, thickness=2)

    def add_grid(self, meters=1000):
        km = realm_to_pixels(meters, self.scale, 300)
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

