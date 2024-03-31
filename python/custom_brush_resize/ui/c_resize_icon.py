from PyQt5 import QtWidgets, QtGui, QtCore


LIGHT_GRAY = QtCore.Qt.GlobalColor.lightGray
BLACK = QtCore.Qt.GlobalColor.black
MAGENTA = QtCore.Qt.GlobalColor.magenta
SOLID_LINE = QtCore.Qt.PenStyle.SolidLine
DOT_LINE = QtCore.Qt.PenStyle.DotLine
HIGH_QUAL_ANTI_ALIAS = QtGui.QPainter.HighQualityAntialiasing


class CustomBrushIcon(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(CustomBrushIcon, self).__init__(parent=parent)
        self.setWindowFlags(
            self.windowFlags()
            | QtCore.Qt.Window
            | QtCore.Qt.FramelessWindowHint
        )
        self._radius = 50
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setWindowTitle("icon")

    def paintEvent(self, event):
        # return
        self.painter = QtGui.QPainter(self)
        self.painter.setRenderHints(HIGH_QUAL_ANTI_ALIAS)
        self.draw_circle(self.painter)
        self.painter.end()

    def draw_circle(self, painter):
        painter.setPen(QtGui.QPen(BLACK, 1, SOLID_LINE))
        painter.drawEllipse(0, 0, self.radius, self.radius)

    def move_to(self, position):
        self.move(
            int(position.x() - self.radius / 2),
            int(position.y() - self.radius / 2),
        )
        self.resize(self.radius, self.radius)
        self.update()

    def show_at(self, position):
        self.move(
            int(position.x() - self.radius / 2),
            int(position.y() - self.radius / 2),
        )
        self.resize(self.radius, self.radius)
        self.show()

    @property
    def radius(self):
        return int(self._radius)

    @radius.setter
    def radius(self, value):
        self._radius = value
