import pygame
import random

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.MUSIC_END_EVENT = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
        self.music_restart_time = 0
        self.delay_ms = 1200 # 1.5 second pause
        self.is_main_menu = True
        
        # Load sound effects
        self.sfx_hover = self._load_sfx("game-assets/sfx/CLICK_001.wav")
        self.sfx_keypress = self._load_sfx("game-assets/sfx/KEY_PRESS_005.wav")
        self.sfx_flip = self._load_sfx("game-assets/sfx/FIip.mp3")
        
        # Track hover state to avoid repeating the sound every frame
        self._last_hovered = None

    def _load_sfx(self, path):
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.5)
            return sound
        except Exception as e:
            print(f"Could not load SFX '{path}': {e}")
            return None

    def play_hover(self, hovered_id):
        """Play hover sound once per unique button hover. Pass None if nothing hovered."""
        if hovered_id != self._last_hovered:
            self._last_hovered = hovered_id
            if hovered_id is not None and self.sfx_hover:
                self.sfx_hover.play()

    def play_keypress(self):
        if self.sfx_keypress:
            self.sfx_keypress.play()

    def play_flip(self):
        if self.sfx_flip:
            self.sfx_flip.play()

    def update(self, events):
        """Update logic for checking audio events."""
        for event in events:
            if event.type == self.MUSIC_END_EVENT:
                self.music_restart_time = pygame.time.get_ticks() + self.delay_ms
                
        if self.is_main_menu and self.music_restart_time > 0 and pygame.time.get_ticks() >= self.music_restart_time:
            self.music_restart_time = 0
            self.play_main_menu_music()

    def play_main_menu_music(self):
        try:
            self.is_main_menu = True
            pygame.mixer.music.load("game-assets/music/Main Menu-timestrech.mp3")
            pygame.mixer.music.play(0)
        except Exception as e:
            print(f"Could not load main menu music: {e}")

    def play_gameplay_music(self):
        try:
            self.is_main_menu = False
            self.music_restart_time = 0
            pygame.mixer.music.load("game-assets/music/Play.mp3")
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Could not load gameplay music: {e}")

    def get_current_bg_index(self, bpm=120, offset_ms=0):
        """Returns 0 (bg1/High Tone) or 1 (bg2/Low Tone) by alternating perfectly on the beat."""
        music_pos = pygame.mixer.music.get_pos()
        if music_pos == -1:
            return 0
            
        adjusted_pos = music_pos - offset_ms
        ms_per_beat = 60000 / bpm
        current_beat = int(adjusted_pos / ms_per_beat)
        
        if current_beat % 2 == 0:
            return 0
        else:
            return 1
