import numpy as np
import requests
import cv2

from units import realm_to_pixels, pixels_to_realm


class MapSource:

    def __init__(self, scale, bounding_box):
        self.scale = scale
        self.bounding_box = bounding_box

    def download_map(self, max_width=2560, max_height=2000):
        total_w = realm_to_pixels(self.bounding_box.get_width(), self.scale)
        total_h = realm_to_pixels(self.bounding_box.get_height(), self.scale)

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
                    req_x + pixels_to_realm(cur_w, self.scale), req_y + pixels_to_realm(cur_h, self.scale)), cur_w, cur_h)

                req_x += pixels_to_realm(cur_w, self.scale)

            rem_w = total_w
            req_x = self.bounding_box.left
            req_y += pixels_to_realm(cur_h, self.scale)
        # rows, cols, channels = result.shape
        # m = cv2.getRotationMatrix2D((cols/2, rows/2), 9, 1)
        # result = cv2.warpAffine(src=result, M=m, dsize=(cols, rows))
        return result

    def __get_maptile(self, start, end, w, h):
        sc = None

        # todo check at __init__ and raise custom exception
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

        if response.status_code == 200:
            print("success")
            # print(response.content)

            nparr = np.fromstring(response.content, np.uint8)
            im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if im is None:
                print(response.content)
                im = self.__get_maptile(start, end, w, h)
            print(im.shape)
            return im

        elif response.status_code == 400:
            print("not found")
            return None
        else:
            print("unknown code: ", response.status_code)
            return None

import math
import map

class MapyCzSource:

    def __init__(self, gpx, scale=50_000):
        for point in gpx:
            x, y = self.convert_to_webmercat(point['coord'])
            print(x, y)
            point['coord'] = {'x': x, 'y': y}

        print(gpx)
        self.bounding_box = map.BoundingBox(gpx)
        self.scale = scale

        self.download_map()

    def convert_to_webmercat(self, coords, zoom=18):
        zoom = 18  # 256px = 100m
        x = (math.radians(float(coords['lon'])) + math.pi) * (256 / (2 * math.pi)) * 2 ** zoom
        y = 256 / (2 * math.pi) * (2 ** zoom) * (
                math.pi - math.log(math.tan(math.pi / 4 + math.radians(float(coords['lat'])) / 2)))
        return x, y

    def download_map(self, zoom=18):
        # todo calculate zoom from scale??
        total_w = realm_to_pixels(self.bounding_box.get_width(), self.scale)
        total_h = realm_to_pixels(self.bounding_box.get_height(), self.scale)
        result = np.full(shape=(total_h, total_w, 3), dtype=np.uint8, fill_value=(255, 255, 255))

        print(math.floor(self.bounding_box.top), math.ceil(self.bounding_box.bottom))
        for idy in range(math.floor(self.bounding_box.bottom/256), math.ceil(self.bounding_box.top/256)):
            for idx in range(math.floor(self.bounding_box.left/256), math.ceil(self.bounding_box.right/256)):
                tile = self.get_maptile(zoom, idx, idy)
                cv2.imwrite("aaaaa.png", tile)

    def get_maptile(self, zoom, idx, idy):
        url = "https://mapserver.mapy.cz/turist-m/"+str(zoom)+"-"+str(idx)+"-"+str(idy)
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            print("success")
            # print(response.content)

            nparr = np.fromstring(response.content, np.uint8)
            im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if im is None:
                print(response.content)
                im = self.get_maptile(zoom, idx, idy)
            print(im.shape)
            return im
        else:
            print(response)