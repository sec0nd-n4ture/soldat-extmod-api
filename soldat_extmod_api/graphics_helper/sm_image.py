from struct import unpack
from soldat_extmod_api.game_structs.gfx_structs import ImageData, TGfxRect, TGfxSprite
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE
from vector_utils import Vector2D, Vector3D
from color import Color, WHITE

'''
(s)hared(m)emoryimage
'''
class Image:
    def __init__(self, mod_api,
                image_data: ImageData, 
                position: Vector2D = None, 
                scale: Vector2D = None, 
                rotation: Vector3D = None, 
                color: Color = None, 
                is_world: bool = None):
        self.mod_api = mod_api
        self.baseAddr = None
        self.spriteAddr = None
        self.graphics_manager = mod_api.graphics_manager
        self.soldat_bridge = mod_api.soldat_bridge
        self.dimensions = None
        self.add(image_data, position, scale, rotation, color, is_world)

    def toggle(self):
        state = self.soldat_bridge.read(self.baseAddr + 0x24, 1)
        self.soldat_bridge.write(self.baseAddr + 0x24, (int.from_bytes(state, "little") ^ 1).to_bytes(1, "little"))

    def hide(self):
        self.soldat_bridge.write(self.baseAddr + 0x24, b"\x00")

    def show(self):
        self.soldat_bridge.write(self.baseAddr + 0x24, b"\x01")

    def set_pos(self, pos: Vector2D):
        self.soldat_bridge.write(self.baseAddr + 0x4, pos.to_bytes())

    def set_scale(self, scale: Vector2D):
        self.soldat_bridge.write(self.baseAddr + 0xc, scale.to_bytes())

    def set_color(self, color: Color):
        self.soldat_bridge.write(self.baseAddr + 0x20, color.to_bytes())

    def set_rotation(self, rot: Vector3D):
        self.soldat_bridge.write(self.baseAddr + 0x14, rot.to_bytes())

    @property
    def get_pos(self) -> Vector2D:
        return Vector2D(*unpack("ff", self.soldat_bridge.read(self.baseAddr + 0x4, 8)))

    @property
    def get_dimensions(self) -> Vector2D:
        if not self.dimensions:
            self.dimensions = Vector2D(*unpack("II", self.soldat_bridge.read(self.spriteAddr + 0x8, 8)))
        return self.dimensions
    
    @property
    def get_scale(self) -> Vector2D:
        return Vector2D(*unpack("ff", self.soldat_bridge.read(self.baseAddr + 0x0C, 8)))
    
    def get_rect(self) -> TGfxRect:
        return TGfxRect(*unpack("ffff", self.soldat_bridge.read(self.spriteAddr + 24, 16)))
    
    def set_rect(self, rect: TGfxRect):
        self.soldat_bridge.write(self.spriteAddr + 24, rect.to_bytes())
    
    @property
    def get_color(self) -> Color:
        return Color.from_bytes(self.soldat_bridge.read(self.baseAddr + 0x20, 4))

    def serialize(self):
        return {"baseAddr": self.baseAddr, "spriteAddr": self.spriteAddr}
    
    @classmethod
    def from_serialized(cls, data: dict, mod_api):
        return cls(mod_api.graphics_manager, baseAddr=data["baseAddr"], spriteAddr=data["spriteAddr"])
    
    def add(self, image_data: ImageData, position: Vector2D, scale: Vector2D, rotation: Vector3D, color: Color, is_world: bool):
        tx = self.graphics_manager.CreateTexture(image_data.pData, image_data.components.to_bytes(4, "little", signed=False),
                            image_data.width.to_bytes(4, "little", signed=False),
                            image_data.height.to_bytes(4, "little", signed=False))
        rect = TGfxRect(0, 1, 0, 1)
        sprite = TGfxSprite(0, 0, image_data.width, image_data.height, 1, 0, rect, tx, b"\x00\x00\x00\x00")
        sprite_bytes = sprite.to_bytes()
        sprite_ptr = self.soldat_bridge.allocate_memory(len(sprite_bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.soldat_bridge.write(sprite_ptr, sprite_bytes)
        count = int.from_bytes(self.soldat_bridge.read(self.mod_api.graphics_patcher.sprite_addresses, 4), "little", signed=False)
        new_saddr = self.mod_api.image_address_cache.get()
        new_saddr = new_saddr if new_saddr else self.mod_api.graphics_patcher.sprite_addresses + (count * 0x26) + 4
        self.soldat_bridge.write(self.mod_api.graphics_patcher.sprite_addresses, (count+1).to_bytes(4, "little", signed=False))
        self.soldat_bridge.write(new_saddr, sprite_ptr.to_bytes(4, "little"))
        self.soldat_bridge.write(new_saddr + 0x4, position.to_bytes()) 
        self.soldat_bridge.write(new_saddr + 0xc, scale.to_bytes())
        self.soldat_bridge.write(new_saddr + 0x14, rotation.to_bytes()) 
        self.soldat_bridge.write(new_saddr + 0x20, color.to_bytes())
        self.soldat_bridge.write(new_saddr + 0x24, b"\x01")
        self.soldat_bridge.write(new_saddr + 0x25, is_world.to_bytes(1, "little"))
        self.baseAddr = new_saddr
        self.spriteAddr = sprite_ptr

    def destroy(self):
        count = int.from_bytes(self.soldat_bridge.read(self.mod_api.graphics_patcher.sprite_addresses, 4), "little", signed=False)
        self.soldat_bridge.write(self.mod_api.graphics_patcher.sprite_addresses, (count-1).to_bytes(4, "little", signed=False))
        self.soldat_bridge.free_memory(self.spriteAddr + 28)
        self.hide()
        self.soldat_bridge.write(self.baseAddr, b"\xff\xff\xff\xff")
        self.mod_api.image_address_cache.add(self.baseAddr)
        del self

class InterfaceImage(Image):
    def __init__(self, mod_api, image_data: ImageData, 
                position: Vector2D = Vector2D.zero(), 
                scale: Vector2D = Vector2D(1, 1), 
                rotation: Vector3D = Vector3D.zero(), 
                color: Color = WHITE):
        super().__init__(mod_api, image_data, position, scale, rotation, color, False)

    def serialize(self):
        return {"baseAddr": self.baseAddr,
                "spriteAddr": self.spriteAddr,
                "type": 0,
                "position": (self.get_pos.x, self.get_pos.y),
                "scale": (self.get_scale.x, self.get_scale.y)}

    def set_pos(self, pos: Vector2D):
        return super().set_pos(pos)

class WorldImage(Image):
    def __init__(self, mod_api, image_data: ImageData, 
                position: Vector2D = Vector2D.zero(), 
                scale: Vector2D = Vector2D(1, 1), 
                rotation: Vector3D = Vector3D.zero(), 
                color: Color = WHITE):
        super().__init__(mod_api, image_data, position, scale, rotation, color, True)

    def serialize(self):
        return {"baseAddr": self.baseAddr,
                "spriteAddr": self.spriteAddr,
                "type": 0,
                "position": (self.get_pos.x, self.get_pos.y),
                "scale": (self.get_scale.x, self.get_scale.y)}

    def set_pos(self, pos: Vector2D):
        return super().set_pos(pos)

class ImageAddressCache:
    def __init__(self) -> None:
        self.cache = []

    def add(self, address: int) -> None:
        self.cache.append(address)

    def get(self) -> int | None:
        return None if not self.cache else self.cache.pop(0)