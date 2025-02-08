from krita import Extension

from ..drivers.shortcut_listener import ShortcutListener
from ..drivers.brush_size_driver import BrushSizeDriver
from ..ui.c_brush_resize_dock import (
    SINGAL_HANDLER,
    DEFAULT_SHORTCUT,
    SETTINGS_FILE,
)
from ..ui.c_brush_icon import CustomBrushIcon
from ..utils import read_from_json


class CustomBrushResizeExtension(Extension):
    """Extension class that connects everything together."""

    def __init__(self, parent=None):
        super(CustomBrushResizeExtension, self).__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Register actions with krita and initialize drivers."""
        self.c_brush_resize = window.createAction(
            "c_brush_resize",
            "Custom Brush resize",
        )

        # Initialize drivers
        data = read_from_json(SETTINGS_FILE)
        shortcut = data.get("shortcut", DEFAULT_SHORTCUT)

        self.shortcut_listener = ShortcutListener(shortcut)
        self.brush_driver = BrushSizeDriver()
        self.brush_icon = CustomBrushIcon()
        self.brush_icon.hide()

        # Connecting shorcut listener to other drivers
        # For whatever reason, I could not connect the drivers signals
        # and slots together directly. Instead, I had to define functions on
        # this extension class, and connect them instead.

        # press events
        self.shortcut_listener.button_pressed.connect(self.start_resize)
        self.shortcut_listener.shortcut_pressed_while_dragging.connect(
            self.resize_brush
        )

        # release events
        self.shortcut_listener.button_released.connect(self.hide_icon)
        self.shortcut_listener.key_released.connect(self.hide_icon)
        self.shortcut_listener.button_released.connect(self.end_resize)
        self.shortcut_listener.key_released.connect(self.end_resize)

        # This one can be connected directly?
        # setting changes
        SINGAL_HANDLER.shortcut_changed.connect(
            self.shortcut_listener.set_shortcut
        )

    def hide_icon(self, *_):
        self.brush_icon.hide()

    def start_resize(self, *_):
        self.brush_driver.start_resize()

    def resize_brush(self, *_):
        if not self.brush_driver.can_resize_brush:
            return
        self.brush_icon.radius = (
            self.brush_driver.brush_size_after_change * 0.5
        )
        self.brush_icon.show_at(self.brush_driver.initial_press_position)
        self.brush_driver.resize_brush()

    def end_resize(self, *_):
        self.brush_driver.end_resize()
