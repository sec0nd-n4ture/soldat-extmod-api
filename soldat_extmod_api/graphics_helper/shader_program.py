from soldat_extmod_api.graphics_helper.gl_constants import ShaderType, ShaderLayer


class ShaderProgram:
    def __init__(
            self, 
            mod_api, 
            layer: ShaderLayer,
            fragment_shader_source: str,
            vertex_shader_source: str
        ):
        self.enabled = False
        self.layer = layer
        self.api = mod_api
        self.frag_shader = self.api.create_shader(ShaderType.GL_FRAGMENT_SHADER, fragment_shader_source)
        self.vert_shader = self.api.create_shader(ShaderType.GL_VERTEX_SHADER, vertex_shader_source)
        self.program_handle = self.api.gl_create_shader_program()
        self.api.gl_attach_shader(self.frag_shader, self.program_handle)
        self.api.gl_attach_shader(self.vert_shader, self.program_handle)
        self.api.gl_link_program(self.program_handle)
        self.frame_buffer_addr = self.api.create_frame_buffer()
        self.uniforms = None
        self.locations = None
        self.uniforms = {
            # uniform_name: uniform_type
            line.split(" ")[2].replace(";", ""): line.split(" ")[1]
            for line in 
                fragment_shader_source.splitlines() 
            if "uniform" in line
        }
        if self.uniforms:
            self.locations = self.api.gl_resolve_uniform_locations(self.uniforms, self.program_handle)

        shader_addresses = self.api.graphics_patcher.shader_addresses
        count = int.from_bytes(self.api.soldat_bridge.read(shader_addresses, 4), "little", signed=False)
        self.base_address = shader_addresses + (count * 24) + 4
        self.api.soldat_bridge.write(self.base_address, self.to_bytes()+b"\xFF"*12)
        self.api.soldat_bridge.write(shader_addresses, (count+1).to_bytes(4, "little", signed=False))

    def to_bytes(self):
        return b"".join([
            self.enabled.to_bytes(1, "little"),
            self.layer.value.to_bytes(1, "little"),
            self.frame_buffer_addr.to_bytes(4, "little"),
            self.program_handle.to_bytes(4, "little", signed=False)
        ])

    def enable(self):
        self.api.soldat_bridge.write(self.base_address, b"\x01")
        self.enabled = True

    def disable(self):
        self.api.soldat_bridge.write(self.base_address, b"\x00")
        self.enabled = False

    def set_layer(self, layer: ShaderLayer):
        self.api.soldat_bridge.write(self.base_address+1, layer.value.to_bytes(1, "little"))
        self.layer = layer

    def set_fbo(self, fbo_ptr: int):
        self.api.soldat_bridge.write(self.base_address+2, fbo_ptr.to_bytes(4, "little"))
        self.frame_buffer_addr = fbo_ptr

    def set_program_handle(self, handle: int):
        self.api.soldat_bridge.write(self.base_address+6, handle.to_bytes(4, "little", signed=False))
        self.program_handle = handle

    def bind_time_uniform(self, uniform_name: str):
        if self.locations and uniform_name in self.locations:
            uniform_location = self.locations[uniform_name]
            self.api.soldat_bridge.write(self.base_address+10, uniform_location)

    def bind_velocity_uniform(self, uniform_name: str, velocity_addr: int):
        if self.locations and uniform_name in self.locations:
            uniform_location = self.locations[uniform_name]
            self.api.soldat_bridge.write(self.base_address+18, velocity_addr.to_bytes(4, "little"))
            self.api.soldat_bridge.write(self.base_address+14, uniform_location)
