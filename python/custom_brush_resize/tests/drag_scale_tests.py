from PyQt5 import QtCore, QtGui, QtWidgets
import typing


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


class DragScale(QtWidgets.QWidget):
    """This is to test the idea of creating a QRect that maps the
        current clicked position to a custom value within a different range.
        The goal is to have the click point represent the percentage of the
        custom value along the width of the rect.
    """
    def __init__(self, parent=None):
        super(DragScale, self).__init__(parent=parent)
        self.resize(500, 500)

        # custom values to map the mouse click position to
        self.max_size = 50
        self.min_size = 1
        self.current_size = 15

        # initialize rect variables
        self.rect = None
        self.first_click = False

    def paintEvent(self, event):
        """This will draw the rect on the widget.
        """
        painter = QtGui.QPainter(self)
        if not self.first_click:
            self.rect = QtCore.QRect(0, 0, 250, 50)
        painter.begin(self)
        painter.drawRect(self.rect)
        painter.end()

    def mousePressEvent(self, event):
        """Calculate the current size along the rect width.
            The rect is drawn with the current clicked x position representing
            the current size along the drawn rect.
        """
        # get te position of the click and the end
        # position of the rect relative to the click
        clicked_x_pos = event.pos().x()
        rect_end_pos = clicked_x_pos + self.rect.width()

        # get current_size mapped along the rect width
        remapped_size = translate(
            self.current_size,
            self.min_size,
            self.max_size,
            clicked_x_pos,
            rect_end_pos
        )

        # get the distance that the rect has to be move back to
        # correspond with the current size
        offset_distance = event.pos().x() - remapped_size

        # move the rect left so the current clicked location matches the
        # current size but remapped to the rect width
        new_x_pos = int(event.pos().x() - abs(offset_distance))

        # shift the rect down so it is centered to the current click
        nex_y_pos = int(event.pos().y() - self.rect.height() / 2)

        self.first_click = True
        self.rect.moveTo(new_x_pos, nex_y_pos)

        # redraw the rect
        self.update()

    def mouseMoveEvent(self, event):
        """Track when the user is dragging
        """
        pass

    def mouseReleaseEvent(self, event):
        """Redraw rect in initial position
        """
        self.first_click = False
        self.update()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ui = DragScale()
    ui.show()
    app.exec()