import os
from struct import pack
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE
from soldat_extmod_api.interprocess_utils.game_addresses import addresses
from soldat_extmod_api.interprocess_utils.branch_controller import BranchController
from soldat_extmod_api.interprocess_utils.shared_memory import SharedMemory


class GraphicsPatcher:
    def __init__(self, mod_api):
        self.patcher = mod_api.patcher
        self.assembler = self.patcher.assembler
        self.soldat_bridge = mod_api.soldat_bridge
        self.shared_memory = SharedMemory(mod_api)
        self.branch_controller = BranchController(self.shared_memory, mod_api.soldat_bridge)
        self.shared_memory.update(0) # let the class decide the base address
        self.assembler.add_to_symbol_table(self.shared_memory.sm_symbol_table)
        self.sprite_addresses = self.soldat_bridge.allocate_memory(32768, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.text_addresses = self.soldat_bridge.allocate_memory(32768, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.keypress_buffer_address = self.soldat_bridge.allocate_memory(12, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.keypress_buffer_inc_address = self.keypress_buffer_address + 0x4
        self.assembler.add_to_symbol_table("keypress_buffer_key", self.keypress_buffer_address)
        self.assembler.add_to_symbol_table("keypress_buffer_inc", self.keypress_buffer_address + 0x4)
        self.assembler.add_to_symbol_table("keypress_buffer_eax", self.keypress_buffer_address + 0x8)
        self.assembler.add_to_symbol_table("ptr_sprite_count", self.sprite_addresses)
        self.assembler.add_to_symbol_table("ptr_sprite_array", self.sprite_addresses + 0x4)
        self.assembler.add_to_symbol_table("ptr_text_count", self.text_addresses)
        self.assembler.add_to_symbol_table("ptr_text_array", self.text_addresses + 0x4)
        self.assembler.add_to_symbol_table("RIhookContinue", addresses[self.soldat_bridge.executable_hash]["RenderInterface"] + 0x8)
        self.assembler.add_to_symbol_table("FormKeyPressContinue", addresses[self.soldat_bridge.executable_hash]["FormKeyPress"] + 0x7)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        self.patches_dir = os.path.join(os.path.dirname(module_dir), "patches")

    @property
    def check_patch(self):
        return self.patcher.check_patch("RenderInterface")

    def apply_patch(self):
        fp_buffer = self.soldat_bridge.allocate_memory(48, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.soldat_bridge.write(fp_buffer, pack("f", 2)) # constant 2.0 for calculations later
        self.assembler.add_to_symbol_table("fp_buffer", fp_buffer)
        self.patcher.patch(os.path.join(self.patches_dir, "gui_patch.asm"), "RenderInterface", 3)
        self.patcher.patch(os.path.join(self.patches_dir, "keypress_hook.asm"), "FormKeyPress", 1)