from soldat_extmod_api.graphics_helper.math_utils import lerpf


class Color:
    def __init__(self, red: int | str = 0, 
                 green: int | str = 0, 
                 blue: int | str = 0, 
                 alpha: int | str = 0):
        
        if type(red) == str:
            red = self.color_percentage(red)
        if type(green) == str:
            green = self.color_percentage(green)
        if type(blue) == str:
            blue = self.color_percentage(blue)
        if type(alpha) == str:
            alpha = self.color_percentage(alpha)

        self.red = min(max(red, 0),255)
        self.green = min(max(green, 0),255)
        self.blue = min(max(blue, 0),255)
        self.alpha = min(max(alpha, 0),255)

    def to_bytes(self):
        return self.red.to_bytes(1, "little") + \
               self.green.to_bytes(1, "little") + \
               self.blue.to_bytes(1, "little") + \
               self.alpha.to_bytes(1, "little")
    
    def to_int(self):
        return int.from_bytes(self.to_bytes(), "big")

    @classmethod
    def from_bytes(cls, color_bytes: bytes):
        cls = Color(int().from_bytes(color_bytes[0:1], "little"),
                    int().from_bytes(color_bytes[1:2], "little"),
                    int().from_bytes(color_bytes[2:3], "little"),
                    int().from_bytes(color_bytes[3:4], "little"))
        return cls
    
    @classmethod
    def from_hex(cls, color_hex: str):
        cls = Color.from_bytes(bytes.fromhex(color_hex))
        return cls

    @staticmethod
    def lerp_color(a: 'Color', b: 'Color', step: int) -> 'Color':
        return Color(int(lerpf(a.red, b.red, step)), 
                    int(lerpf(a.green, b.green, step)), 
                    int(lerpf(a.blue, b.blue, step)), 
                    int(lerpf(a.alpha, b.alpha, step)))
    
    def color_percentage(self, perc_expr: str | int):
        max = 255
        one_perc = max / 100
        ret = 0
        if type(perc_expr) == str:
            if "%" in perc_expr:
                perc_expr = perc_expr.replace("%", "")
            int_perc = int(perc_expr)
            ret = int_perc * one_perc
        elif type(perc_expr) == int:
            ret = perc_expr * one_perc
        return int(ret)

RED = Color(255, 0, 0, 255)
GREEN = Color(0, 255, 0, 255)
BLUE = Color(0, 0, 255, 255)
WHITE = Color(255, 255, 255, 255)
BLACK = Color(0, 0, 0, 255)
YELLOW = Color(0xFF, 0xFF, 0x00, 0xFF)
SILVER = Color(0xC0, 0xC0, 0xC0, 0xFF)
BRONZE = Color(0xCD, 0x7F, 0x32, 0xFF)