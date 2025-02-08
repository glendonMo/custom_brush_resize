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


# Sign used between buttons in keys in displayed shortcuts
SEPARATOR = "+"


def buttons_to_text(buttons) -> str:
    """Map Qt.Mousebuttons to display names."""
    text = ""
    button_count = 0
    for button in BUTTON_NAME_MAP:
        if not is_button_in(buttons, button):
            continue
        if button_count > 0:
            text += SEPARATOR
        button_count += 1
        name = BUTTON_NAME_MAP[button]
        text += name

    return text


def is_button_in(buttons, button):
    """Check if given buttons contains button."""
    if isinstance(buttons, list):
        return button in buttons
    if type(buttons) == Qt.MouseButtons:
        return buttons & button
    return False


def keys_to_text(keys: list[Qt.Key]) -> str:
    """Map a list of Qt.Key to display names."""
    text = ""
    for key in keys:
        if len(text) > 0:
            text += SEPARATOR
        default_key = QtGui.QKeySequence(key).toString(
            QtGui.QKeySequence.NativeText
        )
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


def text_to_buttons(text, separator=SEPARATOR) -> list[Qt.MouseButton]:
    """Map a mouse button shortcut to a list of Qt.Mousebutton.
    Expects each button to be separated by given separator.
    """
    buttons = []
    for button in text.split(separator):
        for qt_button in BUTTON_NAME_MAP:
            if not button == BUTTON_NAME_MAP[qt_button]:
                continue
            buttons.append(qt_button)
    return buttons


def text_to_keys(text, separator=SEPARATOR) -> list[Qt.Key]:
    """Map a keyboard shortcut to a list of Qt.Key.
    Expects each key to be separated by given separator.
    """
    keys = []
    # TODO(glendon):
    # Right now, the Left and Right mouse button names
    # will be interpreted as the Left and Right keys.
    # There should be a better way of handling this.
    buttons = [BUTTON_NAME_MAP[button] for button in BUTTON_NAME_MAP]

    for key in text.split(separator):
        # ignoring keys that have the same name as the mouse buttons
        if key in buttons:
            continue
        qt_key = [
            qt_key for qt_key in KEY_NAME_MAP if KEY_NAME_MAP[qt_key] == key
        ]
        if not qt_key:
            key_sequence = QtGui.QKeySequence(key)
            qt_key = [Qt.Key(key_sequence[0])]
        keys += qt_key
    return keys


def text_input_to_buttons(text, separator=SEPARATOR):
    """Map mouse buttons and keys to lists of Qt.Key and Qt.MouseButton.
    Expects each button and key to be separated by given separator.
    """
    keys = text_to_keys(text, separator)
    buttons = text_to_buttons(text, separator)
    return buttons, keys
