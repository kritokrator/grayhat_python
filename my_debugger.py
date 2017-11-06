from ctypes import *
from my_debugger_defines import *

kernel32 = windll.kernel32


class Debugger:
    def __init__(self):
        self.h_process = None
        self.pid = None
        self.debugger_active = False


    def load(self, path_to_exe):

        creation_flags = DEBUG_PROCESS
        startup_info = STARTUPINFO()
        process_information = PROCESS_INFORMATION()

        startup_info.dwFlags = 0x1
        startup_info.wShowWindow = 0x0
        startup_info.cb = sizeof(startup_info)

        if kernel32.CreateProcessW(
                path_to_exe,
                None,
                None,
                None,
                None,
                creation_flags,
                None,
                None,
                byref(startup_info),
                byref(process_information)
        ):
            print("[*] We have successfully launched process")
            print("[*] PID {}".format(process_information.dwProcessId))

            self.h_process = self.open_process(process_information.dwProcessId)
        else:
            print("!! ERROR: 0x%08x." % kernel32.GetLastError())

    def open_thread(self, thread_id):

        h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, None, thread_id)

        if h_thread is not None:
            return h_thread
        else:
            print("[*] Could not obtain a valid thread handle.")
            return False

    def enumerate_threads(self):

        thread_entry = THREADENTRY32()
        thread_list = []
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)

        if snapshot is not None:
            thread_entry.dwSize = sizeof(thread_entry)
            success = kernel32.Thread32First(snapshot, byref(thread_entry))

            while success:
                if thread_entry.th32OwnerProcessID == self.pid:
                    thread_list.append(thread_entry.th32ThreadID)
                success = kernel32.Thread32Next(snapshot, byref(thread_entry))
            kernel32.CloseHandle(snapshot)
            return thread_list
        else:
            return False

    def get_thread_context(self, thread_id):

        context = CONTEXT()
        context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS

        h_thread = self.open_thread(thread_id)

        if kernel32.GetThreadContext(h_thread, byref(context)):
            kernel32.CloseHandle(h_thread)
            return context
        else:
            return False

    def open_process(self, pid):
        # there is a typo here in the grayhat book, the order of the params is inverted
        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

        return h_process

    def attach(self, pid):
        self.h_process = self.open_process(pid)
        # if the open process returns NULL not a valid handle we now something went wrong
        # therefore if self.h_process is NULL we should GetLastError know and not call
        # DebugActiveProcess with an invalid pid

        if self.h_process == 0:
            print("Error while obtaining handle")
            print("!! ERROR: 0x%08x." % kernel32.GetLastError())
            return
        else:
            print("process handle {}".format(self.h_process))

        # before attaching to the process check if it is a 32 bit since this is a 32 bit debugger

        i = c_int()
        kernel32.IsWow64Process(self.h_process, byref(i))
        if i:
            print('[*] 32 bit process')
        else:
            print("Error process is not 32 bit")
            return

        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid = pid
            self.run()
        else:
            print("unable to attach to the process")
            print("!! ERROR: 0x%08x" % kernel32.GetLastError())

    def run(self):
        while self.debugger_active:
            self.get_debug_event()

    def get_debug_event(self):
        debug_event = DEBUG_EVENT()
        continue_status = DBG_CONTINUE

        if kernel32.WaitForDebugEvent(byref(debug_event), INFINITE):
            input("Press a key to continue ...")
            self.debugger_active = False
            kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)

    def detach(self):
        if kernel32.DebugActiveProcessStop(self.pid):
            print("[*] Finished debugging. Exiting ...")
            return True
        else:
            print("There was an error")
            return False

    def hello(self):
        print("Hello World!")
