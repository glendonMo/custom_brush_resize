# first crack at trying to translate kis_slider_spin_box.h into python
# I cannot seem to figure out how to the `slider` part is drawn

from enum import Enum

try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtCore, QtGui


def clamp_value(min_value, value, max_value):
    """QBound is not available in QtCore?
    Looks like it is only clamping a value between a min and a max.
    """
    return max(min(value, max_value), min_value)


def lerp(pt1, pt2, t):
    """KisAlgebra2D::lerp function"""
    return pt1 + (pt2 - pt1) * t


class ValueUpdateMode(Enum):
    NoChange = 1


class TestSlidingSpinBox(QtWidgets.QDoubleSpinBox):
    height_of_collapsed_slider = 3.0
    height_of_space_between_sliders = 0.0
    constant_dragging_margin = 32.0
    exponent_ratio = 1.0
    start_drag_distance = 2
    start_drag_distance_squared = start_drag_distance * start_drag_distance

    def __init__(self, parent=None):
        super(TestSlidingSpinBox, self).__init__(parent=parent)
        self.setSuffix("%")
        self.setPrefix("Opacity: ")

        self.line_edit = self.lineEdit()
        self.line_edit.selectionChanged.connect(self.fixup_selection)
        self.line_edit.cursorPositionChanged.connect(
            self.fixup_cursor_position
        )

        self.line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.line_edit.setAutoFillBackground(False)
        self.line_edit.setCursor(QtCore.Qt.CursorShape.SplitHCursor)

        self.widget_range_toggle = QtWidgets.QWidget(self)
        self.widget_range_toggle.hide()

        self.slider_animation = QtCore.QVariantAnimation()
        self.slider_animation.setStartValue(0.0)
        self.slider_animation.setEndValue(1.0)
        self.slider_animation.setEasingCurve(
            QtCore.QEasingCurve(QtCore.QEasingCurve.InOutCubic)
        )
        self.slider_animation.valueChanged.connect(self.line_edit.update)
        self.slider_animation.valueChanged.connect(
            self.widget_range_toggle.update
        )

        # different colors for testing
        # palette = QtGui.QPalette()
        # palette.setColor(QtGui.QPalette.Base, QtCore.Qt.black)
        # palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        # self.line_edit.setPalette(palette)

        self.set_default()

        self.installEventFilter(self)
        self.line_edit.installEventFilter(self)
        self.widget_range_toggle.installEventFilter(self)

    # def mousePressEvent(self, event) -> None:
    #     #self.setValue(10)
    #     super(TestSlidingSpinBox, self).mousePressEvent(event)

    def set_default(self):
        self.palette().highlight().setColor(QtGui.QColor(QtCore.Qt.red))
        self.soft_minimum = 0
        self.soft_maximum = 100
        self.set_range(0, 100, 0)

    def fixup_selection(self):
        """This excludes the prefix and suffix from being selected."""
        if not len(self.line_edit.selectedText()):
            return

        suffix_start = len(self.text()) - len(self.suffix())
        prefix_end = len(self.prefix())
        selection_start = self.line_edit.selectionStart()
        selection_end = selection_start + len(self.line_edit.selectedText())

        new_start = clamp_value(prefix_end, selection_start, suffix_start)
        new_end = clamp_value(
            prefix_end, selection_start + selection_end, suffix_start
        )

        if self.line_edit.cursorPosition() == self.line_edit.selectionStart():
            self.line_edit.setSelection(new_end, -(new_end - new_start))
            return
        self.line_edit.setSelection(new_end, new_end - new_start)

    def fixup_cursor_position(self, _, new_pos):
        """Make sure the cursor is not at the prefix or suffix??"""
        prefix_end = len(self.prefix())
        suffix_start = len(self.text()) - len(self.suffix())
        if new_pos < prefix_end:
            self.line_edit.setCursorPosition(len(self.prefix()))
            return
        if new_pos > suffix_start:
            self.line_edit.setCursorPosition(suffix_start)

    def start_editing(self):
        self.value_before_editing = self.value()
        self.line_edit.setReadOnly(False)
        self.selectAll()
        self.line_edit.setFocus(QtCore.Qt.OtherFocusReason)
        self.line_edit.setCursor(QtCore.Qt.CursorShape.IBeamCursor)

    def end_editing(self, update_mode):
        self.setValue(self.value(), overwrite=True)

        pal = self.line_edit.palette()
        pal.setBrush(QtGui.QPalette.ColorRole.Text, self.palette().text())
        self.line_edit.setPalette(pal)
        self.right_click_counter = 0
        self.line_edit.setReadOnly(True)
        self.line_edit.setCursor(QtCore.Qt.CursorShape.SplitHCursor)
        self.line_edit.update()
        self.update()

    def setValue(self, value, overwrite=False):
        """Does not seem to run when pressing buttons or changing value?"""
        # print("Overridden setValue")
        if self.hasFocus() or self.line_edit.isReadOnly():
            overwrite = True
        if overwrite:
            self.last_expression_parsed = str()

        if value != self.value() or overwrite:
            super(TestSlidingSpinBox, self).setValue(value)

        if not self.hasFocus():
            self.end_editing(ValueUpdateMode.NoChange)

    def set_range(self, new_min, new_max, num_decimals):
        print("SET RANGE")
        self.setDecimals(num_decimals)
        super(TestSlidingSpinBox, self).setRange(new_min, new_max)
        self.soft_minimum = clamp_value(
            self.minimum(), self.soft_minimum, self.maximum()
        )
        self.soft_maximum = clamp_value(
            self.minimum(), self.soft_maximum, self.maximum()
        )
        self.resetRangeMode()
        self.line_edit.update()

    def resetRangeMode(self):
        pass

    def line_edit_PaintEvent(self, event):
        # print("Painting Line Edit")
        text = self.text()
        painter = QtGui.QPainter()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        value = self.value()
        hard_slider_width = self.compute_slider_width(
            float(self.minimum()), float(self.maximum()), value
        )

        color = self.palette().base().color()
        # color.setAlpha(128)
        self.paint_slider(painter, text, hard_slider_width)
        self.paint_slider(painter, text, hard_slider_width, 20)

    def line_edit_mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.last_mouse_press_position = event.pos()

    def line_edit_mouseMoveEvent(self, event):
        print(not self.isEnabled())
        if not self.isEnabled():
            return False
        print("UNDER")
        if event.buttons() & QtCore.Qt.LeftButton:
            dx = event.pos().x() - self.last_mouse_press_position.x()
            dy = event.pos().y() - self.last_mouse_press_position.y()
            if dx * dx + dy * dy <= self.start_drag_distance_squared:
                return True
            else:
                self.is_dragging = True

            p = QtCore.QPoint(event.pos().x(), event.pos().y())
            self.setValue(
                self.value_for_point(p, event.modifiers()), overwrite=True
            )
            return True

    def paint_slider(
        self, painter, text, slider_01_width, slider_02_width=-1.0
    ):
        rect = QtCore.QRectF(self.line_edit.rect())
        highlight_color = self.palette().highlight().color()
        animation_pos = self.slider_animation.currentValue()
        height_between = (
            rect.height()
            - 2.0 * self.height_of_collapsed_slider
            - self.height_of_space_between_sliders
        )
        heightOfCollapsedSliderPlusSpace = (
            self.height_of_collapsed_slider
            + self.height_of_space_between_sliders
        )
        a = heightOfCollapsedSliderPlusSpace
        b = heightOfCollapsedSliderPlusSpace + height_between
        hard_slider_adjustment = lerp(a, b, 1.0 - animation_pos)
        self.paint_slider_rect(
            painter,
            rect.adjusted(
                0, hard_slider_adjustment, -(rect.width() - slider_01_width), 0
            ),
            highlight_color,
        )

    def paint_slider_rect(self, painter, rect, brush):
        painter.save()
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(rect)
        painter.restore()

    def compute_slider_width(self, minimum, maximum, value):
        range_size = maximum - minimum
        local_position = value - minimum
        normalized_value = pow(
            local_position / range_size, 1.0 / self.exponent_ratio
        )
        width = float(self.line_edit.width())
        return clamp_value(0.0, round(normalized_value * width), width)

    def value_for_point(self, point, modifiers):
        rect = self.line_edit.rect()
        center = QtCore.QPointF(
            self.last_mouse_press_position.x() + 0, rect.height() / 2.0
        )

        minimum = self.minimum()
        maximum = self.maximum()
        range_size = maximum - minimum
        distance_y = max(
            0.0,
            abs(float(point.y()) - center.y())
            - center.y()
            - self.constant_dragging_margin,
        )
        scale = (rect.width() + 2.0 * distance_y * 2.0) / rect.width()
        scaled_rect_left = (0.0 - center.x()) * scale + center.x()
        scaled_rect_right = (rect.width() - center.x()) * scale + center.x()
        scaled_rect_width = scaled_rect_right - scaled_rect_left
        pos_x = float(point.x()) - scaled_rect_left
        normalized_pos_x = clamp_value(0.0, pos_x / scaled_rect_width, 1.0)
        normalized_value = pow(normalized_pos_x, self.exponent_ratio)
        value = normalized_value * range_size + minimum
        return value

    def eventFilter(self, obj, event):
        if not all([obj, event]):
            return False

        if obj == self:
            return False
            print("Found self")

        if obj == self.line_edit:
            line_edit_event = self.event_map.get(obj, {}).get(event.type())
            if line_edit_event:
                line_edit_event(event)

        if obj == self.widget_range_toggle:
            return False
            print("Found widget_range_toggle")
        return False

    @property
    def event_map(self):
        return {
            self: {},
            self.line_edit: {
                QtCore.QEvent.Paint: self.line_edit_PaintEvent,
                QtCore.QEvent.MouseButtonPress: self.line_edit_mousePressEvent,
                QtCore.QEvent.MouseMove: self.line_edit_mouseMoveEvent,
            },
            self.widget_range_toggle: {},
        }


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    slide = TestSlidingSpinBox()
    ui = QtWidgets.QWidget()
    ui.setLayout(QtWidgets.QVBoxLayout())
    ui.layout().addWidget(slide)
    ui.show()
    app.exec()
