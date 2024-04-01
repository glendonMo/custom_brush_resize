from PyQt5 import QtWidgets, QtCore

from ...utils import clamp


class KisSliderSpinBox(QtWidgets.QDoubleSpinBox):
    constant_dragging_margin = 32.0
    exponent_ratio = 1.0

    def __init__(self, parent=None):
        super(KisSliderSpinBox, self).__init__(parent=parent)
        self.line_edit = self.lineEdit()
        self.line_edit.installEventFilter(self)
        self.line_edit.selectionChanged.connect(self.fixup_selection)
        self.line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.line_edit.setAutoFillBackground(False)
        self.line_edit.setCursor(QtCore.Qt.CursorShape.SplitHCursor)

    def fixup_selection(self):
        """This excludes the prefix and suffix from being selected."""
        if not len(self.line_edit.selectedText()):
            return

        suffix_start = len(self.text()) - len(self.suffix())
        prefix_end = len(self.prefix())
        selection_start = self.line_edit.selectionStart()
        selection_end = selection_start + len(self.line_edit.selectedText())

        new_start = clamp(prefix_end, selection_start, suffix_start)
        new_end = clamp(
            prefix_end, selection_start + selection_end, suffix_start
        )

        if self.line_edit.cursorPosition() == self.line_edit.selectionStart():
            self.line_edit.setSelection(new_end, -(new_end - new_start))
            return
        self.line_edit.setSelection(new_end, new_end - new_start)

    def value_for_point(self, point):
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
        normalized_pos_x = clamp(0.0, pos_x / scaled_rect_width, 1.0)
        normalized_value = pow(normalized_pos_x, self.exponent_ratio)
        value = normalized_value * range_size + minimum
        return value

    def set_value(self, value):
        """Does not seem to run when pressing buttons or changing value?"""
        if value != self.value():
            super(KisSliderSpinBox, self).setValue(value)

        if not self.hasFocus():
            self.end_editing()

    def end_editing(self):
        self.set_value(self.value())
        self.line_edit.setReadOnly(True)
        self.line_edit.setCursor(QtCore.Qt.CursorShape.SplitHCursor)
        self.line_edit.update()

    def set_range(self, new_min, new_max, num_decimals):
        self.setDecimals(num_decimals)
        super(KisSliderSpinBox, self).setRange(new_min, new_max)

    def line_edit_mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.last_mouse_press_position = event.pos()

    def line_edit_mouseMoveEvent(self, event):
        if not self.isEnabled():
            return False
        if event.buttons() & QtCore.Qt.LeftButton:
            point = QtCore.QPoint(event.pos().x(), event.pos().y())
            self.setValue(self.value_for_point(point))
            return True

    def eventFilter(self, obj, event):
        event_method = self.event_map.get(obj, {}).get(event.type())
        if event_method:
            event_method(event)
        return False

    @property
    def event_map(self):
        return {
            self.line_edit: {
                QtCore.QEvent.MouseMove: self.line_edit_mouseMoveEvent,
                QtCore.QEvent.MouseButtonPress: self.line_edit_mousePressEvent,
            },
        }
