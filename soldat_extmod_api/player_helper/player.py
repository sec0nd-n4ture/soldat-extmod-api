from soldat_extmod_api.interprocess_utils.game_addresses import addresses
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D, Vector2Ds
from soldat_extmod_api.metaclasses.singleton import Singleton
from struct import unpack

class Player:
    def __init__(self, mod_api, id: int):
        self.id = id
        self.soldat_bridge = mod_api.soldat_bridge
        _exec_hash = self.soldat_bridge.executable_hash
        self.tsprite_object_addr =   addresses[_exec_hash]["player_base"] + ((self.id - 1) * 0xC5D0)
        self.mouse_world_pos_addr =  addresses[_exec_hash]["player_base"] + (0x18ba * self.id) * 8 - 0x618
        self.position_addr =         addresses[_exec_hash]["player_sprite_base"] + self.id * 8 + 0x228
        self.velocity_addr =         addresses[_exec_hash]["player_sprite_base"] + self.id * 8 + 0x13a8
        self.first_keystates_addr =  addresses[_exec_hash]["player_base"] + (0x18ba * self.id) * 8 - 0x61c
        self.second_keystates_addr = addresses[_exec_hash]["player_base"] + (0x18ba * self.id) * 8 - 0x612
        self.is_dead_addr =          addresses[_exec_hash]["player_base"] + ((self.id - 1) * 0xC5D0) + 1
        self.player_team_addr =      addresses[_exec_hash]["player_base"] + (0x18ba * self.id) * 8 - 0xC5D0 + 0xC18C
        self.transparency_addr =     addresses[_exec_hash]["player_base"] + (self.id * 0xC5D0) + 0x21
        self.active_addr =           addresses[_exec_hash]["player_base"] + ((self.id - 1) * 0xC5D0)


    def get_position(self) -> Vector2D:
        return Vector2D(*unpack("ff", self.soldat_bridge.read(self.position_addr, 8)))

    def get_position_bytes(self):
        return self.soldat_bridge.read(self.position_addr, 8)
    
    def set_position(self, position: Vector2D | bytes):
        if isinstance(position, bytes):
            return self.soldat_bridge.write(self.position_addr, position)
        self.soldat_bridge.write(self.position_addr, position.to_bytes())


    def get_velocity(self) -> Vector2D:
        return Vector2D(*unpack("ff", self.soldat_bridge.read(self.velocity_addr, 8)))
    
    def set_velocity(self, velocity: Vector2D | bytes):
        if isinstance(velocity, bytes):
            return self.soldat_bridge.write(self.velocity_addr, velocity)
        self.soldat_bridge.write(self.velocity_addr, velocity.to_bytes())
    
    
    def get_mouse_world_pos(self) -> Vector2Ds:
        return Vector2Ds(*unpack("hh", self.soldat_bridge.read(self.mouse_world_pos_addr, 4)))

    def set_mouse_world_pos(self, position: Vector2Ds | bytes):
        if isinstance(position, bytes):
            assert(len(position) == 4)
            return self.soldat_bridge.write(self.mouse_world_pos_addr, position)
        self.soldat_bridge.write(self.mouse_world_pos_addr, position.to_bytes())


    def get_is_dead(self) -> bool:
        return bool.from_bytes(self.soldat_bridge.read(self.is_dead_addr, 1), "little")

    def get_first_keystates(self) -> bytes:
        return self.soldat_bridge.read(self.first_keystates_addr, 4)
    
    def set_first_keystates(self, keystates: bytes):
        self.soldat_bridge.write(self.first_keystates_addr, keystates)
    
    def get_second_keystates(self) -> bytes:
        return self.soldat_bridge.read(self.second_keystates_addr, 9)

    def set_second_keystates(self, keystates: bytes):
        assert(len(keystates) == 9)
        self.soldat_bridge.write(self.second_keystates_addr, keystates)

    def get_transparency(self) -> bytes:
        return self.soldat_bridge.read(self.transparency_addr, 1)

    def set_transparency(self, transparency: bytes):
        self.soldat_bridge.write(self.transparency_addr, transparency)

    @property
    def team(self) -> int:
        return int.from_bytes(self.soldat_bridge.read(self.player_team_addr, 1), "little")
    
    @property
    def active(self) -> bool:
        return bool.from_bytes(self.soldat_bridge.read(self.active_addr, 1), "little")
    
    def set_active(self, state: bool | bytes):
        if isinstance(state, bytes):
            return self.soldat_bridge.write(self.active_addr, state)
        self.soldat_bridge.write(self.active_addr, state.to_bytes(1, "little"))