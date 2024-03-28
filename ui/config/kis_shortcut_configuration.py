""" Some useful elements re-implemented from kis_shortcut_configuration.cpp
    which can be useful when setting and getting shortcuts from ui elements.
    https://github.com/KDE/krita/blob/master/libs/ui/input/kis_shortcut_configuration.cpp
"""

from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5 import QtGui


class ShortcutType(Enum):
    """Possible types to be used for shortcuts."""

    UnknownType = 1000
    KeyCombinationType = UnknownType + 1
    MouseButtonType = UnknownType + 2
    MouseWheelType = UnknownType + 3
    GestureType = UnknownType + 4
    MacOSGestureType = UnknownType + 4


# Display names for mouse buttons
BUTTON_NAME_MAP = {
    Qt.LeftButton: "Left",
    Qt.RightButton: "Right",
    Qt.MiddleButton: "Middle",
}


# Display names for keys
KEY_NAME_MAP = {
    Qt.Key_Control: "Ctrl",
    Qt.Key_Meta: "Meta",
    Qt.Key_Alt: "Alt",
    Qt.Key_Shift: "Shift",
}


def buttons_to_text(buttons) -> str:
    """Map Qt.Mousebuttons to display names."""
    text = ""
    separator = "+"
    button_count = 0
    for button in BUTTON_NAME_MAP:
        if buttons & button:
            if button_count > 0:
                text += separator
            button_count += 1
            name = BUTTON_NAME_MAP[button]
            text += name

    return text


def keys_to_text(keys: list[Qt.Key]) -> str:
    """Map a list of Qt.Key to display names."""
    text = ""
    separator = "+"

    for key in keys:
        if len(text) > 0:
            text += separator
        default_key = QtGui.QKeySequence(key).toString(QtGui.QKeySequence.NativeText)
        key_name = KEY_NAME_MAP.get(key, default_key)
        text += key_name
    if len(text) == 0:
        text += "None"
    return text


def buttons_input_to_text(keys, buttons):
    """Map a list of Qt.Key and Qt.Mousebuttons to display names.
    Mouse button display names are always given first.
    """
    button_text = buttons_to_text(buttons)
    if len(keys) > 0:
        keys_text = keys_to_text(keys)
        return button_text + "+" + keys_text
    return button_text
