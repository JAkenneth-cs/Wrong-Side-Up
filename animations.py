import pygame
from ui import create_rounded_surface

class FlyingCard:
    def __init__(self, img, start_x, start_y, target_x, target_y, target_w, target_h, owner=None, duration=600):
        self.img = img
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.target_w = target_w
        self.target_h = target_h
        self.owner = owner
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.current_x = start_x
        self.current_y = start_y
        self.is_done = False
        self.progress_ease = 0.0

    def update(self):
        if self.is_done:
            return
            
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            self.current_x = self.target_x
            self.current_y = self.target_y
            self.progress_ease = 1.0
            self.is_done = True
        else:
            # Ease out cubic interpolation for smoother animation
            self.progress_ease = 1 - pow(1 - progress, 3)
            self.current_x = self.start_x + (self.target_x - self.start_x) * self.progress_ease
            self.current_y = self.start_y + (self.target_y - self.start_y) * self.progress_ease

    def draw(self, screen, orig_w, orig_h):
        if not self.is_done:
            current_w = int(orig_w + (self.target_w - orig_w) * self.progress_ease)
            current_h = int(orig_h + (self.target_h - orig_h) * self.progress_ease)
            if current_w > 0 and current_h > 0:
                scaled_img = pygame.transform.smoothscale(self.img, (current_w, current_h))
                scaled_img = create_rounded_surface(scaled_img, radius=8)
                screen.blit(scaled_img, (int(self.current_x), int(self.current_y)))

class AnimationManager:
    def __init__(self):
        self.flying_cards = []

    def add_flying_card(self, img, start_x, start_y, target_x, target_y, target_w, target_h, owner=None):
        self.flying_cards.append(FlyingCard(img, start_x, start_y, target_x, target_y, target_w, target_h, owner))

    def update_and_draw(self, screen, card_width, card_height):
        # Update
        for card in self.flying_cards:
            card.update()
        
        # Remove done cards
        self.flying_cards = [c for c in self.flying_cards if not c.is_done]
        
        # Draw
        for card in self.flying_cards:
            card.draw(screen, card_width, card_height)

class FlipAnimator:
    def __init__(self):
        self.flipping_cards = {} # card_id -> (start_time, duration, target_state)

    def start_flip(self, card, target_state, duration=300):
        self.flipping_cards[id(card)] = (pygame.time.get_ticks(), duration, target_state)

    def get_scale_and_image(self, card, front_img, back_img):
        # Returns (scale_x, image)
        card_id = id(card)
        if card_id in self.flipping_cards:
            start_time, duration, target_state = self.flipping_cards[card_id]
            now = pygame.time.get_ticks()
            elapsed = now - start_time
            progress = elapsed / duration
            
            if progress >= 1.0:
                del self.flipping_cards[card_id]
                return 1.0, (front_img if card.is_face_up or card.is_matched else back_img)
            
            # If target_state is True (turning face up)
            # progress 0 to 0.5: show back, scale 1 -> 0
            # progress 0.5 to 1: show front, scale 0 -> 1
            if target_state:
                if progress < 0.5:
                    return 1.0 - (progress * 2), back_img
                else:
                    return (progress - 0.5) * 2, front_img
            else:
                # target_state is False (turning face down)
                if progress < 0.5:
                    return 1.0 - (progress * 2), front_img
                else:
                    return (progress - 0.5) * 2, back_img
        else:
            return 1.0, (front_img if card.is_face_up or card.is_matched else back_img)
