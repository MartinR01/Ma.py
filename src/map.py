import numpy as np
import requests
import cv2

STATUS_OK = 200
STATUS_NOT_FOUND = 404

class Map:
    __img = None

    def __init__(self, scale, bounding_box):
        self.scale = scale
        self.bounding_box = bounding_box

    def download_map(self, max_width=2560, max_height=2000):
        total_w = self.realm_to_pixels(self.bounding_box.get_width())
        total_h = self.realm_to_pixels(self.bounding_box.get_height())

        rem_w = total_w
        rem_h = total_h

        result = np.full(shape=(total_h, total_w, 3), dtype=np.uint8, fill_value=(255, 255, 255))
        req_x, req_y = self.bounding_box.get_bottom_left()

        while rem_h > 0:
            cur_h = max_height if rem_h > max_height else rem_h
            rem_h -= cur_h

            while rem_w > 0:
                cur_w = max_width if rem_w > max_width else rem_w
                rem_w -= cur_w

                result[rem_h: rem_h + cur_h, total_w - rem_w - cur_w: total_w - rem_w] = self.__get_maptile((req_x, req_y), (
                    req_x + self.pixels_to_realm(cur_w), req_y + self.pixels_to_realm(cur_h)), cur_w, cur_h)

                req_x += self.pixels_to_realm(cur_w)

            rem_w = total_w
            req_x = self.bounding_box.left
            req_y += self.pixels_to_realm(cur_h)
        self.__img = result
        return result

    def save_img(self, filename):
        cv2.imwrite(filename, self.__img)

    def __get_maptile(self, start, end, w, h):
        sc = None
        if self.scale == 10_000:
            sc = '10'
        elif self.scale == 25_000:
            sc = '25'

        response = requests.get("https://geoportal.cuzk.cz/WMS_ZM"+sc+"_PUB/service.svc/get", params={
            'LAYERS': 'GR_ZM'+sc,
            'TRANSPARENT': 'TRUE',
            'FORMAT': 'Image/png',
            'VERSION': '1.3.0',
            'EXCEPTIONS': 'XML',
            'SERVICE': 'WMS',
            'REQUEST': 'GetMap',
            'STYLES': '',
            'CRS': 'EPSG:5514',
            '_OLSALT': '0.3850038833609193',
            'BBOX': '{},{},{},{}'.format(start[0], start[1], end[0], end[1]),
            'WIDTH': w,
            'HEIGHT': h
        })

        if response.status_code == STATUS_OK:
            print("success")
            # print(response.content)

            nparr = np.fromstring(response.content, np.uint8)
            im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if im is None:
                print(response.content)
                im = self.__get_maptile(start, end, w, h)
            print(im.shape)
            return im

        elif response.status_code == STATUS_NOT_FOUND:
            print("not found")
            return None
        else:
            print("unknown code: ", response.status_code)
            return None

    def cm_to_inch(self, cm):
        return cm / 2.54

    def inch_to_cm(self, inch):
        return inch * 2.54

    def print_cm_to_pixels(self, cm, dpi=300):
        return int(self.cm_to_inch(cm) * dpi)

    def pixels_to_realm(self, px, dpi=300):
        return self.inch_to_cm(px * self.scale / dpi) / 100

    def realm_to_pixels(self, m, dpi=300):
        print_cm = 100 * m / self.scale
        return self.print_cm_to_pixels(print_cm, dpi)

    def get_printsize(self):
        return self.bounding_box.get_width() / self.scale, self.bounding_box.get_height() / self.scale

    def mark_points(self, points, radius_realm=20, color=(0, 0, 255), thickness=3, print_text=True, extra_offset=5, font_face=cv2.FONT_HERSHEY_DUPLEX):
        for point in points:
            coords = self.realm_to_pixels(point["coord"][0] - self.bounding_box.left), self.realm_to_pixels(self.bounding_box.top - point["coord"][1])
            radius = self.realm_to_pixels(radius_realm)
            cv2.circle(self.__img, coords, radius, color, thickness)

            if print_text:
                cv2.putText(self.__img, point["name"], tuple(radius + c + extra_offset for c in coords), font_face, 1.0, color, thickness=2)

    def add_grid(self, meters=1000):
        km = self.realm_to_pixels(meters)
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


class BoundingBox:

    def __init__(self, points, padding=0):
        self.right = max(points, key=lambda x: x["coord"][0])["coord"][0]
        self.left = min(points, key=lambda x: x["coord"][0])["coord"][0]

        self.top = max(points, key=lambda x: x["coord"][1])["coord"][1]
        self.bottom = min(points, key=lambda x: x["coord"][1])["coord"][1]

        if padding:
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
