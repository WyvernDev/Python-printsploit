from winapi import *
import psutil

'''
This is our shellcode, essentially this is just a basic function that calls print for us.
These bytes would look close to something like this in a real programming language:

void call_print()
{
    print(0, ""); <- we write our arguments to the shellcode so we can get it to call print how we like
}

Here is a very good tutorial on calling functions externally, which does include the shellcode method I use here: https://guidedhacking.com/threads/calling-functions-externally-the-definitive-guide.10509/
'''
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

'''
This is just for writing to the shellcode, for instance, 'string_ptr_off' is where we'd need to write our pointer to the string we want to print
'''
string_ptr_off = 4
print_type_off = 9
func_ptr_off = 11
total_bytes = 22

handle = ctypes.c_void_p() # since a HANDLE type in C++ is defined as void*, ive set it to a void pointer here
base_addr = 0 # the base address of roblox, for use with the aslr bypass

def aslr(addr: int):
    return (addr - 0x400000) + base_addr # simple ASLR bypass... all exploits will use this

def get_relative(addr: int, location: int):
    '''
    because the call instruction we're using in our shellcode is relative, we need to get the relative address of Roblox's print function
    A relative address is defined as "an address specified by indicating its distance from another address" (https://www.webopedia.com/definitions/relative-address/)
    so this function will get the relative address for Roblox's print function from our call instruction, we minus 5 because thats how long the call instruction is
    '''
    return (addr - location) - 5

def rbx_print(print_type: int, string: str):
    '''
    This function will take the arguments we want to call print with, write the shellcode, write the arguments to the shellcode and then create a new thread at the start of the shellcode
    The if stat below is needed because roblox only accepts 4 print types, normal, info, warn, error (0-3)
    '''
    if (print_type < 0 or print_type > 3):
        print("Invalid print type!")
        return

    shellcode_mem = virtual_alloc_ex(handle, None, ctypes.c_size_t(total_bytes), win32con.MEM_COMMIT, win32con.PAGE_EXECUTE_READWRITE) #allocate enough memory to write the bytes
    string_mem = virtual_alloc_ex(handle, None, ctypes.c_size_t(len(string)), win32con.MEM_COMMIT, win32con.PAGE_EXECUTE_READWRITE) #allocate enough memory for the string to print

    write_proc_mem(handle, string_mem, bytes(string, "utf-8"), len(string), None) #write the string to the memory we just allocated
    write_proc_mem(handle, shellcode_mem, bytes(shellcode), total_bytes, None) #write the shellcode to the memory we allocated for the shellcode

    write_proc_mem(handle, shellcode_mem + string_ptr_off, ctypes.byref(ctypes.c_uint32(string_mem)), ctypes.sizeof(ctypes.c_uint32), None) #write the address to the string we wrote to Roblox in our shellcode (so it will be passed as an argument to print)
    write_proc_mem(handle, shellcode_mem + print_type_off, ctypes.byref(ctypes.c_int8(print_type)), ctypes.sizeof(ctypes.c_int8), None) #write the type of print to the shellcode, again so it will be passed as an argument
    write_proc_mem(handle, shellcode_mem + func_ptr_off, ctypes.byref(ctypes.c_uint32(get_relative(aslr(0x752820), shellcode_mem + func_ptr_off) + 1)), ctypes.sizeof(ctypes.c_uint32), None) #write the *relative* address of print to the call instruction in our shellcode


    create_remote_thread(handle, None, 0, shellcode_mem, 0, 0, 0) #create a new thread at the start of the shellcode


def main():
    #not even sure why i need the two lines below but it wouldnt work without them /shrug
    global handle
    global base_addr

    for proc in psutil.process_iter():
        if proc.name() == "RobloxPlayerBeta.exe":
            handle = open_process(win32con.PROCESS_ALL_ACCESS, False, proc.pid) #allow us to write mem to the process and so on...

    modules = win32process.EnumProcessModules(handle)
    base_addr = modules[0] #get the base address of Roblox

    while True:
        rbx_print(int(input("Enter print type (0-3): ")), input("Emter string: ")) #pretty self explanatory I think

#this is just to make sure that our python file isnt being imported and was ran directly
if __name__ == '__main__':
    main()
