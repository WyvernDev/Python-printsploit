'''
This is a simple file to get the windows native functions so we can write to the memory and create a remote thread when we need to.
I would've used a memory library in python but i dont know of any python mem libs that allow me to create remote threads so I would've needed to use ctypes eventually
'''
import ctypes
import win32con
import win32process

api = ctypes.windll.kernel32

virtual_alloc_ex = api.VirtualAllocEx
open_process = api.OpenProcess
write_proc_mem = api.WriteProcessMemory
create_remote_thread = api.CreateRemoteThread
