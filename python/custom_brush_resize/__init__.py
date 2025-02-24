from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
from .extension.c_brush_resize_extension import CustomBrushResizeExtension
from .ui.c_brush_resize_dock import CustomBrushResizeDock, DOCK_OBJECT_NAME

# Adding extension and Dock to krita
Krita.instance().addExtension(CustomBrushResizeExtension(Krita.instance()))
Krita.instance().addDockWidgetFactory(
    DockWidgetFactory(
        DOCK_OBJECT_NAME,
        DockWidgetFactoryBase.DockRight,
        CustomBrushResizeDock,
    )
)
