from soldat_extmod_api.interprocess_utils.kernel_wrapper import (
    GetKeyState, GetKeyboardLayout, ToUnicode
)
from enum import Enum, auto
from ctypes import c_short, create_unicode_buffer, c_byte
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
    MOUSE_KEYDOWN = auto()
    MOUSE_KEYUP = auto()
    INTERNAL_KEYPRESS = auto()
    MAP_CHANGE = auto()
    DINPUT_READY = auto()
    DINPUT_NOTREADY = auto()
    SOLDAT_BRIDGE_COLLAPSE = auto()

class VK_KEYCODE(Enum):
    VK_LBUTTON = 0x01
    VK_RBUTTON = 0x02
    VK_CANCEL = 0x03
    VK_MBUTTON = 0x04
    VK_XBUTTON1 = 0x05
    VK_XBUTTON2 = 0x06
    VK_BACK = 0x08
    VK_TAB = 0x09
    VK_CLEAR = 0x0C
    VK_RETURN = 0x0D
    VK_SHIFT = 0x10
    VK_CONTROL = 0x11
    VK_MENU = 0x12
    VK_PAUSE = 0x13
    VK_CAPITAL = 0x14
    VK_KANA = 0x15
    VK_HANGUL = 0x15
    VK_IME_ON = 0x16
    VK_JUNJA = 0x17
    VK_FINAL = 0x18
    VK_HANJA = 0x19
    VK_KANJI = 0x19
    VK_IME_OFF = 0x1A
    VK_ESCAPE = 0x1B
    VK_CONVERT = 0x1C
    VK_NONCONVERT = 0x1D
    VK_ACCEPT = 0x1E
    VK_MODECHANGE = 0x1F
    VK_SPACE = 0x20
    VK_PRIOR = 0x21
    VK_NEXT = 0x22
    VK_END = 0x23
    VK_HOME = 0x24
    VK_LEFT = 0x25
    VK_UP = 0x26
    VK_RIGHT = 0x27
    VK_DOWN = 0x28
    VK_SELECT = 0x29
    VK_PRINT = 0x2A
    VK_EXECUTE = 0x2B
    VK_SNAPSHOT = 0x2C
    VK_INSERT = 0x2D
    VK_DELETE = 0x2E
    VK_HELP = 0x2F
    VK_0 = 0x30
    VK_1 = 0x31
    VK_2 = 0x32
    VK_3 = 0x33
    VK_4 = 0x34
    VK_5 = 0x35
    VK_6 = 0x36
    VK_7 = 0x37
    VK_8 = 0x38
    VK_9 = 0x39
    VK_A = 0x41
    VK_B = 0x42
    VK_C = 0x43
    VK_D = 0x44
    VK_E = 0x45
    VK_F = 0x46
    VK_G = 0x47
    VK_H = 0x48
    VK_I = 0x49
    VK_J = 0x4A
    VK_K = 0x4B
    VK_L = 0x4C
    VK_M = 0x4D
    VK_N = 0x4E
    VK_O = 0x4F
    VK_P = 0x50
    VK_Q = 0x51
    VK_R = 0x52
    VK_S = 0x53
    VK_T = 0x54
    VK_U = 0x55
    VK_V = 0x56
    VK_W = 0x57
    VK_X = 0x58
    VK_Y = 0x59
    VK_Z = 0x5A
    VK_LWIN = 0x5B
    VK_RWIN = 0x5C
    VK_APPS = 0x5D
    VK_SLEEP = 0x5F
    VK_NUMPAD0 = 0x60
    VK_NUMPAD1 = 0x61
    VK_NUMPAD2 = 0x62
    VK_NUMPAD3 = 0x63
    VK_NUMPAD4 = 0x64
    VK_NUMPAD5 = 0x65
    VK_NUMPAD6 = 0x66
    VK_NUMPAD7 = 0x67
    VK_NUMPAD8 = 0x68
    VK_NUMPAD9 = 0x69
    VK_MULTIPLY = 0x6A
    VK_ADD = 0x6B
    VK_SEPARATOR = 0x6C
    VK_SUBTRACT = 0x6D
    VK_DECIMAL = 0x6E
    VK_DIVIDE = 0x6F
    VK_F1 = 0x70
    VK_F2 = 0x71
    VK_F3 = 0x72
    VK_F4 = 0x73
    VK_F5 = 0x74
    VK_F6 = 0x75
    VK_F7 = 0x76
    VK_F8 = 0x77
    VK_F9 = 0x78
    VK_F10 = 0x79
    VK_F11 = 0x7A
    VK_F12 = 0x7B
    VK_F13 = 0x7C
    VK_F14 = 0x7D
    VK_F15 = 0x7E
    VK_F16 = 0x7F
    VK_F17 = 0x80
    VK_F18 = 0x81
    VK_F19 = 0x82
    VK_F20 = 0x83
    VK_F21 = 0x84
    VK_F22 = 0x85
    VK_F23 = 0x86
    VK_F24 = 0x87
    VK_NUMLOCK = 0x90
    VK_SCROLL = 0x91
    VK_LSHIFT = 0xA0
    VK_RSHIFT = 0xA1
    VK_LCONTROL = 0xA2
    VK_RCONTROL = 0xA3
    VK_LMENU = 0xA4
    VK_RMENU = 0xA5
    VK_BROWSER_BACK = 0xA6
    VK_BROWSER_FORWARD = 0xA7
    VK_BROWSER_REFRESH = 0xA8
    VK_BROWSER_STOP = 0xA9
    VK_BROWSER_SEARCH = 0xAA
    VK_BROWSER_FAVORITES = 0xAB
    VK_BROWSER_HOME = 0xAC
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_STOP = 0xB2
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_LAUNCH_MAIL = 0xB4
    VK_LAUNCH_MEDIA_SELECT = 0xB5
    VK_LAUNCH_APP1 = 0xB6
    VK_LAUNCH_APP2 = 0xB7
    VK_OEM_1 = 0xBA
    VK_OEM_PLUS = 0xBB
    VK_OEM_COMMA = 0xBC
    VK_OEM_MINUS = 0xBD
    VK_OEM_PERIOD = 0xBE
    VK_OEM_2 = 0xBF
    VK_OEM_3 = 0xC0
    VK_GAMEPAD_A = 0xC3
    VK_GAMEPAD_B = 0xC4
    VK_GAMEPAD_X = 0xC5
    VK_GAMEPAD_Y = 0xC6
    VK_GAMEPAD_RIGHT_SHOULDER = 0xC7
    VK_GAMEPAD_LEFT_SHOULDER = 0xC8
    VK_GAMEPAD_LEFT_TRIGGER = 0xC9
    VK_GAMEPAD_RIGHT_TRIGGER = 0xCA
    VK_GAMEPAD_DPAD_UP = 0xCB
    VK_GAMEPAD_DPAD_DOWN = 0xCC
    VK_GAMEPAD_DPAD_LEFT = 0xCD
    VK_GAMEPAD_DPAD_RIGHT = 0xCE
    VK_GAMEPAD_MENU = 0xCF
    VK_GAMEPAD_VIEW = 0xD0
    VK_GAMEPAD_LEFT_THUMBSTICK_BUTTON = 0xD1
    VK_GAMEPAD_RIGHT_THUMBSTICK_BUTTON = 0xD2
    VK_GAMEPAD_LEFT_THUMBSTICK_UP = 0xD3
    VK_GAMEPAD_LEFT_THUMBSTICK_DOWN = 0xD4
    VK_GAMEPAD_LEFT_THUMBSTICK_RIGHT = 0xD5
    VK_GAMEPAD_LEFT_THUMBSTICK_LEFT = 0xD6
    VK_GAMEPAD_RIGHT_THUMBSTICK_UP = 0xD7
    VK_GAMEPAD_RIGHT_THUMBSTICK_DOWN = 0xD8
    VK_GAMEPAD_RIGHT_THUMBSTICK_RIGHT = 0xD9
    VK_GAMEPAD_RIGHT_THUMBSTICK_LEFT = 0xDA
    VK_OEM_4 = 0xDB
    VK_OEM_5 = 0xDC
    VK_OEM_6 = 0xDD
    VK_OEM_7 = 0xDE
    VK_OEM_8 = 0xDF
    VK_OEM_102 = 0xE2
    VK_PROCESSKEY = 0xE5
    VK_PACKET = 0xE7
    VK_ATTN = 0xF6
    VK_CRSEL = 0xF7
    VK_EXSEL = 0xF8
    VK_EREOF = 0xF9
    VK_PLAY = 0xFA
    VK_ZOOM = 0xFB
    VK_NONAME = 0xFC
    VK_PA1 = 0xFD
    VK_OEM_CLEAR = 0xFE

class KeyInfo:
    def __init__(self, vk_code: int, char: str, modifiers: set[str]):
        self.vk_code = vk_code
        self.char = char
        self.modifiers = modifiers

    def __repr__(self):
        mod_str = '+' + '+'.join(self.modifiers) if self.modifiers else ''
        return f"KeyInfo({self.vk_code:02X}{mod_str}, char='{self.char}')"

    def get_key_name(self):
        if self.char:
            return self.char
        for member in VK_KEYCODE:
            if member.value == self.vk_code:
                return member.name[3:]
        return f"VK_{self.vk_code:02X}"

class EventDispatcher:
    def __init__(self, mod_api):
        self.soldat_bridge = mod_api.soldat_bridge
        self.own_player = None
        self.graphics_patcher = mod_api.graphics_patcher
        self.mod_api = mod_api
        self.map_manager = None
        self.addr_directx_ready = mod_api.addresses["dxready"]
        self.addr_dimousestate2 = mod_api.addresses["dimousestate2"]
        self.addr_dinput_ready = mod_api.addresses["diready"]
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
        self.dinput_state = False
        self.checkpoints = []
        self.respawned = True
        self.key_prev_state = {}
        # self.pynput_listener = keyboard.Listener(on_press=self.pynput_on_keyboard_down, on_release=self.pynput_on_keyboard_up, win32_event_filter=self.win32_event_filter, suppress=False)
        # self.pynput_listener.start()
        # self.prevent_key_propagation = False


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
        elif evt_type in (
            Event.PLAYER_COLLIDE_ENTER,
            Event.PLAYER_COLLIDE_EXIT,
            Event.KEYBOARD_KEYDOWN,
            Event.KEYBOARD_KEYUP,
            Event.MOUSE_WHEEL,
            Event.INTERNAL_KEYPRESS,
            Event.MAP_CHANGE,
            Event.MOUSE_KEYDOWN,
            Event.MOUSE_KEYUP
        ):
            ret_arg = args[0]
        else:
            ret_arg = None
        if evt_type in self.callbacks:
            cbs = self.callbacks[evt_type].copy()
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
        if Event.DIRECTX_READY in self.callbacks or Event.DIRECTX_NOT_READY in self.callbacks:
            directx_state = bool.from_bytes(self.soldat_bridge.read(self.addr_directx_ready, 1), "little")
            if directx_state != self.directx_state and directx_state == True:
                self.directx_state = directx_state
                self.__dispatch(Event.DIRECTX_READY)
            if directx_state != self.directx_state and directx_state == False:
                self.__dispatch(Event.DIRECTX_NOT_READY)
            self.directx_state = directx_state
        
        if Event.DINPUT_READY in self.callbacks or Event.DINPUT_NOTREADY in self.callbacks:
            dinput_state = bool.from_bytes(self.soldat_bridge.read(self.addr_dinput_ready, 1), "little")
            if dinput_state != self.dinput_state and dinput_state == True:
                self.dinput_state = dinput_state
                self.__dispatch(Event.DINPUT_READY)
            if dinput_state != self.dinput_state and dinput_state == False:
                self.__dispatch(Event.DINPUT_NOTREADY)
            self.dinput_state = dinput_state
        
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
            c_key_state: c_short = GetKeyState(VK_KEYCODE.VK_C.value)
            if (c_key_state & 0x8000) != 0:
                self.__dispatch(Event.C_KEY_DOWN)
            elif (self.c_down):
                self.__dispatch(Event.C_KEY_UP)
            self.c_down = (c_key_state & 0x8000) != 0

        if Event.R_KEY_DOWN in self.callbacks or Event.R_KEY_UP in self.callbacks:
            r_key_state = c_short()
            r_key_state: c_short = GetKeyState(VK_KEYCODE.VK_R.value)
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
            press_count = int.from_bytes(self.soldat_bridge.read(self.graphics_patcher.keypress_buffer_inc_address, 4), "little")
            if press_count != self.keypress_count:
                self.keypress_count = press_count
                keychar = self.soldat_bridge.read(self.graphics_patcher.keypress_buffer_address, 2).decode("utf-16")
                self.__dispatch(Event.INTERNAL_KEYPRESS, keychar)

        if Event.MOUSE_WHEEL in self.callbacks:
            self.get_mouse_wheel_info()

        if Event.SOLDAT_BRIDGE_COLLAPSE in self.callbacks:
            intact = self.soldat_bridge.read(0x00400000, 2) == b"MZ"
            if not intact:
                self.__dispatch(Event.SOLDAT_BRIDGE_COLLAPSE)

        if Event.KEYBOARD_KEYDOWN in self.callbacks or Event.KEYBOARD_KEYUP in self.callbacks:
            self.poll_keyboard()

        if Event.MOUSE_KEYDOWN in self.callbacks or Event.MOUSE_KEYUP in self.callbacks:
            self.poll_mouse()

    def poll_keyboard(self):
        for vk in range(1, 255):
            if vk <= 0x6:
                continue
            current = (GetKeyState(vk) & 0x8000) != 0
            prev = self.key_prev_state.get(vk, False)
            if current != prev:
                key_info = self.get_key_info(vk)
                if current:
                    self.__dispatch(Event.KEYBOARD_KEYDOWN, key_info)
                else:
                    self.__dispatch(Event.KEYBOARD_KEYUP, key_info)
                self.key_prev_state[vk] = current

    def poll_mouse(self):
        for vk in range(0x1, 0x7):
            current = (GetKeyState(vk) & 0x8000) != 0
            prev = self.key_prev_state.get(vk, False)
            if current != prev:
                key_info = self.get_key_info(vk)
                if current:
                    self.__dispatch(Event.MOUSE_KEYDOWN, key_info)
                else:
                    self.__dispatch(Event.MOUSE_KEYUP, key_info)
                self.key_prev_state[vk] = current

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

    def get_key_info(self, vk_code):
        modifiers = set()
        if GetKeyState(0xA2) & 0x8000:
            modifiers.add('lctrl')
        if GetKeyState(0xA3) & 0x8000:
            modifiers.add('rctrl')
        if GetKeyState(0xA0) & 0x8000:
            modifiers.add('lshift')
        if GetKeyState(0xA1) & 0x8000:
            modifiers.add('rshift')
        if GetKeyState(0xA4) & 0x8000:
            modifiers.add('lalt')
        if GetKeyState(0xA5) & 0x8000:
            modifiers.add('ralt')

        char = ''
        hkl = GetKeyboardLayout(0)
        buf = create_unicode_buffer(5)
        state = (c_byte * 256)()
        ret = ToUnicode(vk_code, 0, state, buf, 5, 0)
        if ret > 0:
            char = buf.value

        return KeyInfo(vk_code, char, modifiers)
