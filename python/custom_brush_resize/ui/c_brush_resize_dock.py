import os

from krita import DockWidget

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal

from .widgets import kis_input_button, kis_slider_spinbox
from .config import buttons_input_to_text
from ..utils import write_to_json, get_settings_file, read_from_json


DOCK_OBJECT_NAME = "c_resize_brush_dock"
SETTINGS_FILE = get_settings_file(DOCK_OBJECT_NAME)

DEFAULT_SHORTCUT = buttons_input_to_text(
    [Qt.Key_Shift],
    Qt.MouseButtons(Qt.RightButton),
)


class DockSignalHandler(QtCore.QObject):
    shortcut_changed = pyqtSignal(str)
    settings_changed = pyqtSignal()


SINGAL_HANDLER = DockSignalHandler()


class CustomBrushResizeDock(DockWidget):
    def __init__(self):
        super(CustomBrushResizeDock, self).__init__()
        self.setWindowTitle("Custom Brush Resize Settings")

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        widget.setLayout(layout)

        self.setWidget(widget)

        max_brush_size = kis_slider_spinbox.KisSliderSpinBox()
        min_brush_size = kis_slider_spinbox.KisSliderSpinBox()
        max_size = kis_slider_spinbox.KisSliderSpinBox()
        shortcut_button = kis_input_button.KisInputButton()

        layout.addRow(i18n("Maximum Brush Size:"), max_brush_size)
        layout.addRow(i18n("Minimum Brush Size:"), min_brush_size)
        layout.addRow(i18n("Resize Range Max:"), max_size)
        layout.addRow(i18n("Shortcut:"), shortcut_button)

        self.handler = SINGAL_HANDLER
        self.widgets = {
            "max_brush_size": max_brush_size,
            "min_brush_size": min_brush_size,
            "max_size": max_size,
            "shortcut": shortcut_button,
        }

        self._set_internal_settings()

    def _set_internal_settings(self):
        self.widgets["max_size"].set_range(10, 1000, 0)
        self.widgets["max_size"].setSingleStep(1)
        self.widgets["max_size"].setValue(100)

        self.widgets["max_brush_size"].set_range(10, 10000, 0)
        self.widgets["max_brush_size"].setSingleStep(1)
        self.widgets["max_brush_size"].setValue(1000)

        self.widgets["min_brush_size"].set_range(0, 1000, 0)
        self.widgets["min_brush_size"].setSingleStep(1)
        self.widgets["min_brush_size"].setValue(0)

        self.widgets["shortcut"].setText(DEFAULT_SHORTCUT)
        self.import_settings()

        self.widgets["shortcut"].dataChanged.connect(
            self.emit_shortcut_changed
        )

        # handling tool settings
        self.handler.settings_changed.connect(self.export_settings)
        self.widgets["max_size"].valueChanged.connect(
            self.handler.settings_changed.emit
        )
        self.widgets["max_brush_size"].valueChanged.connect(
            self.handler.settings_changed.emit
        )
        self.widgets["min_brush_size"].valueChanged.connect(
            self.handler.settings_changed.emit
        )
        self.widgets["shortcut"].dataChanged.connect(
            self.handler.settings_changed.emit
        )

    def as_dict(self):
        return {
            "max_size": self.widgets["max_size"].value(),
            "max_brush_size": self.widgets["max_brush_size"].value(),
            "min_brush_size": self.widgets["min_brush_size"].value(),
            "shortcut": self.widgets["shortcut"].text(),
        }

    def emit_shortcut_changed(self):
        self.handler.shortcut_changed.emit(self.widgets["shortcut"].text())

    def canvasChanged(self, _):
        pass

    def export_settings(self):
        write_to_json(SETTINGS_FILE, self.as_dict())

    def import_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return
        settings = read_from_json(SETTINGS_FILE)
        self.widgets["max_size"].setValue(
            settings.get("max_size", self.widgets["max_size"].value())
        )
        self.widgets["max_brush_size"].setValue(
            settings.get(
                "max_brush_size", self.widgets["max_brush_size"].value()
            )
        )
        self.widgets["min_brush_size"].setValue(
            settings.get(
                "min_brush_size", self.widgets["min_brush_size"].value()
            )
        )
        self.widgets["shortcut"].setText(
            settings.get("shortcut", self.widgets["shortcut"].text())
        )
