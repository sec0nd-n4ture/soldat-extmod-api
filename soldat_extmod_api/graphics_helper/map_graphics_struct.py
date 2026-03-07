class TMapGraphics:
    def __init__(self, mod_api):
        self.api = mod_api
        self.base_address = self.api.addresses["tMapGraphics"]

    def get_filename(self) -> str:
        name_ptr = int.from_bytes(
            self.api.soldat_bridge.read(self.base_address, 4),
            "little"
        )
        name_length = int.from_bytes(
            self.api.soldat_bridge.read(name_ptr - 4, 4),
            "little"
        )
        name = b""
        for i in range(name_length):
            name += self.api.soldat_bridge.read(name_ptr+i, 1)
        return name.decode()

    def get_vertex_buffer(self) -> int:
        return int.from_bytes(
            self.api.soldat_bridge.read(
                self.base_address+0x10, 4
            ), 
            "little"
        )

    def get_polys_front(self) -> int:
        return int.from_bytes(
            self.api.soldat_bridge.read(
                self.base_address+0xA4, 4
            ), 
            "little"
        )

    def get_polys_front_count(self) -> int:
        return int.from_bytes(
            self.api.soldat_bridge.read(
                self.base_address+0xA8, 4
            ), 
            "little"
        )

    def get_polys_back(self) -> int:
        return int.from_bytes(
            self.api.soldat_bridge.read(
                self.base_address+0x9C, 4
            ), 
            "little"
        )

    def get_polys_back_count(self) -> int:
        return int.from_bytes(
            self.api.soldat_bridge.read(
                self.base_address+0xA0, 4
            ), 
            "little"
        )
