def cm_to_inch(cm):
    return cm / 2.54


def inch_to_cm(inch):
    return inch * 2.54


def print_cm_to_pixels(cm, dpi=300):
    return int(cm_to_inch(cm) * dpi)


def pixels_to_realm(px, scale, dpi=300):
    return inch_to_cm(px * scale / dpi) / 100


def realm_to_pixels(m, scale, dpi=300):
    print_cm = 100 * m / scale
    return print_cm_to_pixels(print_cm, dpi)