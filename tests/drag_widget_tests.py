import PySide6
from PySide6 import QtCore, QtGui, QtWidgets

SHIFT_KEY = 16777248

class DragTests(QtWidgets.QWidget):
    """A class for testing various drag/keyboard input options.
        The goal is to be able to check whether the user is pressing `Shift`
        and is dragging with the left mouse button pressed.
    """

    def __init__(self, parent=None):
        super(DragTests, self).__init__(parent)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(QtWidgets.QPushButton("Hello"))
        self.resize(500, 500)
        self.setAcceptDrops(True)
        self.i = 0
        self.first_release = False
        self.pressed_keys = []


    def keyPressEvent(self, event: PySide6.QtGui.QKeyEvent) -> None:
        """Collecting each pressed key as an integer
        """
        # tracking when first key is released
        self.first_release = True
        pressed_key = event.key()
        self.pressed_keys.append(pressed_key)

    def keyReleaseEvent(self, event: PySide6.QtGui.QKeyEvent) -> None:
        """ Process any multi key combinations and remove
            keys when they are no longer pressed.
        """
        # branch to handle key combinations
        if self.first_release:
            self.process_multiple_keys(self.pressed_keys)

        # keys are no longer pressed
        self.first_release = False

        del self.pressed_keys[-1]
        print("Removed last key")
        print(self.pressed_keys)

    def process_multiple_keys(self, pressed_keys: list[int]) -> None:
        """Logic for handling key combinations can be added here.
        """
        print(pressed_keys)

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """This event triggers when the user left clicks
            and drags on the widget.
            Here, we can check if the user has pressed the
            shift key and is click dragging on the widget.
        """
        print(f"Mouse Move {self.i}")
        self.i += 1
        if SHIFT_KEY in self.pressed_keys:
            print("Shift pressed while dragging")

    def dragEnterEvent(self, event: PySide6.QtGui.QDragEnterEvent) -> None:
        """This event is used when dragging something with
            mimedata over the widget. It will not help with detect mouse
            dragging or keyboard presses.
        """
        super(DragTests, self).dragEnterEvent(event)
        print("Hello")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ui = DragTests()
    ui.show()
    app.exec()
