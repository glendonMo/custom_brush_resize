from krita import Krita, DockWidget

from PyQt5 import QtGui, QtCore, QtWidgets

from ..utils import remap, clamp
from ..ui.c_resize_brush_dock import DOCK_OBJECT_NAME

# For finding ui elements within krita
KRITA_TOOL_BOX_NAME = "ToolBox"
KRITA_BRUSH_TOOL_NAME = "KritaShape/KisToolBrush"


def get_brush_settings(q_window):
    """Get all settings from the custom brush resize dock widget."""
    settings_dock = q_window.findChild(DockWidget, DOCK_OBJECT_NAME)
    if not settings_dock:
        return {}
    return settings_dock.as_dict()


class BrushSizeDriver(QtCore.QObject):
    """Will keep track of the brush size changes."""

    start_resizing = QtCore.pyqtSignal()
    end_resizing = QtCore.pyqtSignal()
    brush_size_changed = QtCore.pyqtSignal(int)

    def __init__(self) -> None:
        super(BrushSizeDriver, self).__init__()
        self.brush_size = None
        self.brush_size_before_change = None
        self.brush_size_after_change = None
        self.initial_press_position = None
        self.max_brush_size = None
        self.min_brush_size = None
        self.new_resize_max = None
        self.view_while_resizing = None
        self.can_resize_brush = False

    def start_resize(self, *_):
        """Initialize the values needed for brush resizing."""
        window = Krita.instance().activeWindow()
        # only resize brush if the window exists, the brush tool
        # is checked and a document exists!
        if not all(
            [
                window,
                self.is_brush_tool_toggled(),
                self.does_document_exist(),
            ]
        ):
            self.can_resize_brush = False
            return

        view = window.activeView()
        q_window = window.qwindow()

        # store the starting press position for calculating the
        # distance that was dragged
        self.initial_press_position = QtGui.QCursor.pos()

        # store current brush size
        self.brush_size = view.brushSize()
        self.brush_size_before_change = view.brushSize()
        self.brush_size_after_change = view.brushSize()

        # store the current view so it does not have to be resolved again
        self.view_while_resizing = view

        # read settings from custom brush resize dock widget
        tool_settings = get_brush_settings(q_window)
        self.max_brush_size = tool_settings.get("max_brush_size")
        self.min_brush_size = tool_settings.get("min_brush_size")
        self.new_resize_max = tool_settings.get("max_size")

        self.can_resize_brush = True
        self.start_resizing.emit()

    def resize_brush(self, *_):
        """Resize the brush using the distance that was dragged
        from the starting click position.
        """

        if not self.can_resize_brush:
            return

        new_size = self.calculate_new_brush_size()
        self.brush_size_after_change = new_size
        self.set_brush_size(int(new_size))

    def end_resize(self, *_):
        """Resizing has stopped."""
        self.can_resize_brush = False
        self.end_resizing.emit()

    def get_starting_x_pos(self):
        """Establish the starting x position for the new resize range."""
        # establish the bounds for the new brush size
        # this determine how far the user has to drag to resize the brush
        new_range_min = self.initial_press_position.x()
        new_range_max = self.initial_press_position.x() + self.new_resize_max
        remapped_brush_size = remap(
            self.brush_size,
            (self.min_brush_size, self.max_brush_size),
            (new_range_min, new_range_max),
        )

        offset_distance = self.initial_press_position.x() - remapped_brush_size

        # offset the pressed x position, so the part directly
        # under the cursor matches the current brush size
        return self.initial_press_position.x() - abs(offset_distance)

    def calculate_new_brush_size(self):
        """Get the upated brush size using the distance that was dragged."""
        # this establishes the distance that the user has to
        # drag to resize the brush to its max or min size.
        start_x = self.get_starting_x_pos()
        end_x = start_x + self.new_resize_max
        new_brush_size = remap(
            QtGui.QCursor.pos().x(),
            (start_x, end_x),
            (self.min_brush_size, self.max_brush_size),
        )
        # make sure the new brush size does not go past the set brush range
        return clamp(self.min_brush_size, new_brush_size, self.max_brush_size)

    def set_brush_size(self, new_size):
        """Set the current view's brush size."""
        self.view_while_resizing.setBrushSize(new_size)
        self.brush_size_changed.emit(new_size)

    def is_brush_tool_toggled(self):
        """Confirm whether the brush tool is the current tool."""
        brush_tool = None

        for dock in Krita.instance().dockers():
            if not dock.objectName() == KRITA_TOOL_BOX_NAME:
                continue

            brush_tool = dock.findChild(
                QtWidgets.QToolButton,
                KRITA_BRUSH_TOOL_NAME,
                QtCore.Qt.FindChildrenRecursively,
            )

        if not brush_tool:
            return False

        return brush_tool.isChecked()

    def does_document_exist(self):
        """Confirm whether a document is open."""
        return Krita.instance().activeDocument()
