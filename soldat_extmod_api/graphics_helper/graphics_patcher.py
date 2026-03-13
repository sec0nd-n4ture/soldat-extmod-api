import os
from struct import pack
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE, PAGE_EXECUTE_READWRITE
from soldat_extmod_api.interprocess_utils.game_addresses import addresses
from soldat_extmod_api.interprocess_utils.branch_controller import BranchController
from soldat_extmod_api.interprocess_utils.shared_memory import SharedMemory
from soldat_extmod_api.interprocess_utils.assembler import Assembler
from soldat_extmod_api.soldat_bridge import SoldatBridge

class GraphicsPatcher:
    def __init__(self, mod_api):
        self.symbol_count = 0
        self.patcher = mod_api.patcher
        self.assembler: Assembler = self.patcher.assembler
        self.soldat_bridge: SoldatBridge = mod_api.soldat_bridge
        self.shared_memory = SharedMemory(mod_api)
        self.branch_controller = BranchController(self.shared_memory, mod_api.soldat_bridge)
        self.shared_memory.update(0) # let the class decide the base address
        self.assembler.add_to_symbol_table(self.shared_memory.sm_symbol_table)
        self.float_swizzle_mem = self.soldat_bridge.allocate_memory(16, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.sprite_list_head_ptr = self.soldat_bridge.allocate_memory(4, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.text_addresses = self.soldat_bridge.allocate_memory(32768, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.framebuffer_addresses = self.soldat_bridge.allocate_memory(32768, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.vertexbuffer_addresses = self.soldat_bridge.allocate_memory(32768, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.map_vertexdata_address = self.soldat_bridge.allocate_memory(4, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.map_vertexdatasize_address = self.soldat_bridge.allocate_memory(4, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.wireframe_vbo_address = self.soldat_bridge.allocate_memory(4, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.shader_addresses = self.soldat_bridge.allocate_memory(32768, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.keypress_buffer_address = self.soldat_bridge.allocate_memory(12, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.keypress_buffer_inc_address = self.keypress_buffer_address + 0x4
        self.soldat_bridge.write(self.shared_memory.get_addr_float_swizzle, self.float_swizzle_mem.to_bytes(4, "little"))
        self.assembler.add_to_symbol_table("keypress_buffer_key", self.keypress_buffer_address)
        self.assembler.add_to_symbol_table("keypress_buffer_inc", self.keypress_buffer_address + 0x4)
        self.assembler.add_to_symbol_table("keypress_buffer_eax", self.keypress_buffer_address + 0x8)
        self.assembler.add_to_symbol_table("ptr_sprite_head", self.sprite_list_head_ptr)
        self.assembler.add_to_symbol_table("ptr_text_count", self.text_addresses)
        self.assembler.add_to_symbol_table("ptr_text_array", self.text_addresses + 0x4)
        self.assembler.add_to_symbol_table("ptr_shader_count", self.shader_addresses)
        self.assembler.add_to_symbol_table("ptr_shader_array", self.shader_addresses + 0x4)
        self.assembler.add_to_symbol_table("ptr_framebuffer_count", self.framebuffer_addresses)
        self.assembler.add_to_symbol_table("ptr_framebuffer_array", self.framebuffer_addresses + 0x4)
        self.assembler.add_to_symbol_table("ptr_vertexbuffer_count", self.vertexbuffer_addresses)
        self.assembler.add_to_symbol_table("ptr_vertexbuffer_array", self.vertexbuffer_addresses + 0x4)
        self.assembler.add_to_symbol_table("map_vbo_ptr", self.map_vertexdata_address)
        self.assembler.add_to_symbol_table("map_vbosize_ptr", self.map_vertexdatasize_address)
        self.assembler.add_to_symbol_table("wireframe_vbo", self.wireframe_vbo_address)
        self.assembler.add_to_symbol_table("RIhookContinue", addresses[self.soldat_bridge.executable_hash]["RenderInterface"] + 0x8)
        self.assembler.add_to_symbol_table("FormKeyPressContinue", addresses[self.soldat_bridge.executable_hash]["FormKeyPress"] + 0x7)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        self.patches_dir = os.path.join(os.path.dirname(module_dir), "patches")
        with open(os.path.join(self.patches_dir, "func_draw_fullscreen_quad_shader.asm"), "r") as f:
            code = f.read()

        dummy_gen = self.assembler.assemble(code, 0x0)
        fullscreen_quad_func_shader_addr = self.soldat_bridge.allocate_memory(
            len(dummy_gen),
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE
        )
        self.soldat_bridge.write(
            fullscreen_quad_func_shader_addr, 
            self.assembler.assemble(
                code, fullscreen_quad_func_shader_addr
            )
        )
        with open(os.path.join(self.patches_dir, "func_draw_fullscreen_quad.asm"), "r") as f:
            code = f.read()

        dummy_gen = self.assembler.assemble(code, 0x0)
        fullscreen_quad_func_addr = self.soldat_bridge.allocate_memory(
            len(dummy_gen),
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE
        )
        self.soldat_bridge.write(
            fullscreen_quad_func_addr, 
            self.assembler.assemble(
                code, fullscreen_quad_func_addr
            )
        )
        self.assembler.add_to_symbol_table("DrawFullscreenQuadShader", fullscreen_quad_func_shader_addr)
        self.assembler.add_to_symbol_table("DrawFullscreenQuad", fullscreen_quad_func_addr)


    @property
    def check_patch(self):
        return self.patcher.check_patch("RenderInterface")

    def apply_patch(self):
        fp_buffer = self.soldat_bridge.allocate_memory(64, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        self.soldat_bridge.write(fp_buffer, pack("f", 2)) # constant 2.0 for calculations later
        self.soldat_bridge.write(fp_buffer+48, pack("f", 1000)) # constant 1000.0 for calculations later
        self.assembler.add_to_symbol_table("fp_buffer", fp_buffer)
        self.assembler.add_to_symbol_table("thousand_constant", fp_buffer+48)
        self.__generate_shader_patch_symbols()
        self.patcher.patch(os.path.join(self.patches_dir, "gui_patch.asm"), "RenderInterface", 3)
        self.patcher.patch(os.path.join(self.patches_dir, "keypress_hook.asm"), "FormKeyPress", 1)
        self.patcher.patch(os.path.join(self.patches_dir, "init_context_patch.asm"), "GfxInitContext", 5)
        self.patcher.patch(os.path.join(self.patches_dir, "destroy_context_patch.asm"), "GfxDestroyContext", 4)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_background.asm"), "RF_Background", 1)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_props0.asm"), "RF_RenderProps0", 0)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_players.asm"), "RF_RenderPlayers", 0)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_props1.asm"), "RF_RenderProps1", 0)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_poly.asm"), "RF_RenderPolies", 1)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_props2.asm"), "RF_RenderProps2", 0)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_interface.asm"), "RF_RenderInterface", 0)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_final_pass.asm"), "RF_FBOCombination", 0)
        self.patcher.patch(os.path.join(self.patches_dir, "map_vbo_hook.asm"), "MapVBOHook", 0)
        self.patcher.patch(os.path.join(self.patches_dir, "draw_hijack_things_polygons.asm"), "RF_RenderThingsPolygons", 0)

    # TODO: generalize SharedMemory for shaders
    def __generate_shader_patch_symbols(self):
        self.patch_shared_mem = self.soldat_bridge.allocate_memory(
            1024,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_READWRITE
        )
        self.__add_symbol("ic_ptr_eax_save", self.patch_shared_mem)
        self.__add_symbol("ic_ptr_ebx_save", self.patch_shared_mem)
        self.__add_symbol("ic_ptr_edx_save", self.patch_shared_mem)
        self.__add_symbol("ic_ptr_ebp_save", self.patch_shared_mem)
        self.__add_symbol("ic_ptr_esp_save", self.patch_shared_mem)
        self.__add_symbol("ic_ptr_esi_save", self.patch_shared_mem)
        self.__add_symbol("ic_ptr_edi_save", self.patch_shared_mem)
        self.__add_symbol("ic_ptr_ecx_save", self.patch_shared_mem)
        self.__add_symbol("draw_polygon_wireframe_flag", self.patch_shared_mem)
        self.__add_symbol("disable_poly_texture_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_background_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_props0_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_players_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_props1_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_poly_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_props2_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_interface_flag", self.patch_shared_mem)
        self.__add_symbol("disable_layer_things_polygons_flag", self.patch_shared_mem)
        self.__add_symbol("wireframe_mode", self.patch_shared_mem)

        self.assembler.add_to_symbol_table("background_fbo", self.framebuffer_addresses+4)
        self.assembler.add_to_symbol_table("props_fbo0", self.framebuffer_addresses+8)
        self.assembler.add_to_symbol_table("players_fbo", self.framebuffer_addresses+12)
        self.assembler.add_to_symbol_table("props_fbo1", self.framebuffer_addresses+16)
        self.assembler.add_to_symbol_table("poly_fbo", self.framebuffer_addresses+20)
        self.assembler.add_to_symbol_table("props_fbo2", self.framebuffer_addresses+24)
        self.assembler.add_to_symbol_table("interface_fbo", self.framebuffer_addresses+28)
        self.assembler.add_to_symbol_table("final_pass_fbo", self.framebuffer_addresses+32)
        self.assembler.add_to_symbol_table("poly_wireframe_fbo", self.framebuffer_addresses+36)
        self.assembler.add_to_symbol_table("things_polygons_fbo", self.framebuffer_addresses+40)
        self.assembler.add_to_symbol_table("IC_branch_1", 0x00508988)
        self.assembler.add_to_symbol_table("IC_continue", 0x005088E4)
        self.assembler.add_to_symbol_table("DC_continue", 0x00508B21)

    def __add_symbol(self, name: str, address: int):
        if self.symbol_count == 1024 // 4:
            raise BufferError("Maximum capacity reached for symbols.")
        self.assembler.add_to_symbol_table(name, address + self.symbol_count * 4)
        self.symbol_count += 1

    def get_symbol_address(self, symbol_name: str) -> int:
        if symbol_name not in self.assembler.symbol_table:
            return -1
        return self.assembler.symbol_table[symbol_name]
