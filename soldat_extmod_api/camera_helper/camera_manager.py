from soldat_extmod_api.soldat_bridge import PAGE_READWRITE, MEM_COMMIT, MEM_RESERVE
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D

class CameraManager:
    def __init__(self, mod_api) -> None:
        self.api = mod_api
        self.cursor_x_setter_address = self.api.addresses["cursor_x_setter"]
        self.cursor_y_setter_address = self.api.addresses["cursor_y_setter"]

        self.get_cam_target_address = self.api.addresses["TMainForm.GetCameraTarget"]
        self.__get_cam_target_old_bytes = self.api.soldat_bridge.read(self.get_cam_target_address, 3)

        self.__old_bytes = self.api.soldat_bridge.read(self.cursor_x_setter_address, 2)
        self.__old_bytes += self.api.soldat_bridge.read(self.cursor_y_setter_address, 2)
    
        self.temp_addr = self.api.soldat_bridge.allocate_memory(32, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.api.soldat_bridge.write(self.temp_addr, (self.temp_addr+8).to_bytes(4, "little")+(self.temp_addr+12).to_bytes(4, "little"))
        self.cam_restore_xptr = self.api.addresses["cam_restore_xptr"]
        self.cam_restore_yptr = self.api.addresses["cam_restore_yptr"]
        self.cam_world_pos_vec2 = self.api.addresses["camera_world_pos_x"]

        self.misc1 = self.api.addresses["cam_misc_1"]
        self.misc2 = self.api.addresses["cam_misc_2"]
        self.misc3 = self.api.addresses["cam_misc_3"]
        self.misc4 = self.api.addresses["cam_misc_4"]
        self.misc5 = self.api.addresses["cam_misc_5"]
        self.misc6 = self.api.addresses["cam_misc_6"]
        self.misc7 = self.api.addresses["cam_misc_7"]
        self.misc8 = self.api.addresses["cam_misc_8"]
        self.misc9 = self.api.addresses["cam_misc_9"]

    def take_cursor_controls(self):
        self.api.soldat_bridge.write(self.cursor_x_setter_address, b"\x90\x90")
        self.api.soldat_bridge.write(self.cursor_y_setter_address, b"\x90\x90")
        self.api.soldat_bridge.write(self.get_cam_target_address, b"\x31\xC0\xC3") # xor eax, eax;ret
        self.set_camera_target(0)

    def restore_cursor_controls(self):
        self.api.soldat_bridge.write(self.cursor_x_setter_address, self.__old_bytes[0:2])
        self.api.soldat_bridge.write(self.cursor_y_setter_address, self.__old_bytes[2:4])
        self.api.soldat_bridge.write(self.get_cam_target_address, self.__get_cam_target_old_bytes)

    def take_camera_controls(self):
        self.api.soldat_bridge.write(self.misc1, b"\xA1"+self.temp_addr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc2, b"\xA1"+(self.temp_addr+4).to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc3, b"\xA1"+self.temp_addr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc4, b"\xA1"+(self.temp_addr+4).to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc5, b"\xA1"+self.temp_addr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc6, b"\xA1"+(self.temp_addr+4).to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc7, b"\xA1"+(self.temp_addr+4).to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc8, b"\x8B\x15"+self.temp_addr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc9, b"\x8B\x15"+(self.temp_addr+4).to_bytes(4, "little"))

    def restore_camera_controls(self):
        self.api.soldat_bridge.write(self.misc1, b"\xA1"+self.cam_restore_xptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc2, b"\xA1"+self.cam_restore_yptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc3, b"\xA1"+self.cam_restore_xptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc4, b"\xA1"+self.cam_restore_yptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc5, b"\xA1"+self.cam_restore_xptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc6, b"\xA1"+self.cam_restore_yptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc7, b"\xA1"+self.cam_restore_yptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc8, b"\x8B\x15"+self.cam_restore_xptr.to_bytes(4, "little"))
        self.api.soldat_bridge.write(self.misc9, b"\x8B\x15"+self.cam_restore_yptr.to_bytes(4, "little"))

    def set_cam_pos(self, position: Vector2D):
        self.api.soldat_bridge.write(self.cam_world_pos_vec2, position.to_bytes())

    def get_camera_target(self) -> int:
        return int.from_bytes(
            self.api.soldat_bridge.read(
                int.from_bytes(
                    self.api.soldat_bridge.read(
                        self.api.addresses["pCamera_follow_sprite"], 4
                    ), "little"
                ), 1
            )
        )

    def set_camera_target(self, target: int) -> bool:
        if target > 32 or target < 0:
            return False
        self.api.soldat_bridge.write(
            int.from_bytes(
                self.api.soldat_bridge.read(
                    self.api.addresses["pCamera_follow_sprite"], 4
                ), "little"
            ),
            target.to_bytes(1, "little")
        )
        return True
