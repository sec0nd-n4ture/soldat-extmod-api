from struct import pack
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE
from vector_utils import Vector2D
from color import Color

'''
(s)hared(m)emorytext
'''
'''
Text struct
-------------------------------------------------------------
offs   name                 size
-------------------------------------------------------------
0x00   state                1 byte  (boolean)
0x01   type                 1 byte  (boolean) + 2 byte padding = 4 bytes
0x04   text_color           4 bytes (DWORD) 
0x08   text_shadow_color    4 bytes (DWORD)
0x0C   font_style           4 bytes (DWORD)
0x10   text_position_x      4 bytes (float)
0x14   text_position_y      4 bytes (float)
0x18   text_scale           4 bytes (float)
0x1C   shadow_scale_x       4 bytes (float)
0x20   shadow_scale_y       4 bytes (float)
0x24   wchar_ptr            4 bytes (ptr)
0x28   font_scale           4 bytes (float)
+
___________
0x2C
'''

TEXT_MAX_LENGTH = 4096

class TextStruct:
    state_offset          = 0x0
    type_offset           = 0x1
    color_offset          = 0x4
    shadow_color_offset   = 0x8
    font_style_offset     = 0xC
    position_x_offset     = 0x10
    position_y_offset     = 0x14
    text_scale_offset     = 0x18
    shadow_scale_x_offset = 0x1C
    shadow_scale_y_offset = 0x20
    wchar_ptr_offset      = 0x24
    font_scale_offset     = 0x28
    size = 0x2C

class FontStyle:
    FONT_BIG          = 0
    FONT_SMALL        = 1
    FONT_SMALL_BOLD   = 2
    FONT_SMALLEST     = 3
    FONT_MENU         = 4
    FONT_WEAPONS_MENU = 5
    FONT_WORLD        = 6


class CharacterSize:
    FONT_BIG = 15
    FONT_SMALL_BOLD = 7
    FONT_BIG_SPACING = 3
    FONT_SMALL_BOLD_SPACING = 1.5
    FONT_WEAPONS_MENU = 6.7
    FONT_WEAPONS_MENU_SPACING = 1.7

class Text:
    def __init__(self,
                 mod_api, 
                 text: str,
                 position: Vector2D,
                 color: Color,
                 shadow_color: Color,
                 scale: float,
                 shadow_scale: Vector2D,
                 font_style: FontStyle,
                 font_scale: float,
                 is_world: bool):
        self.baseAddr = None
        self.process_bridge = mod_api.soldat_bridge
        self.text_addresses = mod_api.graphics_patcher.text_addresses
        self.text_position = Vector2D.zero()
        self.scale = scale
        self.add(text, position, color, shadow_color, scale, shadow_scale, font_style, font_scale, is_world)

    def toggle(self):
        state = self.process_bridge.read(self.baseAddr + TextStruct.state_offset, 1)
        self.process_bridge.write(self.baseAddr + TextStruct.state_offset, 
                                                   (int.from_bytes(state, "little") ^ 1).to_bytes(1, "little"))
        
    def hide(self):
        self.process_bridge.write(self.baseAddr + TextStruct.state_offset, b"\x00")

    def show(self):
        self.process_bridge.write(self.baseAddr + TextStruct.state_offset, b"\x01")

    def set_pos(self, pos: Vector2D):
        self.text_position = pos
        self.process_bridge.write(self.baseAddr + TextStruct.position_x_offset, pos.to_bytes())

    def set_scale(self, scale: float):
        self.scale = scale
        self.process_bridge.write(self.baseAddr + TextStruct.text_scale_offset, pack("f", scale))

    def set_text_color(self, color: Color):
        self.process_bridge.write(self.baseAddr + TextStruct.color_offset, color.to_bytes())

    def set_shadow_color(self, color: Color):
        color_bytes = color.to_bytes()
        self.process_bridge.write(self.baseAddr + TextStruct.shadow_color_offset, color_bytes)

    def set_shadow_scale(self, scale: Vector2D):
        self.process_bridge.write(self.baseAddr + TextStruct.shadow_scale_x_offset, scale.to_bytes())

    def set_font_style(self, style: int):
        style_bytes = style.to_bytes(4, "little")
        self.process_bridge.write(self.baseAddr + TextStruct.font_style_offset, style_bytes)

    def set_font_scale(self, scale: float):
        scale_bytes = pack("f", scale)
        self.process_bridge.write(self.baseAddr + TextStruct.font_scale_offset, scale_bytes)

    def set_text(self, text: str):
        text_addr_bytes = self.process_bridge.read(self.baseAddr + TextStruct.wchar_ptr_offset, 4)
        text_addr = int().from_bytes(text_addr_bytes, "little")
        wctext = text.encode("utf-16le")
        if not text_addr:
            text_addr = self.process_bridge.allocate_memory(TEXT_MAX_LENGTH * 2, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)       
            self.process_bridge.write(text_addr, len(wctext).to_bytes(4, "little") + wctext)
            self.process_bridge.write(self.baseAddr + TextStruct.wchar_ptr_offset, (text_addr + 4).to_bytes(4, "little"))
        else:
            self.process_bridge.write(text_addr-4, len(wctext).to_bytes(4, "little") + wctext)

    def add(self, text: str,
            position: Vector2D,
            color: Color,
            shadow_color: Color,
            scale: float,
            shadow_scale: Vector2D,
            font_style: FontStyle,
            font_scale: float,
            is_world: bool):
        count = int.from_bytes(self.process_bridge.read(self.text_addresses, 4), "little", signed=False)
        new_taddr = self.text_addresses + (count * TextStruct.size) + 4
        self.baseAddr = new_taddr
        if len(text) > 0: self.set_text(text)
        else: self.set_text("")
        self.set_pos(position)
        self.set_text_color(color)
        self.set_shadow_color(shadow_color)
        self.set_scale(scale)
        self.set_shadow_scale(shadow_scale)
        self.set_font_style(font_style)
        self.set_font_scale(font_scale)
        self.process_bridge.write(new_taddr + TextStruct.type_offset, is_world.to_bytes(1, "little"))
        self.process_bridge.write(new_taddr + TextStruct.state_offset, b"\x01")
        self.process_bridge.write(self.text_addresses, (count+1).to_bytes(4, "little", signed=False))


class InterfaceText(Text):
    def __init__(self, mod_api,
                text: str, 
                position: Vector2D, 
                color: Color, 
                shadow_color: Color, 
                scale: float, 
                shadow_scale: Vector2D, 
                font_style: FontStyle, 
                font_scale: float):
        super().__init__(mod_api, text, position, color, shadow_color, scale, shadow_scale, font_style, font_scale, False)

class WorldText(Text):
    def __init__(self, mod_api, 
                text: str, 
                position: Vector2D, 
                color: Color, 
                shadow_color: Color, 
                scale: float, 
                shadow_scale: Vector2D, 
                font_style: FontStyle, 
                font_scale: float):
        super().__init__(mod_api, text, position, color, shadow_color, scale, shadow_scale, font_style, font_scale, True)