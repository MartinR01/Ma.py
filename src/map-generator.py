from pyproj import Proj, transform
import gpxpy
from map import BoundingBox, Map


def parse_gpx(filename, in_proj="epsg:4326", out_proj="epsg:5514"):
    gpx_file = open(filename)
    gpx = gpxpy.parse(gpx_file)
    result = []
    in_p = Proj(in_proj)
    out_p = Proj(out_proj)

    for w in gpx.waypoints:
        tmp = transform(in_p, out_p, w.latitude, w.longitude)
        result.append({"coord": tmp, "name": w.name})
        print(tmp)
    print(result)
    return result


def main():
    points = parse_gpx("export.gpx")
    bb = BoundingBox(points, padding=300)

    map = Map(25_000, bb)
    w, h = map.get_printsize()
    print("25 - size: {}x{} [mm] - 300m padding".format(int(w * 1000), int(h * 1000)))

    map.download_map()
    map.add_grid()
    map.mark_points(points, radius_realm=30)

    map.save_img("response.png")


if __name__ == "__main__":
    main()
