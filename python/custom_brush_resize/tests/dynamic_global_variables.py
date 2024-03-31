"""Testing a way to dynamically define global variable"""

from PyQt5.QtCore import Qt
import ast

KEYS = [Qt.Key.Key_Shift, Qt.Key.Key_S]
GLOBAL_KEY_NAME = "key_{}_pressed"


def define_globals():
    for qt_key in KEYS:
        name = GLOBAL_KEY_NAME.format(qt_key)
        globals()[name] = True


define_globals()
# I dont like that I have to use `eval` to get the value
print(f"Found global variable: {eval(GLOBAL_KEY_NAME.format(KEYS[0]))}")
print(f"Without value: {GLOBAL_KEY_NAME.format(KEYS[0])}")
globals()[GLOBAL_KEY_NAME.format(KEYS[0])] = False
print([globals()[GLOBAL_KEY_NAME.format(i)] for i in KEYS])
