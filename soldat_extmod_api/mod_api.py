from soldat_extmod_api.metaclasses.singleton import Singleton
from soldat_extmod_api.soldat_bridge import SoldatBridge
from soldat_extmod_api.interprocess_utils import assembler
from soldat_extmod_api.interprocess_utils import patcher
from soldat_extmod_api.map_helper.map_manager import MapManager
from soldat_extmod_api.graphics_helper.vector_utils import *
from soldat_extmod_api.graphics_helper.color import *
from soldat_extmod_api.graphics_helper.graphics_patcher import GraphicsPatcher
from soldat_extmod_api.graphics_helper.graphics_manager import GraphicsManager
from soldat_extmod_api.graphics_helper.graphics_manager import *
from soldat_extmod_api.graphics_helper.sm_image_linkedlist import ImageNode
from soldat_extmod_api.graphics_helper.sm_text import InterfaceText, WorldText, FontStyle
from soldat_extmod_api.player_helper.player import Player
from soldat_extmod_api.interprocess_utils.game_addresses import addresses
from soldat_extmod_api.event_dispatcher import Event, EventDispatcher, Callable
from soldat_extmod_api.graphics_helper.gui_addon import Frame
from soldat_extmod_api.camera_helper.camera_manager import CameraManager
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

class ModAPI(metaclass=Singleton):
    def __init__(self) -> None:
        self.soldat_bridge = SoldatBridge()
        if self.soldat_bridge.pid == 0:
            exit(1)
        if self.soldat_bridge.executable_hash not in addresses.keys():
            logging.error(f"Unsupported Soldat version. Version hash: {self.soldat_bridge.executable_hash}")
            exit(1)
        self._exec_hash = self.soldat_bridge.executable_hash
        self.addresses: dict[str, int] = addresses[self._exec_hash].copy()
        self.addr_mouse_screen_pos = self.addresses["cursor_screen_pos"]
        self.assembler = assembler.Assembler()
        self.patcher: patcher.Patcher = patcher.Patcher(self)
        self.graphics_patcher = GraphicsPatcher(self)
        if not self.graphics_patcher.check_patch:
            self.graphics_patcher.apply_patch()
        self.graphics_manager = GraphicsManager(self)
        self.event_dispatcher = EventDispatcher(self)
        self.event_dispatcher.set_own_player(self.get_player(self.get_own_id()))
        self.frame = Frame()
        self.camera_manager = CameraManager(self)
    
    # ======== Graphics related methods

    def create_world_image(self, 
                           path_to_image: str, 
                           position: Vector2D = Vector2D.zero(), 
                           scale: Vector2D = Vector2D(1, 1), 
                           rotation: Vector3D = Vector3D.zero(), 
                           color: Color = WHITE) -> ImageNode:
        '''
        Creates an image in world space.

        Returns a WorldImage object.
        '''
        image_data = self.graphics_manager.load_image(path_to_image)
        return ImageNode(self, image_data, position, scale, rotation, color, True)

    def create_interface_image(self, 
                               path_to_image: str, 
                               position: Vector2D = Vector2D.zero(), 
                               scale: Vector2D = Vector2D(1, 1), 
                               rotation: Vector3D = Vector3D.zero(), 
                               color: Color = WHITE) -> ImageNode:
        '''
        Creates an image in screen space.

        Returns an InterfaceImage object.
        '''
        image_data = self.graphics_manager.load_image(path_to_image)
        return ImageNode(self, image_data, position, scale, rotation, color, False)
    
    def create_world_text(self,
                          text: str, 
                          position: Vector2D, 
                          color: Color, 
                          shadow_color: Color, 
                          scale: float, 
                          shadow_scale: Vector2D, 
                          font_style: FontStyle, 
                          font_scale: float) -> WorldText:
        '''
        Creates a text in world space.

        Returns a WorldText object.
        '''
        return WorldText(self, text, position, color, shadow_color, scale, shadow_scale, font_style, font_scale)

    def create_interface_text(self,
                              text: str, 
                              position: Vector2D, 
                              color: Color, 
                              shadow_color: Color, 
                              scale: float, 
                              shadow_scale: Vector2D, 
                              font_style: FontStyle, 
                              font_scale: float) -> InterfaceText:
        '''
        Creates a text in screen space.

        Returns an InterfaceText object.
        '''
        return InterfaceText(self, text, position, color, shadow_color, scale, shadow_scale, font_style, font_scale)

    def enable_drawing(self):
        '''
        Enables drawing of mod graphics, including texts.
        '''
        self.graphics_manager.EnableDrawing()

    def disable_drawing(self):
        '''
        Disables drawing of mod graphics, including texts.
        '''
        self.graphics_manager.DisableDrawing()

    # ======== GUI methods
    
    def get_gui_frame(self) -> Frame:
        return self.frame

    # ======== Map related methods

    def raycast(self, a: Vector2D, b: Vector2D, distance: float, max_distance: float, 
                player=False, flag=False, bullet=True, check_collider=False, team = b"\x00") -> MapManager.RaycastResult:
        return MapManager.raycast(self, a, b, distance, max_distance, player, flag, bullet, check_collider, team)
    
    def collision_test(self, pos: Vector2D, is_flag : bool = False) -> MapManager.CollisionResult:
        return MapManager.collision_test(self, pos, is_flag)

    # ======== Player related methods

    def get_player(self, id: int) -> Player:
        return Player(self, id)
    
    # blocking method
    def get_own_id(self) -> int:
        ownid = 0
        while ownid == 0:
            ownid = int.from_bytes(self.soldat_bridge.read(self.addresses["own_id"], 1), "little")
        return ownid

    def get_mouse_screen_pos(self) -> Vector2D:
        return Vector2D(*unpack("ff", self.soldat_bridge.read(self.addr_mouse_screen_pos, 8)))
    
    # ======== Event related methods

    def subscribe_event(self, callback: Callable, event: Event):
        self.event_dispatcher.subscribe(callback, event)

    def unsubscribe_event(self, callback: Callable, event: Event):
        self.event_dispatcher.unsubscribe(callback, event)

    def tick_event_dispatcher(self):
        self.event_dispatcher.observe()

    # ======== Camera related methods
        
    def take_camera_controls(self):
        self.camera_manager.take_camera_controls()

    def restore_camera_controls(self):
        self.camera_manager.restore_camera_controls()

    def take_cursor_controls(self):
        self.camera_manager.take_cursor_controls()

    def restore_cursor_controls(self):
        self.camera_manager.restore_cursor_controls()

    def set_camera_position(self, position: Vector2D):
        self.camera_manager.set_cam_pos(position)