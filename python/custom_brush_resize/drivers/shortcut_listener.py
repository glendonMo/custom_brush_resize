from PyQt5 import QtWidgets, QtCore

from ..ui.config import text_input_to_buttons


ACCEPTED_EVENT_TYPES = [
    QtCore.QEvent.KeyRelease,
    QtCore.QEvent.MouseButtonRelease,
    QtCore.QEvent.KeyPress,
    QtCore.QEvent.MouseButtonPress,
    QtCore.QEvent.MouseMove,
]


class ShortcutListener(QtWidgets.QMdiArea):
    """Main event loop used to process user input.
    The eventFilter of this object will start running
    from the moment krita starts.
    It will monitor the button and key presses from the user.
    """

    button_pressed = QtCore.pyqtSignal(QtCore.Qt.MouseButton)
    button_released = QtCore.pyqtSignal(QtCore.Qt.MouseButton)
    key_pressed = QtCore.pyqtSignal(QtCore.Qt.Key)
    key_released = QtCore.pyqtSignal(QtCore.Qt.Key)

    shortcut_pressed = QtCore.pyqtSignal(bool)
    shortcut_pressed_while_dragging = QtCore.pyqtSignal(bool)

    def __init__(self, shortcut=None, parent=None):
        super(ShortcutListener, self).__init__(parent=parent)
        self.shortcut = shortcut

        self.shortcut_keys_pressed = {}
        self.shortcut_buttons_pressed = {}

        self.initialize_shortcut_presses()

    def set_shortcut(self, shortcut):
        """Set shortcut to given shortcut."""
        self.shortcut = shortcut
        self.initialize_shortcut_presses()

    def initialize_shortcut_presses(self):
        """Set the intial press state for each key and
        button in the current shortcut."""
        buttons, keys = text_input_to_buttons(self.shortcut)
        self.shortcut_buttons_pressed.clear()
        self.shortcut_keys_pressed.clear()
        for button in buttons:
            self.shortcut_buttons_pressed[button] = False
        for key in keys:
            self.shortcut_keys_pressed[key] = False

    def eventFilter(self, obj, event):
        """Overriding evenFilter to catch accepted event types.
        The mouse button and key presses are monitored here.
        When the user presses/releases a key or mouse button that
        belongs to the current shortcut, it's `pressed` state is
        updated in shortcut_buttons_pressed or shortcut_keys_pressed.
        """
        event_type = event.type()

        # Ignore all none accecpted event types
        if event_type not in ACCEPTED_EVENT_TYPES:
            return False

        # Evaluate asscepted event types
        # Is user pressing a shortcut key?
        if event_type == QtCore.QEvent.KeyPress:
            if self._can_press_key(event.key()):
                self.shortcut_keys_pressed[event.key()] = True
                self.key_pressed.emit(event.key())

        # User released shorcut key
        if event_type == QtCore.QEvent.KeyRelease:
            self._release_pressed(event.key())
            self.key_released.emit(event.key())
            return False

        # Is user pressing a shortcut mouse button?
        if event_type == QtCore.QEvent.MouseButtonPress:
            if self._can_press_button(event.button()):
                self.shortcut_buttons_pressed[event.button()] = True
                self.button_pressed.emit(event.button())

        # User released shorcut mouse button
        if event_type == QtCore.QEvent.MouseButtonRelease:
            self._release_pressed(event.button())
            self.button_released.emit(event.button())
            return False

        # User is pressing all shortcut buttons and keys
        if self.is_shortcut_pressed:
            self.shortcut_pressed.emit(True)
            if event_type == QtCore.QEvent.MouseMove:
                self.shortcut_pressed_while_dragging.emit(True)
        return False

    def _can_press_key(self, key):
        """Confirm whether given key can be pressed."""
        _, keys = text_input_to_buttons(self.shortcut)
        return key in keys and not self.shortcut_keys_pressed[key]

    def _can_press_button(self, button):
        """Confirm whether given button can be pressed."""
        buttons, _ = text_input_to_buttons(self.shortcut)
        return button in buttons and not self.shortcut_buttons_pressed[button]

    def _release_pressed(self, item):
        buttons, keys = text_input_to_buttons(self.shortcut)
        if item in buttons:
            self.shortcut_buttons_pressed[item] = False
        if item in keys:
            self.shortcut_keys_pressed[item] = False

    @property
    def is_shortcut_pressed(self):
        """Confirm whether current set shortcut is being pressed."""
        keys_pressed = [
            self.shortcut_keys_pressed[key]
            for key in self.shortcut_keys_pressed
        ]
        buttons_pressed = [
            self.shortcut_buttons_pressed[button]
            for button in self.shortcut_buttons_pressed
        ]

        return all(buttons_pressed + keys_pressed)
