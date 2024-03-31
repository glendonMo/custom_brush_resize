from krita import Krita, DockWidget
from PyQt5 import QtWidgets, QtCore, QtGui
from ..ui.c_resize_icon import CustomBrushIcon
from ..ui.c_resize_brush_dock import (
    DOCK_OBJECT_NAME,
    DEFAULT_SHORTCUT,
    SINGAL_HANDLER,
)
from ..ui.config import text_input_to_buttons
from ..utils import translate


# global variables for tracking user input
l_mouse_button_pressed = False
shift_key_pressed = False


# variables used to calculate new brush size
cursor_press_position = None
current_brush_size = 50
max_brush_size = 1000
min_brush_size = 0
max_resize_value = 100
min_resize_value = 0
current_view = None
shortcut = text_input_to_buttons(DEFAULT_SHORTCUT)


# variables used for dynamically settings global variables
key_name = "key_{qt_key}_pressed"
button_name = "mouse_{qt_button}_pressed"


brush_icon = CustomBrushIcon()


ACCEPTED_EVENT_TYPES = [
    QtCore.QEvent.KeyRelease,
    QtCore.QEvent.MouseButtonRelease,
    QtCore.QEvent.KeyPress,
    QtCore.QEvent.MouseButtonPress,
    QtCore.QEvent.MouseMove,
]


def start_resize():
    global cursor_press_position
    global current_brush_size
    global max_resize_value
    global max_brush_size
    global min_brush_size
    global current_view
    global shortcut

    window = Krita.instance().activeWindow()
    current_view = window.activeView()
    current_q_window = window.qwindow()

    settings = get_dock_settings(current_q_window)

    max_resize_value = settings.get("max_size", max_resize_value)
    max_brush_size = settings.get("max_brush_size", max_brush_size)
    min_brush_size = settings.get("min_brush_size", min_brush_size)

    set_shortcut_globals()

    cursor_press_position = QtGui.QCursor.pos()
    current_brush_size = current_view.brushSize()
    brush_icon.radius = current_brush_size


def set_shortcut_globals():
    global shortcut

    if shortcut is None:
        shortcut = text_input_to_buttons(DEFAULT_SHORTCUT)

    buttons = shortcut[0]
    keys = shortcut[1]

    for button in buttons:
        name = button_name.format(qt_button=button)
        globals()[name] = globals().get(name, False)

    for key in keys:
        name = key_name.format(qt_key=key)
        globals()[name] = globals().get(name, False)


def set_global_shortcut():
    global shortcut
    print("Shortcut changed")
    window = Krita.instance().activeWindow()
    if window is None:
        return
    current_q_window = window.qwindow()

    settings = get_dock_settings(current_q_window)
    shortcut = text_input_to_buttons(
        settings.get("shortcut", DEFAULT_SHORTCUT)
    )
    set_shortcut_globals()


def is_shortcut_pressed():
    global shortcut
    buttons = shortcut[0]
    keys = shortcut[1]
    keys_pressed = [globals()[key_name.format(qt_key=key)] for key in keys]
    buttons_pressed = [
        globals()[button_name.format(qt_button=button)] for button in buttons
    ]
    return all(buttons_pressed + keys_pressed)


def get_dock_settings(q_window=None):
    q_window = q_window or Krita.instance().activeWindow().qwindow()
    settings_dock = q_window.findChild(DockWidget, DOCK_OBJECT_NAME)
    if not settings_dock:
        return {}
    return settings_dock.as_dict()


def get_start_x():
    global cursor_press_position
    global current_brush_size
    global max_brush_size
    global min_brush_size
    global max_resize_value

    new_range_start = cursor_press_position.x()
    new_range_end = cursor_press_position.x() + max_resize_value
    remapped_size = translate(
        current_brush_size,
        min_brush_size,
        max_brush_size,
        new_range_start,
        new_range_end,
    )
    offset_distance = cursor_press_position.x() - remapped_size
    return int(cursor_press_position.x() - abs(offset_distance))


def get_brush_size():
    global cursor_press_position
    global current_brush_size
    global max_brush_size
    global min_brush_size
    global max_resize_value

    # establish the extremes of the rectangle
    start_x_pos = get_start_x()
    end_x_pos = start_x_pos + max_resize_value

    # remap the current mouse position to a brush size
    new_size = translate(
        QtGui.QCursor.pos().x(),
        start_x_pos,
        end_x_pos,
        min_brush_size,
        max_brush_size,
    )
    # clamp the new size within the min and max values
    remap = max(min(new_size, max_brush_size), min_brush_size)
    # get the radius of the circle
    return remap


def set_brush_size(size):
    global current_view
    current_view.setBrushSize(size)


class MdiFilterArea(QtWidgets.QMdiArea):
    """Main event loop used to process user input."""

    def __init__(self, parent=None):
        super(MdiFilterArea, self).__init__(parent)
        self.image = QtGui.QPixmap()
        set_shortcut_globals()
        SINGAL_HANDLER.shortcut_changed.connect(set_global_shortcut)

    def eventFilter(self, object, event):
        global shortcut_pressed
        global shortcut

        buttons = shortcut[0]
        keys = shortcut[1]

        if not event.type() in ACCEPTED_EVENT_TYPES:
            return False

        # Is user pressing a shorcut key?
        if (
            event.type() == QtCore.QEvent.KeyPress
            and event.key() in keys
            and not globals()[key_name.format(qt_key=event.key())]
        ):
            globals()[key_name.format(qt_key=event.key())] = True

        # The user released a shortcut key
        if (
            event.type() == QtCore.QEvent.KeyRelease
            and event.key() in keys
            and globals()[key_name.format(qt_key=event.key())]
        ):
            globals()[key_name.format(qt_key=event.key())] = False
            return False

        # Is the user pressing a shortcut mouse button
        if (
            event.type() == QtCore.QEvent.MouseButtonPress
            and event.button() in buttons
            and not globals()[button_name.format(qt_button=event.button())]
        ):
            globals()[button_name.format(qt_button=event.button())] = True
            start_resize()

        # The user released a shortcut mouse button
        if (
            event.type() == QtCore.QEvent.MouseButtonRelease
            and event.button() in buttons
        ):
            brush_icon.hide()
            globals()[button_name.format(qt_button=event.button())] = False
            return False

        # Is user pressing all shortcut keys and buttons?
        if is_shortcut_pressed():
            new_size = current_brush_size
            # print("Shift and Left mouse button pressed")
            if event.type() == QtCore.QEvent.MouseMove:
                new_size = get_brush_size()

            brush_icon.radius = new_size * 0.5
            set_brush_size(new_size)
            brush_icon.show_at(cursor_press_position)
            return True

        # User was not triggering the tool
        return False
