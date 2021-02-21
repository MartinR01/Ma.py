def cm_to_inch(cm):
    return cm / 2.54


def inch_to_cm(inch):
    return inch * 2.54


def printcm_to_pixels(cm, dpi):
    return int(cm_to_inch(cm) * dpi)


def pixels_to_printcm(px, dpi):
    return inch_to_cm(px / dpi)


def pixels_to_realm(px, scale, dpi):
    return inch_to_cm(px * scale / dpi) / 100


def realm_to_pixels(m, scale, dpi):
    print_cm = 100 * m / scale
    return printcm_to_pixels(print_cm, dpi)
