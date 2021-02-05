from pyproj import Proj, transform
import untangle
from map import BoundingBox, Map
import pickle
from _collections import defaultdict
import math

def parse_gpx(filename, in_proj="epsg:4326", out_proj="epsg:5514"):
    gpx = untangle.parse(filename)
    result = []

    counter = defaultdict(int)

    for w in gpx.gpx.wpt:
        tmp = transform(Proj(in_proj), Proj(out_proj), w['lat'], w['lon'])
        x, y = tmp
        x = (math.radians(float(w['lon'])) + math.pi) * (256/(2 * math.pi)) * 2 ** 18
        y = 256 / (2 * math.pi) * (2 ** 18) * (math.pi - math.log(math.tan(math.pi/4 + math.radians(float(w['lat']))/2)))
        print(x, y)
        # score = w.desc.cdata
        score = "1"
        letter = chr(ord('A') + counter[score])
        result.append({"coord": tmp, "name": score+letter})
        counter[score] += 1
        print(w.name.cdata, "\t", score+letter)
    print(result)
    return result


def main():
    points = parse_gpx("export.gpx", out_proj="EPSG:3857")
    # bb = BoundingBox(points, padding=300)
    # map = Map(25_000, bb)
    # w, h = map.get_printsize()
    # print("25 - size: {}x{} [mm] - 300m padding".format(int(w * 1000), int(h * 1000)))
    #
    # map.download_map()
    # map.add_grid()

    # with open('rick.pkl', 'wb') as pickle_file:
    #     pickle.dump(map, pickle_file)

    # with open('rick.pkl', 'rb') as pickle_file:
    #     map = pickle.load(pickle_file)
    #
    # map.mark_points(points, radius_realm=60, scale=2.1)
    # map.save_img("response.png")


if __name__ == "__main__":
    main()
