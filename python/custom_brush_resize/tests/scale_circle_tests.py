import sys
from PyQt5 import QtCore, QtGui, QtWidgets

BLACK = QtCore.Qt.GlobalColor.black
SOLID_LINE = QtCore.Qt.PenStyle.SolidLine
HIGH_QUAL_ANTI_ALIAS = QtGui.QPainter.HighQualityAntialiasing


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

    def mousePressEvent(self, event):
        """Save the position of the click.
            This will be the center of the circle.
        """
        self.center = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        """Calculate the radius and store that the mouse is moving
        """
        # mouse is moving
        self.moving = True

        # get radius of circle using the click point
        # and the current mouse position
        dif_x = event.pos().x() - self.center.x()
        dif_y = event.pos().y() - self.center.y()
        r = dif_x ** 2 + dif_y ** 2
        self.radius = r ** 0.5

        # draw the circle
        self.update()

    def mouseReleaseEvent(self, event):
        """Mouse is no longer moving. Circle is removed.
        """
        self.moving = False
        self.update()

    def paintEvent(self, event):
        """Draw the circle when mouse is moving.
        """
        painter = QtGui.QPainter(self)
        rect = event.rect()
        painter.drawPixmap(rect, self.image, rect)
        if self.moving:
            self.draw_circle(painter)

    def draw_circle(self, painter):
        """Will draw a circle at the clicked position
            with the calculated radius.
        """
        painter.setRenderHint(HIGH_QUAL_ANTI_ALIAS)
        painter.setPen(QtGui.QPen(BLACK, 2, SOLID_LINE))
        painter.drawEllipse(self.center, self.radius, self.radius)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = ScaleCircle()
    gui.show()
    sys.exit(app.exec_())
