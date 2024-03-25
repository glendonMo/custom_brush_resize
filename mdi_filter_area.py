from krita import Krita, DockWidget
from PyQt5 import QtWidgets, QtCore, QtGui
from .c_resize_icon import CustomBrushIcon
from .c_resize_brush_dock import DOCK_OBJECT_NAME
from .utils import translate


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

    window = Krita.instance().activeWindow()
    current_view = window.activeView()
    current_q_window = window.qwindow()

    settings = get_dock_settings(current_q_window)

    max_resize_value = settings.get("max_size", max_resize_value)
    max_brush_size = settings.get("max_brush_size", max_brush_size)
    min_brush_size = settings.get("min_brush_size", min_brush_size)

    cursor_press_position = QtGui.QCursor.pos()
    current_brush_size = current_view.brushSize()
    brush_icon.radius = current_brush_size


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

    def eventFilter(self, object, event):
        global shift_key_pressed
        global l_mouse_button_pressed

        global cursor_press_position

        if not event.type() in ACCEPTED_EVENT_TYPES:
            return False

        # Is user pressing the shift key?
        if (
            not shift_key_pressed
            and event.type() == QtCore.QEvent.KeyPress
            and event.key() == QtCore.Qt.Key_Shift
        ):
            shift_key_pressed = True

        # The user released the shift key
        if (
            event.type() == QtCore.QEvent.KeyRelease
            and event.key() == QtCore.Qt.Key_Shift
        ):
            shift_key_pressed = False
            return False

        # Is the user pressing the left mouse button
        # while pressing the shift key?
        if (
            not l_mouse_button_pressed
            and shift_key_pressed
            and event.type() == QtCore.QEvent.MouseButtonPress
            and event.button() == QtCore.Qt.LeftButton
        ):
            l_mouse_button_pressed = True
            start_resize()

        # The user released the left mouse button
        if (
            event.type() == QtCore.QEvent.MouseButtonRelease
            and event.button() == QtCore.Qt.LeftButton
        ):
            brush_icon.hide()
            l_mouse_button_pressed = False
            return False

        # Is user pressing shift key and left mouse button
        if all([shift_key_pressed, l_mouse_button_pressed]):
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
