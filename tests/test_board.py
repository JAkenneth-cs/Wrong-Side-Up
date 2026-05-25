import pytest
from models.board import Board


def test_grid_12():
    b = Board(12)
    assert b.rows == 3 and b.cols == 4
    assert len(b.get_all_cards()) == 12


def test_grid_16():
    b = Board(16)
    assert b.rows == 4 and b.cols == 4


def test_grid_20():
    b = Board(20)
    assert b.rows == 4 and b.cols == 5


def test_all_symbols_appear_exactly_twice():
    for count in [12, 16, 20]:
        b = Board(count)
        symbols = [b.get_card(r, c).symbol for r in range(b.rows) for c in range(b.cols)]
        for sym in set(symbols):
            assert symbols.count(sym) == 2, f"symbol {sym!r} not paired in {count}-card board"


def test_check_match_true():
    b = Board(12)
    seen = {}
    for r in range(b.rows):
        for c in range(b.cols):
            card = b.get_card(r, c)
            if card.symbol in seen:
                other = seen[card.symbol]
                assert b.check_match(card, other)
                return
            seen[card.symbol] = card


def test_check_match_false_same_object():
    b = Board(12)
    card = b.get_card(0, 0)
    assert not b.check_match(card, card)


def test_not_complete_initially():
    b = Board(16)
    assert not b.is_complete()


def test_complete_after_all_matched():
    b = Board(12)
    for card in b.get_all_cards():
        card.set_matched()
    assert b.is_complete()


def test_invalid_count_raises():
    with pytest.raises(ValueError):
        Board(8)
