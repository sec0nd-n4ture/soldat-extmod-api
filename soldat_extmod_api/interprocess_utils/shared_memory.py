from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE
from struct import pack
import json

SERIAL_FILE_NAME = "sharedmemory.json"
SHARED_MEMORY_DEFAULT_SIZE = 0x78

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
    0x38 DWORD flow CreateShader flag
    0x3C DWORD pointer to shader source
    0x40 DWORD shader type
    0x44 DWORD flow pglCreateProgram flag
    0x48 DWORD shader handle
    0x4C DWORD prog handle
    0x50 DWORD flow pglAttachShader flag
    0x54 DWORD flow pglLinkProgram flag
    0x58 DWORD ptr uniform name
    0x5C DWORD flow CreateFrameBuffer flag
    0x60 DWORD flow pglGetUniformLocation
    0x64 DWORD uniform location
    0x68 DWORD ptr float swizzle
    0x6C DWORD swizzle count
    0x70 DWORD flow glUniformf
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
        self.sm_symbol_table["flag_shadercreate_func"] = self.get_addr_flagshadercreate
        self.sm_symbol_table["flag_progcreate_func"] = self.get_addr_flagprogcreate
        self.sm_symbol_table["flag_attachshader_func"] = self.get_addr_flagattachshader
        self.sm_symbol_table["flag_linkprog_func"] = self.get_addr_flaglinkprogram
        self.sm_symbol_table["flag_fbocreate_func"] = self.get_addr_flagcreatefbo
        self.sm_symbol_table["flag_getuniformloc_func"] = self.get_addr_flag_uniform
        self.sm_symbol_table["flag_setuniformf_func"] = self.get_addr_flaguniformf
        self.sm_symbol_table["swizzle_count"] = self.get_addr_swizzle_count
        self.sm_symbol_table["ptr_float_swizzle"] = self.get_addr_float_swizzle
        self.sm_symbol_table["uniform_location"] = self.get_addr_uniform_location
        self.sm_symbol_table["ptr_ret_save"] = self.get_addr_returnval
        self.sm_symbol_table["ptr_image"] = self.get_addr_imageptr
        self.sm_symbol_table["ptr_shadertype"] = self.get_addr_shader_type
        self.sm_symbol_table["ptr_shadersource"] = self.get_addr_shader_source
        self.sm_symbol_table["ptr_uniformname"] = self.get_addr_uniform_name
        self.sm_symbol_table["ptr_proghandle"] = self.get_addr_prog_handle
        self.sm_symbol_table["ptr_shaderhandle"] = self.get_addr_shader_handle
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
    def get_addr_shader_type(self):
        return self.address + 0x40

    @property
    def get_addr_shader_source(self):
        return self.address + 0x3C

    @property
    def get_addr_prog_handle(self):
        return self.address + 0x4C

    @property
    def get_addr_shader_handle(self):
        return self.address + 0x48

    @property
    def get_addr_flagshadercreate(self):
        return self.address + 0x38

    @property
    def get_addr_flagprogcreate(self):
        return self.address + 0x44

    @property
    def get_addr_flagattachshader(self):
        return self.address + 0x50

    @property
    def get_addr_flaglinkprogram(self):
        return self.address + 0x54

    @property
    def get_addr_flagcreatefbo(self):
        return self.address + 0x5C

    @property
    def get_addr_uniform_name(self):
        return self.address + 0x58
    
    @property
    def get_addr_uniform_location(self):
        return self.address + 0x64

    @property
    def get_addr_float_swizzle(self):
        return self.address + 0x68

    @property
    def get_addr_swizzle_count(self):
        return self.address + 0x6C

    @property
    def get_addr_flaguniformf(self):
        return self.address + 0x70

    @property
    def get_addr_flag_uniform(self):
        return self.address + 0x60

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

    def push_shader_source(self, source: str) -> int:
        src = source.encode()+b"\x00"
        addr = self.soldat_bridge.allocate_memory(
            len(src)+8,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_READWRITE
        )
        self.soldat_bridge.write(addr, b"\x01\x00\x00\x00"+len(src).to_bytes(4, "little") + src)
        self.soldat_bridge.write(self.get_addr_shader_source, (addr+8).to_bytes(4, "little"))
        return addr

    def push_uniform_name(self, uniform: str) -> int:
        uform = uniform.encode()+b"\x00"
        addr = self.soldat_bridge.allocate_memory(
            len(uform)+8,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_READWRITE
        )
        self.soldat_bridge.write(addr, b"\x01\x00\x00\x00"+len(uform).to_bytes(4, "little") + uform)
        self.soldat_bridge.write(self.get_addr_uniform_name, (addr+8).to_bytes(4, "little"))
        return addr

    def push_shader_type(self, shader_type: int):
        self.soldat_bridge.write(self.get_addr_shader_type, shader_type.to_bytes(4, "little"))

    def push_shader_handle(self, shader_handle: int):
        self.soldat_bridge.write(self.get_addr_shader_handle, shader_handle.to_bytes(4, "little"))

    def push_prog_handle(self, prog_handle: int):
        self.soldat_bridge.write(self.get_addr_prog_handle, prog_handle.to_bytes(4, "little"))

    def push_uniform_location(self, uniform_location: bytes):
        self.soldat_bridge.write(self.get_addr_uniform_location, uniform_location)

    def push_float_swizzle(self, floats: tuple[float]):
        floats_swizzle = b"".join(pack("f", f) for f in floats)
        if not hasattr(self, "swizzle_memory_addr"):
            self.swizzle_memory_addr = self.soldat_bridge.read(self.get_addr_float_swizzle, 4)
            self.swizzle_memory_addr = int.from_bytes(self.swizzle_memory_addr, "little")
        self.soldat_bridge.write(self.swizzle_memory_addr, floats_swizzle)

    def push_swizzle_count(self, count: int):
        self.soldat_bridge.write(self.get_addr_swizzle_count, (count - 1).to_bytes(4, "little"))

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
