import random
from models.card import Card

GRID_SIZES = {
    "Easy": (2, 6),    # 12 cards = 6 pairs
    "Moderate": (3, 6),  # 18 cards = 9 pairs
    "Hard": (4, 7)     # 28 cards = 14 pairs
}

class Board:
    """Manages the card grid. Demonstrates Encapsulation — _cards is private
    and all access goes through public methods."""

    def __init__(self, difficulty="Easy"):
        if difficulty not in GRID_SIZES:
            raise ValueError(f"difficulty must be one of {list(GRID_SIZES.keys())}")
        self._difficulty = difficulty
        self._rows, self._cols = GRID_SIZES[difficulty]
        self._card_count = self._rows * self._cols
        self._cards = []
        self._build()

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def card_count(self):
        return self._card_count

    def _build(self):
        pairs = self._card_count // 2
        # Symbols are simply 1 to 32, which will later map to the 32 unique placeholder images
        symbols = list(range(1, pairs + 1))
        
        # Create pairs of cards
        self._cards = [Card(s) for s in symbols * 2]
        random.shuffle(self._cards)

    def get_card(self, row, col):
        return self._cards[row * self._cols + col]

    def check_match(self, card1, card2):
        return card1.symbol == card2.symbol and card1 is not card2

    def is_complete(self):
        return all(c.is_matched for c in self._cards)

    def reset(self):
        self._build()

    def get_all_cards(self):
        return list(self._cards)
