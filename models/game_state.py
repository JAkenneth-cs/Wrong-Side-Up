import json
import os
from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    FIRST_FLIP = auto()
    SECOND_FLIP = auto()
    CHECKING = auto()
    GAME_OVER = auto()


class GameState:
    """Manages the turn state machine. Demonstrates Encapsulation — all state
    transitions are guarded internally; no external code can corrupt the sequence."""

    def __init__(self, board, game_mode):
        self._board = board
        self._game_mode = game_mode
        self._state = State.IDLE
        self._first_card = None
        self._first_pos = None
        self._second_card = None
        self._second_pos = None

    @property
    def state(self):
        return self._state

    @property
    def game_mode(self):
        return self._game_mode

    @property
    def first_pos(self):
        return self._first_pos

    @property
    def second_pos(self):
        return self._second_pos

    def start(self):
        self._game_mode.start_game()
        self._state = State.FIRST_FLIP

    def handle_flip(self, card, row, col):
        """Flip a card and advance state. Returns a result string."""
        if self._state == State.FIRST_FLIP:
            if card.is_matched or card.is_face_up:
                return "ignored"
            self._first_card = card
            self._first_pos = (row, col)
            card.flip()
            self._state = State.SECOND_FLIP
            return "flipped_first"

        if self._state == State.SECOND_FLIP:
            if (row, col) == self._first_pos:
                return "same_card"
            if card.is_matched or card.is_face_up:
                return "ignored"
            self._second_card = card
            self._second_pos = (row, col)
            card.flip()
            self._state = State.CHECKING
            return "flipped_second"

        return "ignored"

    def resolve(self):
        """Check the two flipped cards and update state. Returns 'match' or 'miss'."""
        if self._state != State.CHECKING:
            return None

        if self._board.check_match(self._first_card, self._second_card):
            self._first_card.set_matched()
            self._second_card.set_matched()
            self._game_mode.on_match(self._first_card.symbol)
            result = "match"
        else:
            self._first_card.flip()   # face down again
            self._second_card.flip()
            self._game_mode.on_miss()
            result = "miss"

        self._first_card = None
        self._first_pos = None
        self._second_card = None
        self._second_pos = None

        if self._board.is_complete():
            self._state = State.GAME_OVER
            self._game_mode.end_game()
        else:
            self._state = State.FIRST_FLIP

        return result

    def timeout_turn(self):
        """Called when a turn times out without playing."""
        if self._state == State.FIRST_FLIP:
            self._game_mode.on_miss()
        elif self._state == State.SECOND_FLIP:
            if self._first_card:
                self._first_card.flip()
            self._first_card = None
            self._first_pos = None
            self._state = State.FIRST_FLIP
            self._game_mode.on_miss()

    def update(self):
        """Pass update tick to the game mode (e.g. for timers)."""
        if self._state != State.GAME_OVER:
            self._game_mode.update()
            
            t = self._game_mode.turn_time_remaining
            if t is not None and t == 0 and self._state in [State.FIRST_FLIP, State.SECOND_FLIP]:
                self.timeout_turn()
                
            if self._game_mode.is_game_over:
                self._state = State.GAME_OVER

    def reset(self, board, game_mode):
        self._board = board
        self._game_mode = game_mode
        self._state = State.IDLE
        self._first_card = None
        self._first_pos = None
        self._second_card = None
        self._second_pos = None


class HighScoreTracker:
    """Persists top-5 scores per mode to a JSON file. Demonstrates Encapsulation
    — file path and data structure are private."""

    def __init__(self, filepath="scores.json"):
        self._filepath = filepath
        self._scores = {"solo": [], "pvp": [], "pvai": []}
        if os.path.exists(filepath):
            try:
                with open(filepath, encoding="utf-8") as f:
                    self._scores = json.load(f)
            except (json.JSONDecodeError, KeyError):
                pass

    def record_score(self, mode_key, player_name, score):
        """Add a score entry and keep only the top 5."""
        bucket = self._scores.setdefault(mode_key, [])
        bucket.append({"name": player_name, "score": score})
        bucket.sort(key=lambda x: x["score"], reverse=True)
        self._scores[mode_key] = bucket[:5]
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._scores, f, indent=2)

    def get_top_scores(self, mode_key):
        return list(self._scores.get(mode_key, []))
