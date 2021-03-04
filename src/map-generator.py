from pyproj import Proj, transform
import untangle
from map import Map
import pickle
from _collections import defaultdict
from boundingbox import BoundingBox
import math
import mapsource
import paper


def parse_gpx(filename, in_proj="epsg:4326", out_proj="epsg:5514"):
    gpx = untangle.parse(filename)
    result = []

    counter = defaultdict(int)

    for w in gpx.gpx.wpt:
        # tmp = transform(Proj(in_proj), Proj(out_proj), w['lat'], w['lon'])
        # x, y = tmp
        # print(x, y)

        # score = w.desc.cdata
        score = "1"
        letter = chr(ord('A') + counter[score])
        result.append({"coord": {'lat': w['lat'], 'lon': w['lon']}, "name": score + letter})
        counter[score] += 1
        print(w.name.cdata, "\t", score + letter)
    print(result)
    return result


def main():
    gpx = parse_gpx("test_gpx/pno22.gpx")
    bb = BoundingBox(gpx, padding=500)
    page = paper.Paper(paper.A4, 10, 300)

    mapsrc = mapsource.MapyCzSource(bb, 16, page)
    print("scale:", mapsrc.scale)
    img = mapsrc.download_map()

    mp = Map(mapsrc.scale, bb, img)
    # mp = Map(72223.822090, bb, img)

    mp.mark_points(gpx, radius_realm=30)
    mp.add_grid()

    mp.save_img("result.png")


if __name__ == "__main__":
    main()
