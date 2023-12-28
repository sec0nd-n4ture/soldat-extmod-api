import win32api
import win32con
import ctypes
from ctypes.wintypes import BOOL, HWND,LPDWORD,\
                            DWORD, HANDLE,LPVOID,\
                            LPCVOID, SHORT, INT, LPSTR,\
                            HHOOK, HINSTANCE, WPARAM, LPARAM, MSG

HOOKPROC = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_int, WPARAM, LPARAM)
# Delegate functions
CallNextHookEx = ctypes.windll.user32.CallNextHookEx
SetWindowsHookExW = ctypes.windll.user32.SetWindowsHookExW
UnhookWindowsHookEx = ctypes.windll.user32.UnhookWindowsHookEx
GetMessageW = ctypes.windll.user32.GetMessageW
PeekMessageW = ctypes.windll.user32.PeekMessageW
TranslateMessage = ctypes.windll.user32.TranslateMessage
DispatchMessageW = ctypes.windll.user32.DispatchMessageW
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
CreateRemoteThread = ctypes.windll.kernel32.CreateRemoteThread
WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
EnumProcessModulesEx = ctypes.windll.psapi.EnumProcessModulesEx
GetModuleFileNameExW = ctypes.windll.psapi.GetModuleFileNameExW
GetModuleInformation = ctypes.windll.psapi.GetModuleInformation
GetProcAddress = ctypes.windll.kernel32.GetProcAddress
CloseHandle = ctypes.windll.kernel32.CloseHandle
GetKeyState = ctypes.windll.user32.GetKeyState
GetCurrentThreadId = ctypes.windll.kernel32.GetCurrentThreadId

# kernel32
'''
BOOL WriteProcessMemory(HANDLE hProcess, LPVOID lpBaseAddress, LPCVOID lpBuffer, SIZE_T nSize, SIZE_T *lpNumberOfBytesWritten);
'''
WriteProcessMemory.argtypes = HANDLE, LPVOID, LPCVOID, ctypes.c_size_t, LPVOID
WriteProcessMemory.restype = BOOL

ReadProcessMemory.argtypes = HANDLE, LPCVOID, LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
ReadProcessMemory.restype = BOOL

CreateRemoteThread.argtypes = HANDLE, LPVOID, ctypes.c_size_t, LPVOID, LPVOID, DWORD, LPVOID
CreateRemoteThread.restype = HANDLE

WaitForSingleObject.argtypes = HANDLE, DWORD
WaitForSingleObject.restype = DWORD

GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
GetProcAddress.restype = ctypes.c_void_p

CloseHandle.restype = BOOL

'''
LPVOID VirtualAllocEx(HANDLE hProcess, LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);
'''
VirtualAllocEx.argtypes = HANDLE, LPVOID, ctypes.c_size_t, DWORD, DWORD
VirtualAllocEx.restype = LPVOID

VirtualFreeEx.argtypes = HANDLE, LPVOID, ctypes.c_size_t, DWORD
VirtualFreeEx.restype = BOOL

# user32
'''
DWORD GetWindowThreadProcessId(HWND hWnd, LPDWORD lpdwProcessId);
'''
GetWindowThreadProcessId.argtypes = HWND, LPDWORD
GetWindowThreadProcessId.restype = DWORD

GetKeyState.argtypes = [INT]
GetKeyState.restype = SHORT

SetWindowsHookExW.argtypes = [INT, HOOKPROC, HINSTANCE, DWORD]
SetWindowsHookExW.restype = HHOOK

CallNextHookEx.argtypes = [HHOOK, INT, WPARAM, LPARAM]

UnhookWindowsHookEx.argtypes = [HHOOK]
UnhookWindowsHookEx.restype = BOOL

GetCurrentThreadId.restype = DWORD

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vk_code", ctypes.c_int),
                ("scan_code", ctypes.c_int),
                ("flags", ctypes.c_int),
                ("time", ctypes.c_int),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulonglong))]

class MODULEINFO(ctypes.Structure):
    _fields_ = [("lpBaseOfDll", ctypes.c_void_p),
                ("SizeOfImage", ctypes.c_ulong),
                ("EntryPoint", ctypes.c_void_p)]

def FindWindow(windowTitle: str):
    handle = ctypes.windll.user32.FindWindowW(0, windowTitle)
    return handle

def GetPid(hwnd) -> ctypes.c_ulong:
    lpdwProcessId = ctypes.c_ulong()
    GetWindowThreadProcessId(hwnd, ctypes.byref(lpdwProcessId))
    return lpdwProcessId

def OpenProcess(dwdesiredAccess, lpdwProcessId):
    hProcess = win32api.OpenProcess(dwdesiredAccess, False, lpdwProcessId.value)
    return hProcess