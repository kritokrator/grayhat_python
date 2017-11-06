from ctypes import *
libc = cdll.msvcrt
printf = libc.printf


message_string = b"Hello world!\n"

printf(b"Testing %s", message_string)
