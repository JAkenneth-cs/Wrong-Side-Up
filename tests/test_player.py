import pytest
from unittest.mock import MagicMock
from models.player import Player, HumanPlayer, AIPlayer


def test_player_initial_score():
    p = HumanPlayer("Alice")
    assert p.score == 0
    assert p.name == "Alice"


def test_add_score():
    p = HumanPlayer("Alice")
    p.add_score()
    p.add_score()
    assert p.score == 2


def test_reset_score():
    p = HumanPlayer("Alice")
    p.add_score()
    p.reset_score()
    assert p.score == 0


def test_human_choose_card_returns_none():
    p = HumanPlayer("Alice")
    assert p.choose_card(None, set()) is None


def _make_board(rows, cols):
    """Return a mock board with all cards unmatched."""
    board = MagicMock()
    board.rows = rows
    board.cols = cols
    card = MagicMock()
    card.is_matched = False
    board.get_card.return_value = card
    return board


def test_ai_choose_card_returns_position():
    ai = AIPlayer()
    board = _make_board(2, 2)
    pos = ai.choose_card(board, set())
    assert isinstance(pos, tuple)
    assert len(pos) == 2


def test_ai_uses_memory_for_second_flip():
    ai = AIPlayer()
    ai.remember(1, 1, "🐶")

    board = _make_board(2, 2)

    # First card flipped at (0,0) with symbol "🐶"
    first_card = MagicMock()
    first_card.is_matched = False
    first_card.symbol = "🐶"
    board.get_card.side_effect = lambda r, c: first_card if (r, c) == (0, 0) else MagicMock(is_matched=False)

    pos = ai.choose_card(board, {0})   # index 0 = (0,0) on a 2-col board
    assert pos == (1, 1)


def test_ai_reset_memory():
    ai = AIPlayer()
    ai.remember(0, 0, "X")
    ai.reset_memory()
    board = _make_board(1, 1)
    card = MagicMock()
    card.is_matched = False
    board.get_card.return_value = card
    pos = ai.choose_card(board, set())
    assert pos == (0, 0)
