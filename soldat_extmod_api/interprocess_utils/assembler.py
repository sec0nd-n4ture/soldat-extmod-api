import keystone


class Assembler(keystone.Ks):
    def __init__(self, arch = keystone.KS_ARCH_X86, mode = keystone.KS_MODE_32):
        super().__init__(arch, mode)
        self.sym_resolver = self.sym_callback
        self.symbol_table = {}

    def sym_callback(self, symbol: bytes, value):
        sym_str = symbol.decode("utf-8")
        offset = 0x4             # offset 4 is needed because jmp instruction is 4 bytes long
        if sym_str[0].islower(): # uppercase first letter is reserved for function addresses
            offset = 0x0
        try:
            value[0] = self.symbol_table[symbol.decode("utf-8")] - offset
        except:
            raise KeyError(f"Symbol '{sym_str}' not found in symbol table")
        return True # must return a bool

    def set_symbol_table(self, sym_table: dict):
        self.symbol_table.update(sym_table)

    def add_to_symbol_table(self, key_or_dict: str | dict, value: int | None = None):
        if isinstance(key_or_dict, str):
            self.symbol_table[key_or_dict] = value
        elif isinstance(key_or_dict, dict):
            self.symbol_table.update(key_or_dict)
        else:
            raise TypeError("Expected a string or dictionary argument")

    def assemble(self, code: str, base_address: int) -> bytes:
        return self.asm(code, base_address, True)[0]