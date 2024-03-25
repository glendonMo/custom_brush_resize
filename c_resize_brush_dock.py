from krita import Krita, DockWidget, DockWidgetFactory, DockWidgetFactoryBase
from PyQt5 import QtWidgets

DOCK_OBJECT_NAME = "c_resize_brush_dock"


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

        layout.addRow(i18n("Maximum Brush Size:"), max_brush_size)
        layout.addRow(i18n("Minimum Brush Size:"), min_brush_size)
        layout.addRow(i18n("Resize Range Max:"), max_size)

        self.widgets = {
            "max_brush_size": max_brush_size,
            "min_brush_size": min_brush_size,
            "max_size": max_size,
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

    def as_dict(self):
        return {
            "max_size": self.widgets["max_size"].value(),
            "max_brush_size": self.widgets["max_brush_size"].value(),
            "min_brush_size": self.widgets["min_brush_size"].value(),
        }

    def canvasChanged(self, canvas):
        pass


Krita.instance().addDockWidgetFactory(
    DockWidgetFactory(
        DOCK_OBJECT_NAME,
        DockWidgetFactoryBase.DockRight,
        CustomResizeBrushDock,
    )
)
