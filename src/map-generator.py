import requests
import cv2
import numpy as np

STATUS_OK = 200
STATUS_NOT_FOUND = 404

MERITKO = 10_000


# zoomed out
# response = requests.get("https://geoportal.cuzk.cz/WMS_ZM10_PUB/service.svc/get?LAYERS=GR_ZM10&TRANSPARENT=TRUE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=XML&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A5514&_OLSALT=0.3850038833609193&BBOX=-814466.50708645,-1084332.1486039,-806273.46227613,-1076139.1037935&WIDTH=512&HEIGHT=512")

def cm_to_inch(cm):
    return cm / 2.54


def inch_to_cm(inch):
    return inch * 2.54


def inch_to_m(inch):
    return inch * 254


def cm_to_pixels(cm, dpi=300):
    return int(cm_to_inch(cm) * dpi)


def pixels_to_realm(px, dpi=300, scale=MERITKO):
    return inch_to_cm(px * scale / dpi) / 100


def get_maptile(start, end, w, h):
    response = requests.get("https://geoportal.cuzk.cz/WMS_ZM10_PUB/service.svc/get", params={
        'LAYERS': 'GR_ZM10',
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
        print(im.shape)
        return im

    elif response.status_code == STATUS_NOT_FOUND:
        print("not found")
        return None
    else:
        print("unknown code: ", response.status_code)
        return None


def main():
    # (x, y) (x, y) - jednotky jsou metry
    ORIG = (-81_44_66.50708645, -108_43_32.1486039)
    ORIG = (-82_43_52.81, -105_73_82.37)
    sirka = 6000
    vyska = 5000
    end = (ORIG[0] + sirka, ORIG[1] + vyska)
    # kde  je bod 0,0 ?????

    real_w_cm = 100 * sirka / MERITKO

    REQ_W = cm_to_pixels(real_w_cm)
    REQ_H = int(REQ_W * vyska / sirka)

    w = REQ_W
    h = REQ_H
    print(w)
    print("real", pixels_to_realm(w))

    MAX_WIDTH = 2560
    MAX_HEIGHT = 2000

    print("requestes : w {}, h {}".format(w, h))
    req_x = ORIG[0]
    req_y = ORIG[1]

    result = np.full(shape=(REQ_H, REQ_W, 3), dtype=np.uint8, fill_value=(255, 255, 255))
    print(result.shape)

    while h > 0:
        cur_h = MAX_HEIGHT if h > MAX_HEIGHT else h
        h -= cur_h

        while w > 0:
            cur_w = MAX_WIDTH if w > MAX_WIDTH else w
            w -= cur_w
            print("offset: {},{}".format(REQ_W - w, REQ_H - h))
            print("current: w {}, h {} - starting {},{}".format(cur_w, cur_h, req_x, req_y))
            result[h: h + cur_h, REQ_W - w - cur_w: REQ_W - w] = get_maptile((req_x, req_y), (req_x + pixels_to_realm(cur_w), req_y + pixels_to_realm(cur_h)), cur_w, cur_h)
            # cv2.imwrite('response.png', result)
            # exit()
            req_x += pixels_to_realm(cur_w)

        w = REQ_W
        req_x = ORIG[0]
        req_y += pixels_to_realm(cur_h)
    # cur_h
    # max rozmery 2560 x 2000
    cv2.imwrite('response.png', result)


if __name__ == "__main__":
    main()
