class TMapGraphics:
    def __init__(self, mod_api):
        self.api = mod_api
        self.base_address = self.api.addresses["tMapGraphics"]

    def get_filename(self) -> str:
        name_ptr = int.from_bytes(
            self.api.soldat_bridge.read(self.base_address, 4),
            "little"
        )
        return self.api.soldat_bridge.read_delphi_utf8_string(name_ptr)

    def get_vertex_buffer(self) -> int:
        return self.api.soldat_bridge.read_ptr(self.base_address+0x10)

    def get_polys_front(self) -> int:
        return self.api.soldat_bridge.read_ptr(self.base_address+0xA4)

    def get_polys_front_count(self) -> int:
        return self.api.soldat_bridge.read_value(self.base_address+0xA8, "I")

    def get_polys_back(self) -> int:
        return self.api.soldat_bridge.read_ptr(self.base_address+0x9C)

    def get_polys_back_count(self) -> int:
        return self.api.soldat_bridge.read_value(self.base_address+0xA0, "I")
