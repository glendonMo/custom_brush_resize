from krita import Krita, DockWidget, DockWidgetFactory, DockWidgetFactoryBase
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal

from .widgets import kis_input_button
from .config import buttons_input_to_text


DOCK_OBJECT_NAME = "c_resize_brush_dock"
DEFAULT_SHORTCUT = buttons_input_to_text(
    [Qt.Key_Shift],
    Qt.MouseButtons(Qt.RightButton),
)


class DockSignalHandler(QtCore.QObject):
    shortcut_changed = pyqtSignal(str)


SINGAL_HANDLER = DockSignalHandler()


class CustomResizeBrushDock(DockWidget):
    def __init__(self):
        super(CustomResizeBrushDock, self).__init__()
        self.setWindowTitle("Custom Brush Resize Settings")

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        widget.setLayout(layout)

        self.setWidget(widget)

        max_brush_size = QtWidgets.QSpinBox()
        min_brush_size = QtWidgets.QSpinBox()
        max_size = QtWidgets.QSpinBox()
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

        self.set_default_values()

    def set_default_values(self):
        self.widgets["max_size"].setRange(10, 10000)
        self.widgets["max_size"].setSingleStep(1)
        self.widgets["max_size"].setValue(100)

        self.widgets["max_brush_size"].setRange(1, 10000)
        self.widgets["max_brush_size"].setSingleStep(1)
        self.widgets["max_brush_size"].setValue(1000)

        self.widgets["min_brush_size"].setRange(0, 10000)
        self.widgets["min_brush_size"].setSingleStep(1)
        self.widgets["min_brush_size"].setValue(0)

        self.widgets["shortcut"].setText(DEFAULT_SHORTCUT)
        self.widgets["shortcut"].dataChanged.connect(
            self.emit_shortcut_changed
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

    def canvasChanged(self, canvas):
        pass
