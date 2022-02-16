import ctypes
import win32con
import win32process

api = ctypes.windll.kernel32

virtual_alloc_ex = api.VirtualAllocEx
open_process = api.OpenProcess
write_proc_mem = api.WriteProcessMemory
create_remote_thread = api.CreateRemoteThread