from soldat_extmod_api.interprocess_utils.game_addresses import addresses
from enum import Enum, auto
from soldat_extmod_api.interprocess_utils.kernel_wrapper import GetKeyState
from ctypes import c_short
from pynput import keyboard
from collections.abc import Callable
from struct import unpack

class Event(Enum):
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()
    MOUSE_HOVER = auto()
    MOUSE_WHEEL = auto()
    LCONTROL_DOWN = auto()
    LCONTROL_UP = auto()
    C_KEY_DOWN = auto()
    C_KEY_UP = auto()
    R_KEY_UP = auto()
    R_KEY_DOWN = auto()
    PLAYER_COLLIDE_ENTER = auto()
    PLAYER_COLLIDE_EXIT = auto()
    RUN_START = auto()
    RUN_FINISH = auto()
    DIRECTX_READY = auto()
    DIRECTX_NOT_READY = auto()
    PLAYER_RESPAWN = auto()
    KEYBOARD_KEYDOWN = auto()
    KEYBOARD_KEYUP = auto()
    INTERNAL_KEYPRESS = auto()
    MAP_CHANGE = auto()

# https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
class VK_KEYCODE(Enum):
    VK_LBUTTON = 0x01
    VK_RBUTTON = 0x02
    VK_LCONTROL = 0xA2
    C = 0x43
    R = 0x52


class EventDispatcher:
    def __init__(self, mod_api):
        self.soldat_bridge = mod_api.soldat_bridge
        self.own_player = None
        self.graphics_manager = mod_api.graphics_manager
        self.mod_api = mod_api
        self.map_manager = None
        self.addr_directx_ready = addresses[self.soldat_bridge.executable_hash]["dxready"]
        self.addr_dimousestate2 = addresses[self.soldat_bridge.executable_hash]["dimousestate2"]
        self.callbacks = {}
        self.lcontrol_down = 0
        self.current_map = ""
        self.c_down = 0
        self.r_down = 0
        self.mouse1_down = 0
        self.scroll_accumulator = 0
        self.player_collide = 0
        self.server_msg_count = 0
        self.keypress_count = 0
        self.directx_state = False
        self.checkpoints = []
        self.respawned = True
        self.pynput_listener = keyboard.Listener(on_press=self.pynput_on_keyboard_down, on_release=self.pynput_on_keyboard_up, win32_event_filter=self.win32_event_filter, suppress=False)
        self.pynput_listener.start()
        self.prevent_key_propagation = False


    def subscribe(self, callback: Callable, type: int):
        """
        Subscribes to an event by providing a callback function and event type.

        Args:
        - callback: The callback function to be invoked when the event is dispatched.
        - type: An integer representing the event type.

        Returns:
        - None
        """
        if self.callbacks.get(type) == None:
            self.callbacks[type] = []
        self.callbacks[type].append(callback)

    def unsubscribe(self, callback: Callable, type: int):
        """
        Unsubscribes a callback function from an event type.

        Args:
        - callback: The callback function to be unsubscribed.
        - type: An integer representing the event type.

        Returns:
        - None
        """
        if type in self.callbacks:
            callbacks = self.callbacks[type]
            if callback in callbacks:
                callbacks.remove(callback)
                if len(callbacks) == 0:
                    del self.callbacks[type]

    def __dispatch(self, evt_type, *args):
        if (evt_type == Event.MOUSE_DOWN) or \
           (evt_type == Event.MOUSE_UP) or \
           (evt_type == Event.MOUSE_HOVER):
            ret_arg = self.mod_api.get_mouse_screen_pos()
        elif (evt_type == Event.PLAYER_COLLIDE_ENTER) or \
             (evt_type == Event.PLAYER_COLLIDE_EXIT) or \
             (evt_type == Event.KEYBOARD_KEYDOWN) or \
             (evt_type == Event.KEYBOARD_KEYUP) or \
             (evt_type == Event.MOUSE_WHEEL) or \
             (evt_type == Event.INTERNAL_KEYPRESS) or \
             (evt_type == Event.MAP_CHANGE):
            ret_arg = args[0]
        else:
            ret_arg = None
        if evt_type in self.callbacks:
            cbs = self.callbacks[evt_type]
            if len(cbs) > 0:
                for cb in cbs:
                    if ret_arg:
                        cb(ret_arg)
                    else:
                        cb()

    def observe(self):
        """
        Observes events and dispatches them to the subscribed callbacks.

        This method is expected to be called inside a loop

        Returns:
        - None
        """
        if Event.RUN_FINISH in self.callbacks or \
           Event.RUN_START in self.callbacks or\
           Event.PLAYER_COLLIDE_ENTER in self.callbacks or \
           Event.PLAYER_COLLIDE_EXIT in self.callbacks:
            if len(self.checkpoints) > 0:
                player_pos = self.own_player.get_position()
                for checkpoint in self.checkpoints:
                    if checkpoint.contains_point(player_pos) and not checkpoint.active:
                        if checkpoint.previous != None and checkpoint.previous.active:
                            self.__dispatch(Event.PLAYER_COLLIDE_ENTER, checkpoint.number)
                        elif checkpoint.previous == None and not self.own_player.get_is_dead():
                            self.__dispatch(Event.PLAYER_COLLIDE_ENTER, checkpoint.number)
                            self.__dispatch(Event.RUN_START)
                        if checkpoint.next == None and checkpoint.previous != None:
                            if checkpoint.previous.active:
                                self.__dispatch(Event.RUN_FINISH)
                        break
                    # elif self.player_collide and not col_state:
                    #     self.__dispatch(Event.PLAYER_COLLIDE_EXIT, rect.number)
        if Event.DIRECTX_READY in self.callbacks or Event.DIRECTX_NOT_READY in self.callbacks:
            directx_state = bool.from_bytes(self.soldat_bridge.read(self.addr_directx_ready, 1), "little")
            if directx_state != self.directx_state and directx_state == True:
                self.directx_state = directx_state
                self.__dispatch(Event.DIRECTX_READY)
            if directx_state != self.directx_state and directx_state == False:
                self.__dispatch(Event.DIRECTX_NOT_READY)
            self.directx_state = directx_state
        
        
        if Event.MOUSE_HOVER in self.callbacks:
            self.__dispatch(Event.MOUSE_HOVER)

        if Event.MOUSE_DOWN in self.callbacks or Event.MOUSE_UP in self.callbacks:
            mouse1_state = c_short()
            mouse1_state: c_short = GetKeyState(VK_KEYCODE.VK_LBUTTON.value)
            if (mouse1_state & 0x8000) != 0:
                self.__dispatch(Event.MOUSE_DOWN)
            elif (self.mouse1_down):
                self.__dispatch(Event.MOUSE_UP)
            self.mouse1_down = (mouse1_state & 0x8000) != 0

        if Event.LCONTROL_DOWN in self.callbacks or Event.LCONTROL_UP in self.callbacks:
            lcontrol_state = c_short()
            lcontrol_state: c_short = GetKeyState(VK_KEYCODE.VK_LCONTROL.value)
            if (lcontrol_state & 0x8000) != 0:
                self.__dispatch(Event.LCONTROL_DOWN)
            elif (self.lcontrol_down):
                self.__dispatch(Event.LCONTROL_UP)
            self.lcontrol_down = (lcontrol_state & 0x8000) != 0
        
        if Event.C_KEY_DOWN in self.callbacks or Event.C_KEY_UP in self.callbacks:
            c_key_state = c_short()
            c_key_state: c_short = GetKeyState(VK_KEYCODE.C.value)
            if (c_key_state & 0x8000) != 0:
                self.__dispatch(Event.C_KEY_DOWN)
            elif (self.c_down):
                self.__dispatch(Event.C_KEY_UP)
            self.c_down = (c_key_state & 0x8000) != 0

        if Event.R_KEY_DOWN in self.callbacks or Event.R_KEY_UP in self.callbacks:
            r_key_state = c_short()
            r_key_state: c_short = GetKeyState(VK_KEYCODE.R.value)
            if (r_key_state & 0x8000) != 0:
                self.__dispatch(Event.R_KEY_DOWN)
            elif (self.r_down):
                self.__dispatch(Event.R_KEY_UP)
            self.r_down = (r_key_state & 0x8000) != 0

        if Event.PLAYER_RESPAWN in self.callbacks:
            state = self.own_player.get_is_dead()
            if not state and not self.respawned:
                self.__dispatch(Event.PLAYER_RESPAWN)
                self.respawned = True
            elif state and self.respawned:
                self.respawned = False

        if Event.MAP_CHANGE in self.callbacks and self.map_manager:
            current_map = self.map_manager.current_map_name
            if self.current_map != current_map:
                self.__dispatch(Event.MAP_CHANGE, current_map)
                self.current_map = current_map

        if Event.INTERNAL_KEYPRESS in self.callbacks:
            press_count = int().from_bytes(self.soldat_bridge.read(self.graphics_manager.keypress_buffer_inc_address, 4), "little")
            if press_count != self.keypress_count:
                self.keypress_count = press_count
                keychar = self.soldat_bridge.read(self.graphics_manager.keypress_buffer_address, 2).decode("utf-16")
                self.__dispatch(Event.INTERNAL_KEYPRESS, keychar)

        if Event.MOUSE_WHEEL in self.callbacks:
            self.get_mouse_wheel_info()

    def pynput_on_keyboard_down(self, key):
        if Event.KEYBOARD_KEYDOWN in self.callbacks:
            self.__dispatch(Event.KEYBOARD_KEYDOWN, key)

    def pynput_on_keyboard_up(self, key):
        if Event.KEYBOARD_KEYUP in self.callbacks:
            self.__dispatch(Event.KEYBOARD_KEYUP, key)

    def win32_event_filter(self, msg, data):
        self.pynput_listener._suppress = self.prevent_key_propagation

    def set_own_player(self, own_player):
        self.own_player = own_player

    def get_mouse_wheel_info(self):
        raw_data = self.soldat_bridge.read(self.addr_dimousestate2, 4)
        if raw_data:
            delta = unpack("i", raw_data)[0]
            self.scroll_accumulator += delta

            notches = self.scroll_accumulator // 120

            if notches != 0:
                self.__dispatch(Event.MOUSE_WHEEL, notches)

            self.scroll_accumulator %= 120