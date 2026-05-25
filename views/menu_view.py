import tkinter as tk
from tkinter import font as tkfont


class MenuView(tk.Frame):
    """Start-screen with mode, card-count, and theme selection.
    Inherits from tk.Frame."""

    _GRID_LABELS = {12: "3×4", 16: "4×4", 20: "4×5"}

    def __init__(self, parent, on_start, **kwargs):
        super().__init__(parent, bg="#1a1a2e", **kwargs)
        self._on_start = on_start
        self._name2_widgets = []
        self._build()

    def _build(self):
        title_font = tkfont.Font(family="Arial", size=22, weight="bold")
        label_font = tkfont.Font(family="Arial", size=11)
        btn_font = tkfont.Font(family="Arial", size=13, weight="bold")

        tk.Label(
            self, text="Memory Game", font=title_font, bg="#1a1a2e", fg="#e94560"
        ).pack(pady=(28, 8))

        # ── Name inputs ──────────────────────────────────────────────────────
        name_frame = tk.Frame(self, bg="#1a1a2e")
        name_frame.pack(pady=6)

        tk.Label(
            name_frame, text="Player 1 Name:", bg="#1a1a2e", fg="#ffffff",
            font=label_font
        ).grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self._name1 = tk.Entry(name_frame, font=label_font, width=16)
        self._name1.insert(0, "Player 1")
        self._name1.grid(row=0, column=1, padx=6, pady=4)

        lbl2 = tk.Label(
            name_frame, text="Player 2 Name:", bg="#1a1a2e", fg="#ffffff",
            font=label_font
        )
        lbl2.grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self._name2 = tk.Entry(name_frame, font=label_font, width=16)
        self._name2.insert(0, "Player 2")
        self._name2.grid(row=1, column=1, padx=6, pady=4)
        self._name2_widgets = [lbl2, self._name2]

        # ── Game Mode ────────────────────────────────────────────────────────
        self._mode_var = tk.StringVar(value="solo")
        mode_frame = tk.LabelFrame(
            self, text="Game Mode", bg="#1a1a2e", fg="#e94560",
            font=label_font, padx=10, pady=6
        )
        mode_frame.pack(pady=6, padx=30, fill="x")
        for text, val in [
            ("1 Player (Solo)", "solo"),
            ("Human vs Human", "pvp"),
            ("Human vs AI", "pvai"),
        ]:
            tk.Radiobutton(
                mode_frame, text=text, variable=self._mode_var, value=val,
                bg="#1a1a2e", fg="#ffffff", selectcolor="#0f3460",
                activebackground="#1a1a2e", font=label_font,
                command=self._on_mode_change,
            ).pack(anchor="w")

        # ── Card Count ───────────────────────────────────────────────────────
        self._count_var = tk.IntVar(value=16)
        count_frame = tk.LabelFrame(
            self, text="Card Count", bg="#1a1a2e", fg="#e94560",
            font=label_font, padx=10, pady=6
        )
        count_frame.pack(pady=6, padx=30, fill="x")
        for count in [12, 16, 20]:
            tk.Radiobutton(
                count_frame,
                text=f"{count} cards  ({self._GRID_LABELS[count]} grid)",
                variable=self._count_var, value=count,
                bg="#1a1a2e", fg="#ffffff", selectcolor="#0f3460",
                activebackground="#1a1a2e", font=label_font,
            ).pack(anchor="w")

        # ── Theme ────────────────────────────────────────────────────────────
        self._theme_var = tk.StringVar(value="numbers")
        theme_frame = tk.LabelFrame(
            self, text="Theme", bg="#1a1a2e", fg="#e94560",
            font=label_font, padx=10, pady=6
        )
        theme_frame.pack(pady=6, padx=30, fill="x")
        for text, val in [("Numbers", "numbers"), ("Animals 🐾", "animals")]:
            tk.Radiobutton(
                theme_frame, text=text, variable=self._theme_var, value=val,
                bg="#1a1a2e", fg="#ffffff", selectcolor="#0f3460",
                activebackground="#1a1a2e", font=label_font,
            ).pack(anchor="w")

        # ── Start button ─────────────────────────────────────────────────────
        tk.Button(
            self, text="▶  Start Game", font=btn_font,
            bg="#e94560", fg="#ffffff", activebackground="#c73652",
            padx=20, pady=8, relief="flat", cursor="hand2",
            command=self._start,
        ).pack(pady=18)

        self._on_mode_change()

    def _on_mode_change(self):
        mode = self._mode_var.get()
        state = "normal" if mode == "pvp" else "disabled"
        for w in self._name2_widgets:
            try:
                w.config(state=state)
            except tk.TclError:
                pass

    def _start(self):
        mode = self._mode_var.get()
        count = self._count_var.get()
        theme = self._theme_var.get()
        name1 = self._name1.get().strip() or "Player 1"
        name2 = self._name2.get().strip() or "Player 2"
        self._on_start(mode, count, theme, name1, name2)
