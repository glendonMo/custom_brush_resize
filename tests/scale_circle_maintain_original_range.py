import sys
from PyQt5 import QtCore, QtGui, QtWidgets

BLACK = QtCore.Qt.GlobalColor.black
LIGHT_GRAY = QtCore.Qt.GlobalColor.lightGray
MAGENTA = QtCore.Qt.GlobalColor.magenta
SOLID_LINE = QtCore.Qt.PenStyle.SolidLine
DOT_LINE = QtCore.Qt.PenStyle.DotLine
HIGH_QUAL_ANTI_ALIAS = QtGui.QPainter.HighQualityAntialiasing


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


class ScaleCircle(QtWidgets.QWidget):
    """Drawing circles where the user clicks.
        When dragging, the circle scales to match the mouse position.
        Based on:
            https://stackoverflow.com/questions/61034583/drawing-a-circle-on-a-qwidget-python-gui

        This can be modified to set radius to an existing value and then scale
        the circle based on the distance that the user drags the mouse.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.image = QtGui.QPixmap()
        self.resize(500, 500)

        # initialize values needed for drawing circle
        self.moving = False
        self.center = None
        self.radius = None
        self.rect = None

        self.max_size = 100
        self.min_size = 0
        self.current_size = 25

        self.range_max = 100

        self.pressed = False

    def mousePressEvent(self, event):
        """Save the position of the click.
            This will be the center of the circle.
        """
        self.center = event.pos()
        self.pressed = True
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        """Calculate the radius and store that the mouse is moving
        """
        # mouse is moving
        self.moving = True

        # establish the extremes of the rectangle
        start_x_pos = self.get_rect_x()
        end_x_pos = start_x_pos + self.range_max

        # remap the current mouse position to a brush size
        new_size = translate(
            event.pos().x(),
            start_x_pos,
            end_x_pos,
            self.min_size,
            self.max_size,
        )

        # clamp the new size within the min and max values
        remap = max(min(new_size, self.max_size), self.min_size)

        # get the radius of the circle
        self.radius = remap * 0.5

        # draw the circle
        self.update()

    def mouseReleaseEvent(self, event):
        """Mouse is no longer moving. Circle is removed.
        """
        self.moving = False
        self.pressed = False
        self.update()

    def paintEvent(self, event):
        """Draw the circle when mouse is moving.
        """
        painter = QtGui.QPainter(self)
        rect = event.rect()
        painter.drawPixmap(rect, self.image, rect)
        if self.moving:
            self.draw_circle(painter)
        if self.pressed:
            self.draw_rect(painter)
            self.draw_circle2(painter)

    def draw_circle(self, painter):
        """Will draw a circle at the clicked position
            with the calculated radius.
        """
        painter.setRenderHint(HIGH_QUAL_ANTI_ALIAS)
        painter.setPen(QtGui.QPen(BLACK, 2, SOLID_LINE))
        painter.drawEllipse(self.center, self.radius, self.radius)

    def draw_circle2(self, painter):
        """Will draw a circle at the center of the rectangle
            with the calculated radius.
        """
        new_center_x = int(self.rect.x() + self.rect.width() * 0.5)
        new_center = QtCore.QPoint(new_center_x, self.rect.y())
        painter.setRenderHint(HIGH_QUAL_ANTI_ALIAS)
        painter.setPen(QtGui.QPen(MAGENTA, 1, DOT_LINE))
        painter.drawEllipse(new_center, self.radius, self.radius)

    def draw_rect(self, painter):
        """Will draw a rectangle that represents the entire brush
            size mapped to a new range.
        """
        painter.setRenderHint(HIGH_QUAL_ANTI_ALIAS)
        painter.setPen(QtGui.QPen(LIGHT_GRAY, 2, SOLID_LINE))
        new_x = self.get_rect_x()
        self.rect = QtCore.QRect(new_x, self.center.y(), self.range_max, 50)
        painter.drawRect(self.rect)

    def get_rect_x(self):
        """Get the new rect x position offset to represent
            the current brush size.
        """
        new_range_start = self.center.x()
        new_range_end = self.center.x() + self.range_max
        remapped_size = translate(
            self.current_size,
            self.min_size,
            self.max_size,
            new_range_start,
            new_range_end
        )
        offset_distance = self.center.x() - remapped_size
        return int(self.center.x() - abs(offset_distance))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = ScaleCircle()
    gui.show()
    sys.exit(app.exec_())
