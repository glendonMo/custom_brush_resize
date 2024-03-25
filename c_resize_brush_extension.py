from krita import Krita, Extension
from .mdi_filter_area import MdiFilterArea


class CustomBrushResizeExtension(Extension):
    def __init__(self, parent=None):
        super(CustomBrushResizeExtension, self).__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        self.c_brush_resize = window.createAction(
            "c_brush_resize",
            "Custom Brush resize",
        )

        self.main_event_loop = MdiFilterArea()


Krita.instance().addExtension(CustomBrushResizeExtension(Krita.instance()))
