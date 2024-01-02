from game_addresses import addresses
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE


class Patcher:
    from mod_api import ModAPI
    def __init__(self, mod_api: ModAPI):
        self.soldat_bridge = mod_api.soldat_bridge
        self.assembler = mod_api.assembler
        exec_hash = self.soldat_bridge.executable_hash
        ntdll_base = self.soldat_bridge.get_module_base("ntdll.dll") # 32bit ntdll
        kernel32_base = self.soldat_bridge.get_module_base("kernel32.dll")
        rtexu_offset = self.soldat_bridge.get_proc_offset(r"C:\Windows\SysWOW64\ntdll.dll", "RtlExitUserThread")
        memcpy_offset = self.soldat_bridge.get_proc_offset(r"C:\Windows\SysWOW64\ntdll.dll", "memcpy")
        virtualalloc_offset = self.soldat_bridge.get_proc_offset(r"C:\Windows\SysWOW64\kernel32.dll", "VirtualAlloc")
        self.game_addresses = addresses[exec_hash].copy()
        self.game_addresses["Stbi_load_from_memory"] += self.soldat_bridge.get_module_base("stb.dll")
        self.game_addresses["RtlExitUserThread"] = ntdll_base + rtexu_offset
        self.game_addresses["Memcpy"] = ntdll_base + memcpy_offset
        self.game_addresses["VirtualAlloc"] = kernel32_base + virtualalloc_offset
        self.assembler.set_symbol_table(self.game_addresses)


    def check_patch(self, func_name: str): return (self.soldat_bridge.read(self.game_addresses[func_name], 1) == b"\xE9")

    def patch(self, file_name: str, func_name: str, padding: int = 0) -> int:
        code = ""
        with open(file_name, "r") as f:
            code = f.read()

        dummy_gen = self.assembler.assemble(code, 0x0) # dummy assembly to get size
        code_addr = self.soldat_bridge.allocate_memory(len(dummy_gen),
                                                       MEM_COMMIT | MEM_RESERVE,
                                                       PAGE_EXECUTE_READWRITE)

        opcodes = self.assembler.assemble(code, code_addr)
        self.soldat_bridge.write(code_addr, opcodes)

        self.assembler.add_to_symbol_table("Hook", code_addr)
        trampoline = self.assembler.assemble("jmp Hook;"+"".join(["nop;" for nop in range(padding)]),
                                    self.game_addresses[func_name])

        self.soldat_bridge.write(self.game_addresses[func_name], trampoline) # <--- POSSIBLE PROBLEM
        '''
        Writing to .text section of a running process may lead to undefined behaviour.
        Instruction pointer could be on the address we are currently writing on.
        One way to avoid this is to first suspend the process then write.
        '''
        return code_addr