import pytest
from models.board import Board
from models.player import HumanPlayer
from models.game_mode import SoloMode, PvPMode
from models.game_state import GameState, State


def _find_pair(board):
    """Return positions of the first matching pair on the board."""
    seen = {}
    for r in range(board.rows):
        for c in range(board.cols):
            card = board.get_card(r, c)
            if card.symbol in seen:
                return seen[card.symbol], (r, c)
            seen[card.symbol] = (r, c)
    raise RuntimeError("No pair found")


def test_initial_state_is_idle():
    board = Board(12)
    gs = GameState(board, SoloMode(HumanPlayer("A")))
    assert gs.state == State.IDLE


def test_start_moves_to_first_flip():
    board = Board(12)
    gs = GameState(board, SoloMode(HumanPlayer("A")))
    gs.start()
    assert gs.state == State.FIRST_FLIP


def test_first_flip_transitions():
    board = Board(12)
    gs = GameState(board, SoloMode(HumanPlayer("A")))
    gs.start()
    card = board.get_card(0, 0)
    result = gs.handle_flip(card, 0, 0)
    assert result == "flipped_first"
    assert gs.state == State.SECOND_FLIP
    assert card.is_face_up


def test_same_card_returns_same_card():
    board = Board(12)
    gs = GameState(board, SoloMode(HumanPlayer("A")))
    gs.start()
    card = board.get_card(0, 0)
    gs.handle_flip(card, 0, 0)
    result = gs.handle_flip(card, 0, 0)
    assert result == "same_card"


def test_resolve_match_marks_matched():
    board = Board(12)
    gs = GameState(board, SoloMode(HumanPlayer("A")))
    gs.start()
    (r1, c1), (r2, c2) = _find_pair(board)
    gs.handle_flip(board.get_card(r1, c1), r1, c1)
    gs.handle_flip(board.get_card(r2, c2), r2, c2)
    result = gs.resolve()
    assert result == "match"
    assert board.get_card(r1, c1).is_matched
    assert board.get_card(r2, c2).is_matched


def test_resolve_miss_resets_cards():
    board = Board(12)
    gs = GameState(board, SoloMode(HumanPlayer("A")))
    gs.start()
    # Find two non-matching cards
    seen = {}
    mismatched = []
    for r in range(board.rows):
        for c in range(board.cols):
            card = board.get_card(r, c)
            if card.symbol not in seen:
                seen[card.symbol] = (r, c)
                mismatched.append((r, c))
            if len(mismatched) == 2:
                break
        if len(mismatched) == 2:
            break

    if board.get_card(*mismatched[0]).symbol == board.get_card(*mismatched[1]).symbol:
        pytest.skip("Random board happened to give matching pair")

    r1, c1 = mismatched[0]
    r2, c2 = mismatched[1]
    gs.handle_flip(board.get_card(r1, c1), r1, c1)
    gs.handle_flip(board.get_card(r2, c2), r2, c2)
    result = gs.resolve()
    assert result == "miss"
    assert not board.get_card(r1, c1).is_face_up
    assert not board.get_card(r2, c2).is_face_up


def test_game_over_when_complete():
    board = Board(12)
    gs = GameState(board, SoloMode(HumanPlayer("A")))
    gs.start()
    # Match every pair
    while not board.is_complete():
        seen = {}
        for r in range(board.rows):
            for c in range(board.cols):
                card = board.get_card(r, c)
                if card.is_matched:
                    continue
                if card.symbol in seen:
                    r2, c2 = seen[card.symbol]
                    gs.handle_flip(board.get_card(r2, c2), r2, c2)
                    gs.handle_flip(card, r, c)
                    gs.resolve()
                    break
                seen[card.symbol] = (r, c)
    assert gs.state == State.GAME_OVER


def test_pvp_turn_advances_on_miss():
    board = Board(12)
    p1 = HumanPlayer("A")
    p2 = HumanPlayer("B")
    mode = PvPMode(p1, p2)
    gs = GameState(board, mode)
    gs.start()
    assert mode.current_player is p1

    seen = {}
    mismatched = []
    for r in range(board.rows):
        for c in range(board.cols):
            card = board.get_card(r, c)
            if card.symbol not in seen:
                seen[card.symbol] = (r, c)
                mismatched.append((r, c))
            if len(mismatched) == 2:
                break
        if len(mismatched) == 2:
            break

    if board.get_card(*mismatched[0]).symbol == board.get_card(*mismatched[1]).symbol:
        pytest.skip("Random board gave matching pair")

    r1, c1 = mismatched[0]
    r2, c2 = mismatched[1]
    gs.handle_flip(board.get_card(r1, c1), r1, c1)
    gs.handle_flip(board.get_card(r2, c2), r2, c2)
    gs.resolve()
    assert mode.current_player is p2
