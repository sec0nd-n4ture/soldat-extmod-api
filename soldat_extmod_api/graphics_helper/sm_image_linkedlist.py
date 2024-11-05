from struct import unpack
from soldat_extmod_api.game_structs.gfx_structs import ImageData, TGfxRect, TGfxSprite
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D, Vector3D
from soldat_extmod_api.graphics_helper.color import Color

'''
ImageNode struct
-------------------------------------------------------------
offs   name                 size
-------------------------------------------------------------
0x00   PGfxSprite           4 bytes (ptr)
0x04   position_x           4 bytes (float) 
0x08   position_y           4 bytes (float)
0x0C   scale_x              4 bytes (float)
0x10   scale_y              4 bytes (float)
0x14   rotation_x           4 bytes (float)
0x18   rotation_y           4 bytes (float)
0x1C   rotation_z           4 bytes (float)
0x20   color                4 bytes (DWORD)
0x24   state                1 byte  (bool)
0x25   type                 1 bytes (bool)
0x26   nextnode             4 bytes (ptr)
0x2a   previousnode         4 bytes (ptr)
0x2e   pos_ptr_flag         1 byte  (bool)
0x2f   rot_ptr_flag         1 byte  (bool)
0x30   offset_pos_x         4 byte  (float)
0x34   offset_pos_y         4 byte  (float)
+
___________
0x38
'''


class ImageNode:
    last_node = None
    def __init__(self, mod_api = None,
                image_data: ImageData = None, 
                position: Vector2D = None, 
                scale: Vector2D = None, 
                rotation: Vector3D = None, 
                color: Color = None, 
                is_world: bool = None,
                base_addr: int = None) -> None:
        self.dimensions = None
        self.mod_api = mod_api
        self.soldat_bridge = mod_api.soldat_bridge
        if base_addr:
            self.base_addr = base_addr
            return
        self.graphics_manager = mod_api.graphics_manager
        self.base_addr = self.soldat_bridge.allocate_memory(0x38, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        texture = self.graphics_manager.CreateTexture(image_data.pData, image_data.components.to_bytes(4, "little", signed=False),
                                                      image_data.width.to_bytes(4, "little", signed=False),
                                                      image_data.height.to_bytes(4, "little", signed=False))
        rect = TGfxRect(0, 1, 0, 1)
        sprite = TGfxSprite(0, 0, image_data.width, image_data.height, 1, 0, rect, texture, b"\x00\x00\x00\x00")
        sprite_bytes = sprite.to_bytes()
        sprite_ptr = self.soldat_bridge.allocate_memory(len(sprite_bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.sprite_addr = sprite_ptr
        self.soldat_bridge.write(sprite_ptr, sprite_bytes)
        self.soldat_bridge.write(self.base_addr, sprite_ptr.to_bytes(4, "little"))
        self.soldat_bridge.write(self.base_addr + 0x25, is_world.to_bytes(1, "little"))
        self.set_pos(position)
        self.set_scale(scale)
        self.set_rotation(rotation)
        self.set_color(color)
        if ImageNode.last_node == None:
            ImageNode.last_node = self.base_addr
            mod_api.soldat_bridge.write(mod_api.graphics_patcher.sprite_list_head_ptr, self.base_addr.to_bytes(4, "little"))
            self.__set_next(0)
            self.__set_previous(0)
        else:
            last_image = ImageNode(mod_api, base_addr=ImageNode.last_node)
            self.__set_previous(ImageNode.last_node)
            last_image.__set_next(self.base_addr)
            self.__set_next(0)
            ImageNode.last_node = self.base_addr
        self.show()


    def toggle(self):
        state = self.soldat_bridge.read(self.base_addr + 0x24, 1)
        self.soldat_bridge.write(self.base_addr + 0x24, (int.from_bytes(state, "little") ^ 1).to_bytes(1, "little"))

    def hide(self):
        self.soldat_bridge.write(self.base_addr + 0x24, b"\x00")

    def show(self):
        self.soldat_bridge.write(self.base_addr + 0x24, b"\x01")

    def set_pos(self, pos: Vector2D):
        self.soldat_bridge.write(self.base_addr + 0x2e, b"\x00")
        self.soldat_bridge.write(self.base_addr + 0x4, pos.to_bytes())

    def set_scale(self, scale: Vector2D):
        self.soldat_bridge.write(self.base_addr + 0xc, scale.to_bytes())

    def set_color(self, color: Color):
        self.soldat_bridge.write(self.base_addr + 0x20, color.to_bytes())

    def set_rotation(self, rot: Vector3D):
        self.soldat_bridge.write(self.base_addr + 0x14, rot.to_bytes())

    def __set_next(self, addr: int):
        self.soldat_bridge.write(self.base_addr + 0x26, addr.to_bytes(4, "little"))

    def __set_previous(self, addr: int):
        self.soldat_bridge.write(self.base_addr + 0x2a, addr.to_bytes(4, "little"))

    def __get_next(self) -> int:
        raw = self.soldat_bridge.read(self.base_addr + 0x26, 4)
        return int.from_bytes(raw, "little")
    
    def __get_previous(self) -> int:
        raw = self.soldat_bridge.read(self.base_addr + 0x2a, 4)
        return int.from_bytes(raw, "little")
    
    def set_pointer_pos(self, x_addr: int, y_addr: int):
        self.hide()
        addr_qword = x_addr.to_bytes(4, "little") + y_addr.to_bytes(4, "little")
        self.soldat_bridge.write(self.base_addr + 0x4, addr_qword)
        self.soldat_bridge.write(self.base_addr + 0x2e, b"\x01")
        self.show()

    def set_pos_offset(self, offset: Vector2D):
        self.soldat_bridge.write(self.base_addr + 0x30, offset.to_bytes())

    @property
    def get_pos(self) -> Vector2D:
        return Vector2D(*unpack("ff", self.soldat_bridge.read(self.base_addr + 0x4, 8)))

    @property
    def get_dimensions(self) -> Vector2D:
        if not self.dimensions:
            self.dimensions = Vector2D(*unpack("II", self.soldat_bridge.read(self.sprite_addr + 0x8, 8)))
        return self.dimensions
    
    @property
    def get_scale(self) -> Vector2D:
        return Vector2D(*unpack("ff", self.soldat_bridge.read(self.base_addr + 0x0C, 8)))
    
    def get_rect(self) -> TGfxRect:
        return TGfxRect(*unpack("ffff", self.soldat_bridge.read(self.sprite_addr + 24, 16)))
    
    def set_rect(self, rect: TGfxRect):
        self.soldat_bridge.write(self.sprite_addr + 24, rect.to_bytes())
    
    @property
    def get_color(self) -> Color:
        return Color.from_bytes(self.soldat_bridge.read(self.base_addr + 0x20, 4))

    def insert_after(self, node: 'ImageNode'):
        if node is None or node.base_addr == self.base_addr:
            return

        if self.__get_next() == node.base_addr:
            return

        is_last_node = self.base_addr == ImageNode.last_node
        is_insertee_last_node = node.base_addr == ImageNode.last_node
        is_insertee_first_node = node.__get_previous() == 0

        if is_insertee_first_node:
            ie_next = node.__get_next()
            if ie_next == 0:
                return
            ie_next = ImageNode(self.mod_api, base_addr=ie_next)
            ie_next.__set_previous(0)
            self.soldat_bridge.write(self.mod_api.graphics_patcher.sprite_list_head_ptr, ie_next.base_addr.to_bytes(4, "little"))

        if is_insertee_last_node:
            ie_prev = node.__get_previous()
            if ie_prev == 0:
                return
            ImageNode.last_node = ie_prev
            ie_prev = ImageNode(self.mod_api, base_addr=ie_prev)
            ie_prev.__set_next(0)

        if not is_insertee_first_node and not is_insertee_last_node:
            ie_prev = ImageNode(self.mod_api, base_addr=node.__get_previous())
            ie_next = ImageNode(self.mod_api, base_addr=node.__get_next())
            ie_prev.__set_next(ie_next.base_addr)
            ie_next.__set_previous(ie_prev.base_addr)

        if is_last_node:
            ImageNode.last_node = node.base_addr
            self.__set_next(node.base_addr)
            node.__set_next(0)
        else:
            next_node = ImageNode(self.mod_api, base_addr=self.__get_next())
            next_node.__set_previous(node.base_addr)

        node.__set_previous(self.base_addr)
        node.__set_next(self.__get_next())
        self.__set_next(node.base_addr)

    def destroy(self):
        self.hide()

        is_last_node = self.base_addr == ImageNode.last_node
        is_first_node = self.__get_previous() == 0

        if is_last_node:
            prev = self.__get_previous()
            if prev != 0:
                ImageNode.last_node = prev
                ImageNode(self.mod_api, base_addr=prev).__set_next(0)
        
        if is_first_node:
            next = self.__get_next()
            if next != 0:
                ImageNode(self.mod_api, base_addr=next).__set_previous(0)
    
            self.soldat_bridge.write(self.mod_api.graphics_patcher.sprite_list_head_ptr, next.to_bytes(4, "little"))

        if not is_last_node and not is_first_node:
            prev = ImageNode(self.mod_api, base_addr=self.__get_previous())
            next = ImageNode(self.mod_api, base_addr=self.__get_next())

            prev.__set_next(next.base_addr)
            next.__set_previous(prev.base_addr)


        self.soldat_bridge.free_memory(self.sprite_addr)
        self.soldat_bridge.free_memory(self.base_addr)
        del self


