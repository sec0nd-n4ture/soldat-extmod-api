from kernel_wrapper import FindWindow, OpenProcess, GetPid, VirtualFreeEx,\
                    VirtualAllocEx, WriteProcessMemory, ReadProcessMemory,\
                    CreateRemoteThread, WaitForSingleObject, CloseHandle, \
                    GetModuleFileNameExW, EnumProcessModulesEx, GetModuleInformation,\
                    MODULEINFO, GetProcAddress
from ctypes import c_void_p, byref, c_ulong, create_string_buffer, create_unicode_buffer, c_size_t, sizeof, POINTER
from win32con import MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READ, PAGE_READWRITE, MEM_RELEASE
import pefile
import win32event
import logging
import time
from zlib import crc32


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

WAIT_FOR_SINGLE_OBJECT_TIMEOUT = 2000 #ms
PROCESS_ALL_ACCESS = 0x1F0FFF

class ProcessBridge:
    def __init__(self, dwDesiredAccess: int = None, windowTitle: str = None):
        self.pid: c_ulong = 0
        self.exec_hash = 0
        self.hProcess = 0                 # FIXME
        self.wHandle = FindWindow(windowTitle) # FindWindow isn't reliable, may pick up explorer.exe as the target process-
        if self.wHandle > 0:                   # if a folder named Soldat is open
            logging.info("Got handle to soldat window.")
            self.pid = GetPid(self.wHandle)
            if (self.pid != None) and (self.pid.value > 0):
                logging.info(f"Got PID for soldat {self.pid.value}")
                self.hProcess = OpenProcess(dwDesiredAccess, self.pid)
            else:
                logging.error("Couldn't acquire process handle.")
        else:
            logging.error(f"Couldn't find window with title {windowTitle}.")
            
    def __del__(self):
        CloseHandle(int(self.hProcess))

    def allocate_memory(self, size: int, flAllocationType: int, flProtect: int) -> int:
        addr: int = VirtualAllocEx(c_void_p(int(self.hProcess)), 0, size, flAllocationType, flProtect)
        if addr == 0:
            logging.error("Couldn't allocate memory.")
        else:
            logging.info(f"Allocated memory at address {hex(addr)} with protection {hex(flProtect)}")
        return addr

    def free_memory(self, address: int) -> bool:
        addr = c_void_p(address)
        result: bool = VirtualFreeEx(c_void_p(int(self.hProcess)), addr, 0, MEM_RELEASE)
        if result == 0:
            logging.error("Couldn't free memory.")
        else:
            logging.info(f"Freed memory at address {hex(address)}")
        return result

    def read(self, addr: int, length: int) -> bytes:
        ret = create_string_buffer(length)
        bytes_read = c_size_t()
        ReadProcessMemory(int(self.hProcess), addr, ret, length, byref(bytes_read))
        return ret.raw

    def write(self, addr: int, data: bytes) -> int:
        written = c_ulong(0)
        WriteProcessMemory(int(self.hProcess), addr, data, len(data), byref(written))
        return written.value

    def execute(self, EIP: int, retPtrs: list[list[int]] = None, blocking: bool = True, free_after_use: bool = True) -> tuple[int, list[bytes]]:
        """
        Executes code on the context of target process.

        This method leverages ``CreateRemoteThread`` and ``WaitForSingleObject`` to execute code.

        Args:
            EIP (int): The address of entry point to the code for the remote thread.
            retPtrs (list): List of return address and size pair list.
            blocking (bool): Whether this method should be blocking or not.

        Returns:
            tuple[int, list[bytes]] tuple of exit status of the remote thread and list of return values if there was any.
        """
        exitStat = c_ulong()
        ret = []
        timeout = WAIT_FOR_SINGLE_OBJECT_TIMEOUT
        if blocking:
            timeout = win32event.INFINITE
        hThread = CreateRemoteThread(int(self.hProcess), None, 0, EIP, None, 0, None)
        logging.info(f"[{hex(hThread)}] Remote thread created")
        t1 = time.perf_counter()
        exitStat = WaitForSingleObject(int(hThread), timeout) # this is a blocking call
        logging.info(f"[{hex(hThread)}] Remote thread returned in {round(time.perf_counter() - t1, ndigits=3)}")
        if (exitStat == 0) and (retPtrs != None):
            for ptr,size in retPtrs:
                val = self.read(ptr, size)
                ret.append(val)
                

        CloseHandle(int(hThread))
        if free_after_use:
            self.free_memory(EIP)
        return exitStat, ret
    
    def get_module_base(self, szLibName):
        hMods = (c_ulong * 1024)()
        cbNeeded = c_ulong()
        if EnumProcessModulesEx(int(self.hProcess), byref(hMods), sizeof(hMods), byref(cbNeeded), 0x03):
            for i in range(0, cbNeeded.value // sizeof(c_ulong)):
                szModName = create_unicode_buffer(1024)
                if GetModuleFileNameExW(int(self.hProcess), hMods[i], szModName, sizeof(szModName)):
                    if szModName.value.lower().endswith(szLibName):
                        mi = MODULEINFO()
                        if GetModuleInformation(int(self.hProcess), hMods[i], byref(mi), sizeof(mi)):
                            logging.info(f"{szLibName} is at {hex(mi.lpBaseOfDll)}")
                            return mi.lpBaseOfDll
                        
    def get_proc_offset(self, module_path: str, szFunctionName: str):
        dll = pefile.PE(module_path)

        for export in dll.DIRECTORY_ENTRY_EXPORT.symbols:
            if export.name == szFunctionName.encode("utf-8"):
                return export.address

        
    @property
    def executable_hash(self):
        if self.exec_hash == 0:
            szExePath = create_unicode_buffer(1024)
            GetModuleFileNameExW(int(self.hProcess), None, szExePath, sizeof(szExePath))
            with open(szExePath.value, "rb") as f:
                buffer = f.read(1024)
            crc32hash = crc32(buffer)
            self.exec_hash = crc32hash
        return self.exec_hash

    def close(self):
        CloseHandle(int(self.hProcess))