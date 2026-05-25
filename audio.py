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
            # Load the new timestretched track
            pygame.mixer.music.load("game-assets/music/Main Menu-timestrech.mp3")
            pygame.mixer.music.play(0) # Play once, handled by update() for loop with delay
        except Exception as e:
            print(f"Could not load main menu music: {e}")

    def play_gameplay_music(self):
        try:
            self.is_main_menu = False
            self.music_restart_time = 0
            pygame.mixer.music.load("game-assets/music/Play.mp3")
            pygame.mixer.music.play(-1) # Play repeatedly in a loop
        except Exception as e:
            print(f"Could not load gameplay music: {e}")

    def get_current_bg_index(self, bpm=120, offset_ms=0):
        """Returns 0 (bg1/High Tone) or 1 (bg2/Low Tone) by alternating perfectly on the beat."""
        music_pos = pygame.mixer.music.get_pos()
        if music_pos == -1:
            # Music is paused/stopped, default to bg1
            return 0
            
        adjusted_pos = music_pos - offset_ms
        ms_per_beat = 60000 / bpm
        
        # Determine which total beat we are currently on (0, 1, 2, 3...)
        current_beat = int(adjusted_pos / ms_per_beat)
        
        # Alternate backgrounds based on if the beat is an even or odd number!
        if current_beat % 2 == 0:
            return 0 # bg1 (High Tone / Green)
        else:
            return 1 # bg2 (Low Tone / Black)
