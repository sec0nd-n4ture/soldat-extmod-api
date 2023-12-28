class BranchController:
    def __init__(self, shared_memory, soldat_bridge):
        self.sm = shared_memory
        self.soldat_bridge = soldat_bridge

    def set_redirect(self):
        self.soldat_bridge.write(self.sm.address, b"\x01")

    # will be set to false by the process after function returns
    def set_texturefunc_flag(self):
        self.soldat_bridge.write(self.sm.get_addr_flagtexturefunc, b"\x01")

    def enable_draw_loop(self):
        self.soldat_bridge.write(self.sm.get_addr_flagdrawloop, b"\x01")

    def disable_draw_loop(self):
        self.soldat_bridge.write(self.sm.get_addr_flagdrawloop, b"\x00")