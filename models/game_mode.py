import time
import random
from abc import ABC, abstractmethod

class GameMode(ABC):
    """Base class for game modes. Manages players, turns, and core match/miss logic."""
    def __init__(self, players):
        self._players = players
        # Randomly choose who goes first
        self._current_player_idx = random.randint(0, len(players) - 1) if players else 0
        self._is_game_over = False
        self._turn_start_time = None
        self._turn_time_limit = 10 # 10 seconds

    @property
    def turn_time_remaining(self):
        if not self._turn_start_time:
            return self._turn_time_limit
        elapsed = time.time() - self._turn_start_time
        return max(0, self._turn_time_limit - elapsed)

    def reset_turn_timer(self):
        self._turn_start_time = time.time()

    @property
    def current_player(self):
        return self._players[self._current_player_idx]

    @property
    def players(self):
        return self._players

    @property
    def is_game_over(self):
        return self._is_game_over

    def on_match(self, symbol):
        self.current_player.add_score(symbol)
        self.reset_turn_timer()

    def on_miss(self):
        self._next_turn()
        self.reset_turn_timer()

    def _next_turn(self):
        if self._players:
            self._current_player_idx = (self._current_player_idx + 1) % len(self._players)

    def start_game(self):
        """Hook to initialize game start (like timers)."""
        self.reset_turn_timer()

    def update(self):
        """Called every frame. Used for timers or real-time logic."""
        pass

    def end_game(self):
        self._is_game_over = True


class SoloMode(GameMode):
    """Solo mode with timer-based win/loss conditions."""
    def __init__(self, players, difficulty="Easy"):
        super().__init__(players)
        self._difficulty = difficulty
        self._start_time = None
        self._time_limit = self._get_time_limit(difficulty)
        self._time_remaining = self._time_limit
        self._won = False

    def _get_time_limit(self, difficulty):
        if difficulty == "Easy": return 5 * 60
        if difficulty == "Moderate": return 3 * 60
        if difficulty == "Difficult": return 2 * 60
        return 60

    @property
    def time_remaining(self):
        return self._time_remaining
        
    @property
    def turn_time_remaining(self):
        return None # Solo mode doesn't have a 10s turn limit
        
    @property
    def won(self):
        return self._won

    def start_game(self):
        self._start_time = time.time()

    def update(self):
        if not self._is_game_over and self._start_time:
            elapsed = time.time() - self._start_time
            self._time_remaining = max(0, self._time_limit - elapsed)
            if self._time_remaining == 0:
                self.end_game(won=False)

    def end_game(self, won=True):
        super().end_game()
        self._won = won


class PVPMode(GameMode):
    """Player vs Player mode. Inherits standard turn logic."""
    pass


class PVAIMode(GameMode):
    """Player vs AI mode. Standard turn logic, but one player is AI."""
    def __init__(self, players, difficulty="Easy"):
        super().__init__(players)
        self._difficulty = difficulty
