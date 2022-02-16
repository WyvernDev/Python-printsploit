from winapi import *
import psutil

shellcode = [
    0x55,                       #push ebp
    0x8B, 0xEC,                 #mov esp,ebp
    0x68, 0x0, 0x0, 0x0, 0x0,   #push string to print
    0x6A, 0x0,                  #push type of print
    0xE8, 0x0, 0x0, 0x0, 0x0,   #call print
    0x83, 0xC4, 0x08,           #add esp, 8
    0x8B, 0xE5,                 #mov esp, ebp
    0x5D,                       #pop ebp
    0xC3                        #ret
]

string_ptr_off = 4
print_type_off = 9
func_ptr_off = 11
total_bytes = 22
handle = ctypes.c_void_p()
base_addr = 0

def aslr(addr: int):
    return (addr - 0x400000) + base_addr

def get_relative(addr: int, location: int):
    return (addr - location) - 5

def rbx_print(print_type: int, string: str):
    if (print_type < 0 or print_type > 3):
        print("Invalid print type!")
        return

    shellcode_mem = virtual_alloc_ex(handle, None, ctypes.c_size_t(total_bytes), win32con.MEM_COMMIT, win32con.PAGE_EXECUTE_READWRITE)
    string_mem = virtual_alloc_ex(handle, None, ctypes.c_size_t(len(string)), win32con.MEM_COMMIT, win32con.PAGE_EXECUTE_READWRITE)

    write_proc_mem(handle, string_mem, bytes(string, "utf-8"), len(string), None)
    write_proc_mem(handle, shellcode_mem, bytes(shellcode), total_bytes, None)

    write_proc_mem(handle, shellcode_mem + string_ptr_off, ctypes.byref(ctypes.c_uint32(string_mem)), ctypes.sizeof(ctypes.c_uint32), None)
    write_proc_mem(handle, shellcode_mem + print_type_off, ctypes.byref(ctypes.c_int8(print_type)), ctypes.sizeof(ctypes.c_int8), None)
    write_proc_mem(handle, shellcode_mem + func_ptr_off, ctypes.byref(ctypes.c_uint32(get_relative(aslr(0x752820), shellcode_mem + func_ptr_off) + 1)), ctypes.sizeof(ctypes.c_uint32), None)


    create_remote_thread(handle, None, 0, shellcode_mem, 0, 0, 0)


def main():
    global handle
    global base_addr

    for proc in psutil.process_iter():
        if proc.name() == "RobloxPlayerBeta.exe":
            handle = open_process(win32con.PROCESS_ALL_ACCESS, False, proc.pid)

    modules = win32process.EnumProcessModules(handle)
    base_addr = modules[0]

    while True:
        rbx_print(int(input("Enter print type (0-3): ")), input("Emter string: "))

if __name__ == '__main__':
    main()
