from ctypes import *

class barley_amount(Union):
    _fields_ = [
        ("barley_long", c_long),
        ("barley_int", c_int),
        ("barley_char", c_char * 8)
    ]
value = input("enter the amount of barley to put into the beer vat: ")
my_barley = barley_amount(int(value))
print("Barley amount as long: {}".format(my_barley.barley_long))
print("Barley amount as int: {}".format(my_barley.barley_int))
print("Barley amount as char: {}".format(my_barley.barley_char))
