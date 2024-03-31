from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
from .extension.c_resize_brush_extension import CustomBrushResizeExtension
from .ui.c_resize_brush_dock import CustomResizeBrushDock, DOCK_OBJECT_NAME

# Adding extension and Dock to krita
Krita.instance().addExtension(CustomBrushResizeExtension(Krita.instance()))
Krita.instance().addDockWidgetFactory(
    DockWidgetFactory(
        DOCK_OBJECT_NAME,
        DockWidgetFactoryBase.DockRight,
        CustomResizeBrushDock,
    )
)
