import pygame

class Button:
    def __init__(self, x, y, text, font, base_color, hover_color):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.rect = pygame.Rect(x, y, 0, 0)
        self._update_rect()
        self.is_hovered = False

    def _update_rect(self):
        text_surf = self.font.render(self.text, True, self.base_color)
        self.rect.width = text_surf.get_width()
        self.rect.height = text_surf.get_height()

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.base_color
        # Shift slightly right on hover for effect
        x_pos = self.x + 20 if self.is_hovered else self.x
        
        text_surf = self.font.render(self.text, True, color)
        
        # We don't change self.rect.x here so hover logic remains stable,
        # we just draw it shifted.
        surface.blit(text_surf, (x_pos, self.y))

    def check_click(self, mouse_pos, mouse_clicked):
        if self.is_hovered and mouse_clicked:
            return True
        return False
