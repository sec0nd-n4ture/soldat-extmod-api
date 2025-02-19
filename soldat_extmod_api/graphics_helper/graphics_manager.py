from soldat_extmod_api.game_structs.gfx_structs import ImageData, ImageDataCache
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE, PAGE_READWRITE
from struct import unpack

class GraphicsManager:
    def __init__(self, mod_api):
        self.assembler = mod_api.assembler
        self.soldat_bridge = mod_api.soldat_bridge
        self.shared_graphics_memory = mod_api.graphics_patcher.shared_memory
        self.branch_controller = mod_api.graphics_patcher.branch_controller
        self.cache = ImageDataCache()

    # this probably needs to be rewritten in asm
    def premultiply(self, idata: ImageData): # this should be a method of ImageData
        """
        Premultiplies the alpha values of an ImageData object.

        Args:
        - idata: The ImageData object to be premultiplied.

        Returns:
        - None
        """
        data_ptr_int = int().from_bytes(idata.pData, "little")
        image_data = bytearray(self.soldat_bridge.read(data_ptr_int, idata.height * idata.width * idata.components))
        for i in range(idata.height * idata.width):
            alpha = image_data[i * 4 + 3] / 255.0
            image_data[i * 4] = int(image_data[i * 4] * alpha)
            image_data[i * 4 + 1] = int(image_data[i * 4 + 1] * alpha)
            image_data[i * 4 + 2] = int(image_data[i * 4 + 2] * alpha)
        self.soldat_bridge.write(data_ptr_int, bytes(image_data))

    def load_image(self, fname: str) -> ImageData:
        """
        Loads an image from a file and returns an ImageData object.

        Args:
        - fname: The filename of the image file to be loaded.

        Returns:
        - An ImageData object representing the loaded image.
        """
        if self.cache.check_cache(fname):
            return self.cache.get_from_cache(fname)
        image_bytes = b""
        comp = b""
        with open(fname, 'rb') as f:
            image_bytes = f.read()

        if ".jpg" in fname:
            comp = b"\x03"
        else:
            comp = b"\x04"
        image_addr = self.soldat_bridge.allocate_memory(len(image_bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        code_addr = self.soldat_bridge.allocate_memory(64, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
        ptr_addr = self.soldat_bridge.allocate_memory(12, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)

        self.soldat_bridge.write(image_addr, image_bytes)

        code = f"""
        push {"0x"+comp.hex()}
        push {"0x"+ptr_addr.to_bytes(4, "big").hex()}
        push {"0x"+(ptr_addr+4).to_bytes(4, "big").hex()}
        push {"0x"+(ptr_addr+8).to_bytes(4, "big").hex()}
        push {"0x"+len(image_bytes).to_bytes(4, "big").hex()}
        push {"0x"+image_addr.to_bytes(4, "big").hex()}
        call Stbi_load_from_memory
        mov dword ptr ds:[{"0x"+(code_addr + 0x60).to_bytes(4, "big").hex()}], eax
        xor eax, eax
        call RtlExitUserThread
        """

        assembled_code = self.assembler.assemble(code, code_addr)

        self.soldat_bridge.write(code_addr, assembled_code)
        exitcode, returns = self.soldat_bridge.execute(code_addr, 
                            [[ptr_addr, 4], [ptr_addr+4, 4], [ptr_addr+8, 4], [code_addr+0x60, 4]],
                            True, free_after_use=True)
        if exitcode == 0:
            id = ImageData(fname, 
                           unpack("I", returns[2])[0],
                           unpack("I", returns[1])[0],
                           unpack("I", returns[0])[0],
                           returns[3])
            if id.pData != b"\x00\x00\x00\x00":
                if id.components == 4:
                    self.premultiply(id)
            self.cache.add_to_cache(id)
            return id
        else:
            raise OSError(f"Remote thread returned non-zero exit code, {exitcode}")
    
    # TODO: decide to use PEP-8 naming or keep camel case for denoting foreign functions.
    def CreateTexture(self, ptrToImage: bytes, components: bytes, width: bytes, height: bytes) -> bytes:
        """
        Creates a texture using the provided image data.

        Args:
        - ptrToImage: The pointer to the image data.
        - components: The number of color components.
        - width: The width of the image.
        - height: The height of the image.

        Returns:
        - The address of the created texture in bytes.
        """
        self.shared_graphics_memory.push_imageptr(ptrToImage)
        self.shared_graphics_memory.push_imagecompr(components)
        self.shared_graphics_memory.push_imageheight(height)
        self.shared_graphics_memory.push_imagewidth(width)

        self.branch_controller.set_texturefunc_flag()
        self.branch_controller.set_redirect()
        while self.soldat_bridge.read(self.shared_graphics_memory.get_addr_flagtexturefunc, 1) == b"\x01": pass
        tex_addr = self.shared_graphics_memory.get_return_value
        tries = 0
        while tex_addr == b"\x00\x00\x00\x00":
            print("Null ptr, reading again...")
            tex_addr = self.shared_graphics_memory.get_return_value
            tries += 1
            if tries > 10:
                print("Max tries reached while reading return value...")
                exit()
        return tex_addr
    
    def EnableDrawing(self):
        """
        Enables the drawing loop.
        """
        self.branch_controller.set_redirect()
        self.branch_controller.enable_draw_loop()

    def DisableDrawing(self):
        """
        Disables the drawing loop.
        """
        self.branch_controller.set_redirect()
        self.branch_controller.disable_draw_loop()