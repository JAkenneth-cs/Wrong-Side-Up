import tkinter as tk
from tkinter import messagebox

from models.board import Board
from models.player import HumanPlayer, AIPlayer
from models.game_mode import SoloMode, PvPMode, PvAIMode
from models.game_state import GameState
from views.board_view import BoardView
from views.scoreboard_view import ScoreboardView

AI_THINK_MS = 900   # delay between AI moves so it looks deliberate


class GameController:
    """Wires models to views and handles all user interaction.
    Calls game_mode.on_match() / on_miss() and player.choose_card()
    without knowing the concrete subtype — Polymorphism at the controller level."""

    def __init__(self, root, container, on_back_to_menu, score_tracker=None):
        self._root = root
        self._container = container
        self._on_back_to_menu = on_back_to_menu
        self._score_tracker = score_tracker

        self._board = None
        self._game_state = None
        self._game_mode = None
        self._board_view = None
        self._scoreboard = None
        self._mode_key = "solo"
        self._locked = False
        self._frame = None

    # ── Public ───────────────────────────────────────────────────────────────

    @property
    def frame(self):
        return self._frame

    def start(self, mode, card_count, theme, name1, name2):
        """Initialise a new game and return the frame to display."""
        self._mode_key = mode
        self._locked = False
        self._frame = tk.Frame(self._container, bg="#16213e")
        self._board = Board(card_count, theme)

        if mode == "solo":
            self._game_mode = SoloMode(HumanPlayer(name1))
        elif mode == "pvp":
            self._game_mode = PvPMode(HumanPlayer(name1), HumanPlayer(name2))
        else:
            self._game_mode = PvAIMode(HumanPlayer(name1), AIPlayer("Computer"))

        self._game_state = GameState(self._board, self._game_mode)
        self._game_state.start()
        self._build_ui()
        return self._frame

    # ── Private — UI construction ─────────────────────────────────────────────

    def _build_ui(self):
        for w in self._frame.winfo_children():
            w.destroy()

        top_bar = tk.Frame(self._frame, bg="#16213e")
        top_bar.pack(fill="x", padx=10, pady=(8, 0))
        tk.Button(
            top_bar, text="← Menu", command=self._back_to_menu,
            bg="#e94560", fg="#ffffff", relief="flat",
            font=("Arial", 10, "bold"), cursor="hand2",
        ).pack(side="left")

        self._scoreboard = ScoreboardView(self._frame)
        self._scoreboard.pack(fill="x", padx=10, pady=4)

        self._board_view = BoardView(self._frame, self._board, self._on_card_click)
        self._board_view.pack(padx=20, pady=10)

        self._scoreboard.update(self._game_mode)

    # ── Private — human click flow ────────────────────────────────────────────

    def _on_card_click(self, row, col):
        if self._locked:
            return
        if self._game_state.state.name == "GAME_OVER":
            return

        card = self._board.get_card(row, col)
        result = self._game_state.handle_flip(card, row, col)

        if result in ("flipped_first", "flipped_second"):
            self._board_view.refresh()
            self._scoreboard.update(self._game_mode)

        if result == "flipped_second":
            self._locked = True
            self._root.after(700, self._resolve)

    def _resolve(self):
        self._game_state.resolve()
        self._board_view.refresh()
        self._scoreboard.update(self._game_mode)
        self._locked = False

        if self._game_state.state.name == "GAME_OVER":
            self._root.after(400, self._end_game)
            return

        if self._game_mode.is_ai_turn():
            self._locked = True
            self._root.after(AI_THINK_MS, self._do_ai_first_flip)

    # ── Private — AI turn flow ────────────────────────────────────────────────

    def _do_ai_first_flip(self):
        ai = self._game_mode.current_player
        pos = ai.choose_card(self._board, set())
        if pos is None:
            self._locked = False
            return

        card = self._board.get_card(pos[0], pos[1])
        ai.remember(pos[0], pos[1], card.symbol)
        self._game_state.handle_flip(card, pos[0], pos[1])
        self._board_view.refresh()

        first_idx = pos[0] * self._board.cols + pos[1]
        self._root.after(AI_THINK_MS, lambda: self._do_ai_second_flip(ai, {first_idx}))

    def _do_ai_second_flip(self, ai, flipped):
        pos = ai.choose_card(self._board, flipped)
        if pos is None:
            self._locked = False
            return

        card = self._board.get_card(pos[0], pos[1])
        ai.remember(pos[0], pos[1], card.symbol)
        self._game_state.handle_flip(card, pos[0], pos[1])
        self._board_view.refresh()

        self._root.after(700, self._resolve)

    # ── Private — game over ───────────────────────────────────────────────────

    def _end_game(self):
        winner = self._game_mode.get_winner()

        if isinstance(self._game_mode, SoloMode):
            msg = (
                f"Well done, {winner.name}!\n\n"
                f"Matches: {winner.score}\n"
                f"Turns taken: {self._game_mode.turns}"
            )
            if self._score_tracker:
                self._score_tracker.record_score("solo", winner.name, winner.score)
        else:
            scores = "\n".join(f"  {p.name}: {p.score}" for p in self._game_mode.players)
            msg = f"Game Over!\n\nWinner: {winner.name}\n\n{scores}"
            if self._score_tracker:
                self._score_tracker.record_score(self._mode_key, winner.name, winner.score)

        answer = messagebox.askquestion(
            "Game Over", msg + "\n\nPlay again?", icon="info"
        )
        if answer == "yes":
            self._play_again()
        else:
            self._back_to_menu()

    def _play_again(self):
        self._board.reset()
        self._game_mode.reset()
        for p in self._game_mode.players:
            if isinstance(p, AIPlayer):
                p.reset_memory()
        self._game_state.reset(self._board, self._game_mode)
        self._game_state.start()
        self._locked = False
        self._board_view.rebuild(self._board)
        self._scoreboard.update(self._game_mode)

    def _back_to_menu(self):
        self._frame.pack_forget()
        self._on_back_to_menu()
