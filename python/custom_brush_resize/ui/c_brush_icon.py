from PyQt5 import QtWidgets, QtGui, QtCore

# color definitons
LIGHT_GRAY = QtCore.Qt.GlobalColor.lightGray
BLACK = QtCore.Qt.GlobalColor.black
MAGENTA = QtCore.Qt.GlobalColor.magenta

# rendering settings
SOLID_LINE = QtCore.Qt.PenStyle.SolidLine
DOT_LINE = QtCore.Qt.PenStyle.DotLine
HIGH_QUAL_ANTI_ALIAS = QtGui.QPainter.HighQualityAntialiasing
TRANSLUCENT_WINDOW = QtCore.Qt.WA_TranslucentBackground


class CustomBrushIcon(QtWidgets.QWidget):
    """A Widget that imitates the brush scaling icon of krita."""

    def __init__(self, parent=None):
        super(CustomBrushIcon, self).__init__(parent=parent)

        # hide the window frame and make the widget transparent
        self.setWindowFlags(
            self.windowFlags()
            | QtCore.Qt.Window
            | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(TRANSLUCENT_WINDOW)
        self.setStyleSheet("background: transparent;")
        self.setWindowTitle("icon")

        self._radius = 50
        self.can_paint_icon = True

    def paintEvent(self, _):
        """Draw the icon."""
        if not self.can_paint_icon:
            return
        self.painter = QtGui.QPainter(self)
        self.painter.setRenderHints(HIGH_QUAL_ANTI_ALIAS)
        self.draw_circle(self.painter)
        self.painter.end()

    def draw_circle(self, painter):
        """Draw a circle with the current radius."""
        painter.setPen(QtGui.QPen(BLACK, 1, SOLID_LINE))
        painter.drawEllipse(0, 0, self.radius, self.radius)

    def move_to(self, position):
        """Move the widget to given position."""
        self.move(
            int(position.x() - self.radius / 2),
            int(position.y() - self.radius / 2),
        )
        self.resize(self.radius, self.radius)
        self.update()

    def show_at(self, position):
        """Show the widget at given position."""
        self.move(
            int(position.x() - self.radius / 2),
            int(position.y() - self.radius / 2),
        )
        self.resize(self.radius, self.radius)
        self.show()

    @property
    def radius(self):
        """Get the current set radius as an integer."""
        return int(self._radius)

    @radius.setter
    def radius(self, value):
        """Set radius to given value."""
        self._radius = value
