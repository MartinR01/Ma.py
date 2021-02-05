from pyproj import Proj, transform
import untangle
from map import BoundingBox, Map
import pickle
from _collections import defaultdict


def parse_gpx(filename, in_proj="epsg:4326", out_proj="epsg:5514"):
    gpx = untangle.parse(filename)
    result = []
    in_p = Proj(in_proj)
    out_p = Proj(out_proj)

    counter = defaultdict(int)

    for w in gpx.gpx.wpt:
        tmp = transform(in_p, out_p, w['lat'], w['lon'])
        score = w.desc.cdata
        letter = chr(ord('A') + counter[score])
        result.append({"coord": tmp, "name": score+letter})
        counter[score] += 1
        print(w.name.cdata, "\t", score+letter)
    print(result)
    return result


def main():
    points = parse_gpx("test.gpx")

    bb = BoundingBox(points, padding=300)
    map = Map(25_000, bb)
    w, h = map.get_printsize()
    print("25 - size: {}x{} [mm] - 300m padding".format(int(w * 1000), int(h * 1000)))

    map.download_map()
    map.add_grid()

    # with open('rick.pkl', 'wb') as pickle_file:
    #     pickle.dump(map, pickle_file)

    # with open('rick.pkl', 'rb') as pickle_file:
    #     map = pickle.load(pickle_file)
    #
    map.mark_points(points, radius_realm=60, scale=2.1)
    map.save_img("response.png")


if __name__ == "__main__":
    main()
