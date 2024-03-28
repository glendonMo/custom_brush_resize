import sys

from PySide6 import QtCore, QtGui, QtWidgets

class QMouseKeySequence(QtCore.QObject):
    def __init__(self):
        super(QMouseKeySequence, self).__init__()


class QMouseKeySequenceButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(QMouseKeySequenceButton, self).__init__(parent=parent)

class MouseKeySequenceTests(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = MouseKeySequenceTests()
    gui.show()
    sys.exit(app.exec())