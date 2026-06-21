from soldat_extmod_api.interprocess_utils.process_bridge import ProcessBridge
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READ, PAGE_READWRITE, MEM_RELEASE
from typing import Any
import struct

WAIT_FOR_SINGLE_OBJECT_TIMEOUT = 2000 #ms
PROCESS_ALL_ACCESS = 0x1F0FFF

class SoldatBridge(ProcessBridge):
    """
    Provides a bridge between Python and Soldat process.
    """
    def __init__(self):
        super().__init__(PROCESS_ALL_ACCESS, "Soldat")

    def read_delphi_raw_string(self, string_address: int) -> bytes:
        if not string_address:
            return b""
        str_length = self.read_value(string_address - 4, "i")
        if str_length <= 0:
            return b""
        return self.read(string_address, str_length)

    def read_delphi_utf8_string(self, string_address: int) -> str:
        raw_bytes = self.read_delphi_raw_string(string_address)
        return raw_bytes.decode("utf-8", errors="replace")

    def read_delphi_utf16_string(self, string_address: int) -> str:
        raw_bytes = self.read_delphi_raw_string(string_address)
        return raw_bytes.decode("utf-16", errors="replace")

    def read_ptr(self, address: int) -> int:
        return self.read_value(address, "I") or 0

    def read_value(self, address: int, struct_format: str) -> Any:
        if not address:
            return None

        num_bytes = struct.calcsize(struct_format)
        raw_bytes = self.read(address, num_bytes)

        unpacked = struct.unpack(struct_format, raw_bytes)
        return unpacked[0] if len(unpacked) == 1 else unpacked
