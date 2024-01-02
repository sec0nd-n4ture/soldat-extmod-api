from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE
import json

SERIAL_FILE_NAME = "sharedmemory.json"
SHARED_MEMORY_DEFAULT_SIZE = 0x38

'''
SharedMemory structure:
    0x00 DWORD execution flow redirect flag
    0x04 DWORD EBX save state
    0x08 DWORD EDX save state
    0x0C DWORD EBP save state
    0x10 DWORD ESP save state
    0x14 DWORD ESI save state
    0x18 DWORD EDI save state
    0x1C DWORD function return value
    0x20 DWORD pointer to image data
    0x24 DWORD image components
    0x28 DWORD image height
    0x2C DWORD image width
    0x30 DWORD flow GfxCreateTexture flag
    0x34 DWORD flow GfxDrawSprite flag
'''

class SharedMemory:
    def __init__(self, mod_api):
        self.soldat_bridge = mod_api.soldat_bridge
        self.size = SHARED_MEMORY_DEFAULT_SIZE
        self.address = 0

        self.register_save_states = {}
        self.sm_symbol_table = {}

    def update(self, addr: int):
        if addr:
            self.address = addr
        else:
            self.address = self.soldat_bridge.allocate_memory(self.size,
                                                              MEM_COMMIT | MEM_RESERVE,
                                                              PAGE_READWRITE)
            
            print(f"Allocated shared memory @ {hex(self.address)} with size {hex(self.size)}")

        self.register_save_states = { # should add more for other registers
            "EBX": self.address + 0x4,
            "EDX": self.address + 0x8,
            "EBP": self.address + 0xC,
            "ESP": self.address + 0x10,
            "ESI": self.address + 0x14,
            "EDI": self.address + 0x18,
        }

        self.__generate_symbol_table()

    def __generate_symbol_table(self):
        self.sm_symbol_table["mem_shrd_redir_flag"] = self.get_addr_flagredir
        self.sm_symbol_table["flag_draw_loop"] = self.get_addr_flagdrawloop
        self.sm_symbol_table["flag_texture_func"] = self.get_addr_flagtexturefunc
        self.sm_symbol_table["ptr_ret_save"] = self.get_addr_returnval
        self.sm_symbol_table["ptr_image"] = self.get_addr_imageptr
        self.sm_symbol_table["ptr_imagecompr"] = self.get_addr_imagecompr
        self.sm_symbol_table["ptr_imageheight"] = self.get_addr_imageheight
        self.sm_symbol_table["ptr_imagewidth"] = self.get_addr_imagewidth
        self.sm_symbol_table["ptr_ebx_save"] = self.get_savestate("EBX")
        self.sm_symbol_table["ptr_edx_save"] = self.get_savestate("EDX")
        self.sm_symbol_table["ptr_ebp_save"] = self.get_savestate("EBP")
        self.sm_symbol_table["ptr_esp_save"] = self.get_savestate("ESP")
        self.sm_symbol_table["ptr_esi_save"] = self.get_savestate("ESI")
        self.sm_symbol_table["ptr_edi_save"] = self.get_savestate("EDI")
        
    def __str__(self) -> str:
        full_read = self.soldat_bridge.read(self.address, self.size).hex()
        ret = f"Shared Memory @ {hex(self.address)}\n" 
        ret += "___________________________________________________________________________________________________________\n"
        ret += "". join([hex(x)+" "*(8 - len(hex(x)))+"|" for x in range(0, self.size, 0x4)]) + "\n"
        ret += " ".join([full_read[i:i+8] for i in range(0, len(full_read), 8)]) + "\n"
        return ret

    def get_savestate(self, register: str):
        return self.register_save_states[register]

    @property
    def get_addr_flagredir(self):
        return self.address
    
    @property
    def get_addr_flagdrawloop(self):
        return self.address + 0x34
    
    @property
    def get_addr_flagtexturefunc(self):
        return self.address + 0x30

    @property
    def get_addr_returnval(self):
        return self.address + 0x1C

    @property
    def get_addr_imageptr(self):
        return self.address + 0x20
    
    @property
    def get_addr_imagecompr(self):
        return self.address + 0x24
    
    @property
    def get_addr_imageheight(self):
        return self.address + 0x28
    
    @property
    def get_addr_imagewidth(self):
        return self.address + 0x2C

    @property
    def get_return_value(self):
        return self.soldat_bridge.read(self.get_addr_returnval, 4)

    def null_return_value(self):
        return self.soldat_bridge.write(self.get_addr_returnval, b"\x00\x00\x00\x00")

    def push_imageptr(self, ptr: bytes):
        self.soldat_bridge.write(self.get_addr_imageptr, ptr)

    def push_imageheight(self, height: bytes):
        self.soldat_bridge.write(self.get_addr_imageheight, height)

    def push_imagewidth(self, width: bytes):
        self.soldat_bridge.write(self.get_addr_imagewidth, width)

    def push_imagecompr(self, compression: bytes):
        self.soldat_bridge.write(self.get_addr_imagecompr, compression)

    def as_bytes(self, f, arg=None) -> bytes:
        if arg:
            ret = f(arg)
        else:
            ret = f()
        return ret.to_bytes(4, "little")
    
    def serialize(self):
        with open(SERIAL_FILE_NAME, "w") as f:
            json.dump({"baseAddr": self.address}, f)
    
    def deserialize(self):
        with open(SERIAL_FILE_NAME, "r") as f:
            self.update(json.load(f)["baseAddr"])