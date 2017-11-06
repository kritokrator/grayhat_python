import my_debugger
from ctypes import c_ulong

debugger = my_debugger.Debugger()

debugger.hello()
# debugger.load("C:\\Windows\\System32\\calc.exe")

pid = int((input("Enter PID of the process to attach to:")))
debugger.attach(pid)

list = debugger.enumerate_threads()
for thread in list:
    thread_context = debugger.get_thread_context(thread)

    print("[*] Dumping registers fo thread ID : 0x%08x" % thread)
    print("[**] EIP: 0x%08x" % thread_context.Eip)
    print("[**] ESP: 0x%08x" % thread_context.Esp)
    print("[**] EBP: 0x%08x" % thread_context.Ebp)
    print("[**] EAX: 0x%08x" % thread_context.Eax)
    print("[**] EBX: 0x%08x" % thread_context.Ebx)
    print("[**] ECX: 0x%08x" % thread_context.Ecx)
    print("[**] EDX: 0x%08x" % thread_context.Edx)
    print("[*] END DUMP")

debugger.detach()
