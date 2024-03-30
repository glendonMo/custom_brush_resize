""" Python implementation of kis_input_button.cpp. This allows the user to set
    shortcuts in a way that feels familiar in Krita.
    https://github.com/KDE/krita/blob/master/libs/ui/input/config/kis_input_button.cpp
"""

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from .config import (
    keys_to_text,
    buttons_input_to_text,
    ShortcutType,
)


class KisInputButton(QtWidgets.QPushButton):
    """A QPushButton that records the user's input.
    After pressing the button, the user can either use
    keys or mouse buttons to set the button's label.
    """

    buttons: Qt.MouseButtons = None
    keys: list[Qt.Key] = list()
    shortcut_type: ShortcutType = ShortcutType.MouseButtonType
    accept_new_input: bool = True
    dataChanged = QtCore.pyqtSignal()

    def __init__(self, shortcut_type=None, parent=None) -> None:
        super(KisInputButton, self).__init__(parent=parent)
        self.accept_new_input = True
        self.shortcut_type = shortcut_type or ShortcutType.MouseButtonType
        self.setCheckable(True)

        self.reset_timer = QtCore.QTimer()
        self.reset_timer.setInterval(5000)
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.reset)

    def update_label(self) -> None:
        """Update the button's label with the display names of
        the pressed keys and buttons.
        """
        if self.shortcut_type == ShortcutType.MouseButtonType:
            self.setText(buttons_input_to_text(self.keys, self.buttons))
        elif self.shortcut_type == ShortcutType.KeyCombinationType:
            self.setText(keys_to_text(self.keys))

    def reset(self):
        """Update the button label and stop recording user input."""
        self.setChecked(False)
        self.update_label()
        self.dataChanged.emit()

    @staticmethod
    def remap_to_alt_key(event) -> Qt.Key:
        """Change the event key to the `Alt` key under certain conditions."""
        key = event.key()
        if key == Qt.Key_Meta and event.modifiers().testFlag(Qt.ShiftModifier):
            key = Qt.Key_Alt
        return key

    def mousePressEvent(self, event):
        """Change the label text if the user has already clicked the button."""
        if not self.isChecked():
            return
        self.buttons = event.buttons()
        self.update_label()
        self.reset_timer.start()

    def mouseReleaseEvent(self, event):
        """Accept user input after the user clicks the button."""
        if not self.isChecked():
            self.setChecked(True)
            self.setText("Awaiting Input...")
            self.reset_timer.start()
            self.accept_new_input = True
            return
        self.reset()

    def keyPressEvent(self, event):
        """Add pressed keys to button label."""
        if not self.isChecked():
            return
        if self.accept_new_input:
            self.keys = []
            self.accept_new_input = False
        key = self.remap_to_alt_key(event)
        self.keys.append(key)
        self.update_label()
        self.reset_timer.start()

    def keyReleaseEvent(self, event):
        """Update label with previously pressed keys.
        If the Enter key is used, accept user input.
        """
        if not self.isChecked():
            if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                self.setChecked(True)
                self.setText("Key Input...")
                self.accept_new_input = True
                self.reset_timer.start()
                return
        self.reset()


# Testing
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ui = KisInputButton()
    ui.show()
    app.exec()
