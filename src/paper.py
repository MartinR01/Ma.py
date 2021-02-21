import units

A5 = (148, 210)
A4 = (210, 297)
A3 = (297, 420)
A2 = (420, 594)


class Paper:

    def __init__(self, paper_format, padding, dpi=300):
        self.dpi = dpi
        self.width_mm = paper_format[0] - 2 * padding
        self.height_mm = paper_format[1] - 2 * padding

    def get_area_px(self):
        return units.print_cm_to_pixels(self.width_mm/10), units.print_cm_to_pixels(self.height_mm/10)
