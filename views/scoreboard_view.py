import tkinter as tk


class ScoreboardView(tk.Frame):
    """Displays current player, scores, and turn info. Inherits from tk.Frame."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#0f3460", **kwargs)
        self._turn_label = tk.Label(
            self, text="", font=("Arial", 13, "bold"), bg="#0f3460", fg="#e94560"
        )
        self._turn_label.pack(pady=(6, 2))

        self._info_label = tk.Label(
            self, text="", font=("Arial", 11), bg="#0f3460", fg="#ffffff"
        )
        self._info_label.pack(pady=(0, 6))

    def update(self, game_mode, extra_info=""):
        """Refresh labels based on the current game mode state."""
        from models.game_mode import SoloMode
        current = game_mode.current_player

        if isinstance(game_mode, SoloMode):
            self._turn_label.config(text=f"Player: {current.name}")
            info = f"Matches: {current.score}     Turns: {game_mode.turns}"
        else:
            self._turn_label.config(text=f"Turn: {current.name}")
            scores = "     ".join(f"{p.name}: {p.score}" for p in game_mode.players)
            info = scores

        if extra_info:
            info += f"     {extra_info}"
        self._info_label.config(text=info)
