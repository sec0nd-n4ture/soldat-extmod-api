from interprocess_utils.process_bridge import ProcessBridge
from win32.lib.win32con import MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READ, PAGE_READWRITE, MEM_RELEASE


WAIT_FOR_SINGLE_OBJECT_TIMEOUT = 2000 #ms
PROCESS_ALL_ACCESS = 0x1F0FFF

class SoldatBridge(ProcessBridge):
    """
    Provides a bridge between Python and Soldat process.
    """
    def __init__(self):
        super().__init__(PROCESS_ALL_ACCESS, "Soldat")
