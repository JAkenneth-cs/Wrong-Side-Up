class Card:

    def __init__(self, symbol):
        self._symbol = symbol
        self._is_face_up = False
        self._is_matched = False

    @property
    def symbol(self):
        return self._symbol

    @property
    def is_face_up(self):
        return self._is_face_up

    @property
    def is_matched(self):
        return self._is_matched

    def flip(self):
        if not self._is_matched:
            self._is_face_up = not self._is_face_up

    def set_matched(self):
        self._is_matched = True
        self._is_face_up = True

    def reset(self):
        self._is_face_up = False
        self._is_matched = False

    def get_display(self):
        """Polymorphic: subclasses override to change how the symbol looks."""
        if self._is_face_up or self._is_matched:
            return str(self._symbol)
        return "?"
