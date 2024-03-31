import sys
from PySide6 import QtCore, QtGui, QtWidgets
import typing
from PySide6.QtCore import Qt


def buttonsToText(buttons: QtCore.Qt.MouseButtons):
    text = ""
    separator = "+"
    button_count = 0

    if buttons & QtCore.Qt.LeftButton:
        text = "Left"
        button_count += 1
    if buttons & QtCore.Qt.RightButton:
        if button_count > 0:
            text += separator
        text += "Right"
    if buttons & QtCore.Qt.MiddleButton:
        if button_count > 0:
            text += separator
        text += "Middle"
    return text


def keysToText(keys: list[QtCore.Qt.Key]):
    print("KEYS:")
    print(keys)
    text = ""
    separator = "+"
    key_name_map = {
        QtCore.Qt.Key_Control: "Ctrl",
        QtCore.Qt.Key_Meta: "Meta",
        QtCore.Qt.Key_Alt: "Alt",
        QtCore.Qt.Key_Shift: "Shift",
    }
    for key in keys:
        if len(text) > 0:
            text += separator
        key_name = key_name_map.get(key)
        if not key_name:
            key_name = QtGui.QKeySequence(key).toString(QtGui.QKeySequence.NativeText)
        text += key_name
    if len(text) == 0:
        text += "None"
    print(f"KEY TEXT: {text}")
    return text


def buttonsInputToText(keys, buttons):
    button_text = buttonsToText(buttons)
    if len(keys) > 0:
        keys_text = keysToText(keys)
        return button_text + "+" + keys_text
    return button_text


class KisInputButton(QtWidgets.QPushButton):

    dataChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(KisInputButton, self).__init__(parent=parent)
        self.buttons = None
        self.keys = None
        self._type = None
        self._new_input = True
        self.reset_timer = QtCore.QTimer()

        self.set_defaults()
        self.connections()

    def set_defaults(self):
        self.reset_timer.setInterval(5000)
        self.reset_timer.setSingleShot(True)
        self.setCheckable(True)

    def connections(self):
        self.reset_timer.timeout.connect(self.reset)

    def update_label(self):
        print("Update Label")
        if self._type == QtCore.Qt.MouseButton:
            self.setText(buttonsToText(self.buttons))
            return
        if self._type == QtCore.Qt.Key:
            self.setText(keysToText(self.keys))

    def clear(self):
        pass

    def reset(self):
        print("Resetting")
        self.setChecked(False)
        self.update_label()
        self.dataChanged.emit()
        pass

    def mousePressEvent(self, event):
        print("Mouse press")
        if self.isChecked():
            self.buttons = event.buttons()
            self._type = QtCore.Qt.MouseButton
            self.update_label()
            self.reset_timer.start()

    def mouseReleaseEvent(self, event):
        print("Mouse release")
        print(self.isChecked())
        if self.isChecked():
            self.reset()
            return
        self.setChecked(True)
        print(self.isChecked())
        self.setText("Input...")
        self.reset_timer.start()
        self._new_input = True
        super(KisInputButton, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if self.isChecked():
            if self._new_input:
                print("_new_input TRUE")
                self.keys = []
                print(self.keys)
                self._new_input = False
            key = event.key()
            if key == QtCore.Qt.Key_Meta and event.modifiers().testFlag(
                QtCore.Qt.ShiftModifier
            ):
                key = QtCore.Qt.Key_Alt
            print(f"NEW KEY: {key}")
            self.keys.append(key)
            self._type = QtCore.Qt.Key
            self.update_label()
            self.reset_timer.start()

        super(KisInputButton, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.isChecked():
            self.reset()
            return
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.setChecked(True)
            self.setText("Key Input...")
            self._new_input = True
            self.reset_timer.start()
        super(KisInputButton, self).keyReleaseEvent(event)

    def wheelEvent(self, event):
        pass


class KritaInputWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.button = KisInputButton(self)
        self.layout().addWidget(self.button)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = KritaInputWidget()
    gui.show()
    sys.exit(app.exec())
