import pygame
import sys
import random
import time
from ui import Button
from models.board import Board
from models.game_mode import SoloMode, PVPMode, PVAIMode
from models.game_state import GameState, State
from models.player import HumanPlayer, AIPlayer
from animations import AnimationManager, FlipAnimator


def draw_text(surface, text, font, color, x, y):
    """Helper function to draw static text and return its rect"""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)
    return text_rect

def draw_centered_text(surface, text, font, color, y):
    """Helper function to draw static text perfectly centered horizontally"""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(surface.get_width()//2, y))
    surface.blit(text_obj, text_rect)
    return text_rect

def create_rounded_surface(surface, radius=10):
    """Returns a copy of the surface with perfectly soft, anti-aliased rounded corners."""
    w, h = surface.get_size()
    mask = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius * 2)
    mask = pygame.transform.smoothscale(mask, (w, h))
    
    new_surface = surface.copy().convert_alpha()
    new_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return new_surface

def main():
    pygame.init()
    pygame.mixer.init() 
    WIDTH, HEIGHT = 800, 600
    FPS = 60
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Wrong Side Up")
    clock = pygame.time.Clock()
    
    title_font_path = "game-assets/fonts/Londrina_Sketch/LondrinaSketch-Regular.ttf"
    font_path = "game-assets/fonts/LondrinaSolid-Black.ttf"
    
    title_size = int(HEIGHT * 0.15)
    menu_size = int(HEIGHT * 0.08)
    card_size = int(HEIGHT * 0.06)
    info_size = int(HEIGHT * 0.05)
    
    try:
        title_font = pygame.font.Font(title_font_path, title_size)
        menu_font = pygame.font.Font(font_path, menu_size)
        card_font = pygame.font.Font(font_path, card_size)
        info_font = pygame.font.Font(font_path, info_size)
    except Exception:
        title_font = pygame.font.Font(None, title_size)
        menu_font = pygame.font.Font(None, menu_size)
        card_font = pygame.font.Font(None, card_size)
        info_font = pygame.font.Font(None, info_size)
        
    state = "MAIN_MENU"
    selected_mode = None
    selected_difficulty = None
    
    WHITE = (255, 255, 255)
    GRAY = (180, 180, 180)
    BLACK = (0, 0, 0)
    BG_BASE_COLOR = (20, 60, 20)
    CARD_BACK = (40, 80, 150)
    CARD_FRONT = (200, 200, 200)
    CARD_MATCHED = (100, 255, 100)
    
    bulb_x, bulb_y = int(WIDTH * 0.7), int(HEIGHT * 0.4)
    base_glow_radius = int(HEIGHT * 0.2)

    btn_x = int(WIDTH * 0.08)
    btn_start_y = int(HEIGHT * 0.4)
    btn_gap = int(HEIGHT * 0.12)

    main_menu_buttons = [
        Button(btn_x, btn_start_y, "Play", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap, "How to play", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap*2, "Quit", menu_font, GRAY, WHITE)
    ]
    
    mode_select_buttons = [
        Button(btn_x, btn_start_y, "Solo", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap, "1v1", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap*2, "Computer", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap*3, "Back", menu_font, GRAY, WHITE)
    ]

    difficulty_select_buttons = [
        Button(btn_x, btn_start_y, "Easy", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap, "Moderate", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap*2, "Hard", menu_font, GRAY, WHITE),
        Button(btn_x, btn_start_y + btn_gap*3, "Back", menu_font, GRAY, WHITE)
    ]
    
    
    # Load Background Assets
    bgs = []
    try:
        bgs = [
            pygame.transform.scale(pygame.image.load("game-assets/background/bg 1.png").convert(), (WIDTH, HEIGHT)),
            pygame.transform.scale(pygame.image.load("game-assets/background/bg 2.png").convert(), (WIDTH, HEIGHT)),
            pygame.transform.scale(pygame.image.load("game-assets/background/bg 3.png").convert(), (WIDTH, HEIGHT)),
        ]
    except Exception as e:
        print(f"Background images not found, using fallback: {e}")
        bgs = []

    # Load Card Assets
    try:
        card_back_orig = pygame.image.load("game-assets/sprite/cards/Back.png").convert_alpha()
    except Exception as e:
        print(f"Failed to load card assets: {e}")
        pygame.quit()
        sys.exit()

    card_front_orig = {}
    for s in range(1, 33):
        # Map symbol s (1-32) to one of the 16 available front assets (2.png to 17.png) using modulo
        file_num = 2 + ((s - 1) % 16)
        filename = f"game-assets/sprite/cards/{file_num}.png"
        try:
            card_front_orig[s] = pygame.image.load(filename).convert_alpha()
        except Exception as e:
            print(f"Failed to load card front asset {filename}: {e}")
            pygame.quit()
            sys.exit()
    
    # Game variables
    board = None
    game_state = None
    game_mode = None
    card_width, card_height = 0, 0
    margin = 10
    start_x, start_y = 0, 0
    check_time = 0
    CHECK_DELAY = 1000 # 1 second delay when checking two cards
    ai_last_move_time = 0
    anim_manager = AnimationManager()
    flip_animator = FlipAnimator()
    
    # Store matched cards to hide them from board
    hidden_cards = set()

    def init_game(mode, difficulty):
        nonlocal board, game_state, game_mode, card_width, card_height, start_x, start_y, check_time, ai_last_move_time, hidden_cards
        board = Board(difficulty)
        anim_manager.flying_cards.clear()
        flip_animator.flipping_cards.clear()
        hidden_cards.clear()
        
        if mode == "Solo":
            players = [HumanPlayer("Player 1")]
            game_mode = SoloMode(players, difficulty)
        elif mode == "1v1":
            players = [HumanPlayer("Player 1"), HumanPlayer("Player 2")]
            game_mode = PVPMode(players)
        elif mode == "Computer":
            players = [HumanPlayer("Player 1"), AIPlayer("Computer")]
            game_mode = PVAIMode(players, difficulty)
            
        game_state = GameState(board, game_mode)
        game_state.start()
        
        # Calculate board rendering variables
        available_width = WIDTH - 40 # Leave small margins
        available_height = HEIGHT - 180 # Leave top space for player profiles
        
        cols = board.cols
        rows = board.rows
        
        max_card_width = int(((available_width - (cols + 1) * margin) // cols) * 0.9)
        max_card_height = int(((available_height - (rows + 1) * margin) // rows) * 0.9)
        
        # Enforce 2:3 aspect ratio
        card_width = max_card_width
        card_height = int(card_width * 1.5)
        
        if card_height > max_card_height:
            card_height = max_card_height
            card_width = int(card_height / 1.5)
        
        # Center board horizontally, push down vertically
        board_w = cols * card_width + (cols - 1) * margin
        start_x = (WIDTH - board_w) // 2
        start_y = 160
        
        check_time = 0
        ai_last_move_time = pygame.time.get_ticks()
        
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
                    
        # Background Effects for Menu States
        if state in ["MAIN_MENU", "MODE_SELECT", "DIFFICULTY_SELECT"]:
            flicker_val = random.randint(0, 100)
            is_flickering = flicker_val > 90

            if bgs:
                if is_flickering:
                    # Swap to dim/off backgrounds to create a realistic flicker
                    screen.blit(random.choice([bgs[1], bgs[2]]), (0, 0))
                else:
                    # Default lights-on background
                    screen.blit(bgs[0], (0, 0))
            else:
                # Fallback to the original programmatic shapes if assets are missing
                if is_flickering:
                    bg_color = (10, 30, 10)
                    glow_alpha = random.randint(20, 80)
                    glow_radius = base_glow_radius - random.randint(20, 40)
                else:
                    bg_color = BG_BASE_COLOR
                    glow_alpha = random.randint(150, 200)
                    glow_radius = base_glow_radius + random.randint(-5, 5)

                screen.fill(bg_color)
                pygame.draw.line(screen, (10,10,10), (bulb_x, 0), (bulb_x, bulb_y - 20), 4)
                pygame.draw.rect(screen, (30,30,30), (bulb_x - 15, bulb_y - 30, 30, 20))
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (200, 255, 150, glow_alpha), (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (bulb_x - glow_radius, bulb_y - glow_radius))
                bulb_color = (200, 255, 200) if is_flickering else (240, 255, 240)
                pygame.draw.circle(screen, bulb_color, (bulb_x, bulb_y), 25)

        # STATE: MAIN MENU
        if state == "MAIN_MENU":
            draw_text(screen, "Wrong Side Up", title_font, WHITE, btn_x, int(HEIGHT * 0.15))
            for btn in main_menu_buttons:
                btn.update(mouse_pos)
                btn.draw(screen)
                if btn.check_click(mouse_pos, mouse_clicked):
                    if btn.text == "Play":
                        state = "MODE_SELECT"
                    elif btn.text == "How to play":
                        state = "HOW_TO_PLAY"
                    elif btn.text == "Quit":
                        running = False

        # STATE: MODE SELECT
        elif state == "MODE_SELECT":
            draw_text(screen, "Select Mode", title_font, WHITE, btn_x, int(HEIGHT * 0.15))
            for btn in mode_select_buttons:
                btn.update(mouse_pos)
                btn.draw(screen)
                if btn.check_click(mouse_pos, mouse_clicked):
                    if btn.text == "Back":
                        state = "MAIN_MENU"
                    else:
                        selected_mode = btn.text
                        state = "DIFFICULTY_SELECT"

        # STATE: DIFFICULTY SELECT
        elif state == "DIFFICULTY_SELECT":
            draw_text(screen, "Select Difficulty", title_font, WHITE, btn_x, int(HEIGHT * 0.15))
            for btn in difficulty_select_buttons:
                btn.update(mouse_pos)
                btn.draw(screen)
                if btn.check_click(mouse_pos, mouse_clicked):
                    if btn.text == "Back":
                        state = "MODE_SELECT"
                    else:
                        if "Easy" in btn.text:
                            selected_difficulty = "Easy"
                        elif "Moderate" in btn.text:
                            selected_difficulty = "Moderate"
                        elif "Hard" in btn.text:
                            selected_difficulty = "Hard"
                        
                        init_game(selected_mode, selected_difficulty)
                        state = "PLAYING"
                        
        # STATE: PLAYING
        elif state == "PLAYING":
            if bgs and len(bgs) >= 3:
                screen.blit(bgs[2], (0, 0))
            else:
                screen.fill((30, 30, 30))
            
            # Auto-resolve CHECKING state after delay
            if game_state.state == State.CHECKING:
                if pygame.time.get_ticks() - check_time > CHECK_DELAY:
                    p1 = game_state.first_pos
                    p2 = game_state.second_pos
                    c1 = board.get_card(*p1) if p1 else None
                    c2 = board.get_card(*p2) if p2 else None
                    
                    res = game_state.resolve()
                    
                    if res == "match" and p1 and p2 and c1 and c2:
                        hidden_cards.add(id(c1))
                        hidden_cards.add(id(c2))
                        
                        # Determine target corner based on current player
                        current = game_mode.current_player
                        
                        thumb_w, thumb_h = 24, 36
                        overlap_x = 12
                        
                        is_p1 = (current == game_mode.players[0])
                        
                        if isinstance(game_mode, SoloMode):
                            base_x, base_y = 50, 95
                        else:
                            base_x = 50 if is_p1 else WIDTH - 200
                            base_y = 85
                            
                        # Calculate exact target position in the deck stack
                        # The player's score was already incremented by GameState, 
                        # so captured_symbols already has them. 
                        # The two cards just added are at len-2 and len-1.
                        idx1 = len(current.captured_symbols) - 2
                        idx2 = len(current.captured_symbols) - 1
                        
                        target_x1 = base_x + idx1 * overlap_x
                        target_x2 = base_x + idx2 * overlap_x
                        
                        cx1 = start_x + p1[1] * (card_width + margin)
                        cy1 = start_y + p1[0] * (card_height + margin)
                        cx2 = start_x + p2[1] * (card_width + margin)
                        cy2 = start_y + p2[0] * (card_height + margin)
                        
                        anim_manager.add_flying_card(card_front_orig[c1.symbol], cx1, cy1, target_x1, base_y, thumb_w, thumb_h, owner=current)
                        anim_manager.add_flying_card(card_front_orig[c2.symbol], cx2, cy2, target_x2, base_y, thumb_w, thumb_h, owner=current)
                    
                    elif res == "miss" and c1 and c2:
                        flip_animator.start_flip(c1, False)
                        flip_animator.start_flip(c2, False)
            else:
                game_state.update()

            if game_state.state != State.GAME_OVER:
                current_player = game_mode.current_player
                
                if isinstance(current_player, AIPlayer):
                    # AI logic
                    if game_state.state in [State.FIRST_FLIP, State.SECOND_FLIP]:
                        if pygame.time.get_ticks() - ai_last_move_time > 1000:
                            flipped_indices = []
                            if game_state.first_pos:
                                flipped_indices.append(game_state.first_pos[0] * board.cols + game_state.first_pos[1])
                            
                            pos = current_player.choose_card(board, flipped_indices)
                            if pos:
                                row, col = pos
                                card = board.get_card(row, col)
                                res = game_state.handle_flip(card, row, col)
                                if res in ["flipped_first", "flipped_second"]:
                                    flip_animator.start_flip(card, True)
                                    for p in game_mode.players:
                                        if hasattr(p, 'remember'):
                                            p.remember(row, col, card.symbol)
                                            
                                if game_state.state == State.CHECKING:
                                    check_time = pygame.time.get_ticks()
                                ai_last_move_time = pygame.time.get_ticks()
                else:
                    # Human logic
                    if mouse_clicked and game_state.state in [State.FIRST_FLIP, State.SECOND_FLIP]:
                        mx, my = mouse_pos
                        for row in range(board.rows):
                            for col in range(board.cols):
                                cx = start_x + col * (card_width + margin)
                                cy = start_y + row * (card_height + margin)
                                card_rect = pygame.Rect(cx, cy, card_width, card_height)
                                
                                if card_rect.collidepoint(mx, my):
                                    card = board.get_card(row, col)
                                    res = game_state.handle_flip(card, row, col)
                                    if res in ["flipped_first", "flipped_second"]:
                                        flip_animator.start_flip(card, True)
                                        for p in game_mode.players:
                                            if hasattr(p, 'remember'):
                                                p.remember(row, col, card.symbol)
                                    
                                    if game_state.state == State.CHECKING:
                                        check_time = pygame.time.get_ticks()

            # Draw Board
            for row in range(board.rows):
                for col in range(board.cols):
                    card = board.get_card(row, col)
                    if id(card) in hidden_cards:
                        continue
                        
                    cx = start_x + col * (card_width + margin)
                    cy = start_y + row * (card_height + margin)
                    
                    scale_x, img = flip_animator.get_scale_and_image(card, card_front_orig[card.symbol] if card.is_face_up or card.is_matched else None, card_back_orig)
                    
                    if img:
                        scaled_w = int(card_width * scale_x)
                        if scaled_w > 0:
                            scaled_img = pygame.transform.scale(img, (scaled_w, card_height))
                            
                            # Make the edges softly curved!
                            if scaled_w > 10:
                                scaled_img = create_rounded_surface(scaled_img, radius=min(25, scaled_w//6))
                                
                            # Offset x to keep it centered while flipping
                            offset_x = (card_width - scaled_w) // 2
                            screen.blit(scaled_img, (cx + offset_x, cy))
                            
                            if card.is_matched:
                                overlay = pygame.Surface((scaled_w, card_height), pygame.SRCALPHA)
                                overlay.fill((0, 0, 0, 100))
                                if scaled_w > 10:
                                    overlay = create_rounded_surface(overlay, radius=min(25, scaled_w//6))
                                screen.blit(overlay, (cx + offset_x, cy))
            
            anim_manager.update_and_draw(screen, card_width, card_height)
            
            # Draw UI Panel in Top Corners
            def draw_captured(player, base_x, base_y):
                thumb_w, thumb_h = 24, 36
                overlap_x = 12
                
                # Count how many flying cards this player currently has
                flying_count = sum(1 for c in anim_manager.flying_cards if c.owner == player)
                visible_count = len(player.captured_symbols) - flying_count
                
                for i, symbol in enumerate(player.captured_symbols):
                    if i >= visible_count:
                        break # Don't draw the ones that are still flying!
                        
                    img = card_front_orig[symbol]
                    scaled = pygame.transform.scale(img, (thumb_w, thumb_h))
                    screen.blit(scaled, (base_x + i * overlap_x, base_y))

            if isinstance(game_mode, SoloMode):
                time_left = int(game_mode.time_remaining)
                time_str = f"Time: {time_left//60}:{time_left%60:02d}"
                color = (255, 100, 100) if time_left < 30 else WHITE
                draw_text(screen, time_str, info_font, color, 50, 20)
                draw_text(screen, f"Score: {game_mode.players[0].score}", info_font, WHITE, 50, 60)
                draw_captured(game_mode.players[0], 50, 95)
            else:
                p1 = game_mode.players[0]
                p2 = game_mode.players[1]
                
                # Player 1 (Top Left)
                p1_color = WHITE if game_mode.current_player == p1 else GRAY
                draw_text(screen, f"{p1.name}", info_font, p1_color, 50, 20)
                draw_text(screen, f"Score: {p1.score}", info_font, p1_color, 50, 50)
                draw_captured(p1, 50, 85)
                
                # Player 2 (Top Right)
                p2_color = WHITE if game_mode.current_player == p2 else GRAY
                draw_text(screen, f"{p2.name}", info_font, p2_color, WIDTH - 200, 20)
                draw_text(screen, f"Score: {p2.score}", info_font, p2_color, WIDTH - 200, 50)
                draw_captured(p2, WIDTH - 200, 85)
                
                # Timer centered top
                t_remaining = game_mode.turn_time_remaining
                if t_remaining is not None:
                    t_color = (255, 100, 100) if t_remaining <= 3 else WHITE
                    draw_text(screen, f"{int(t_remaining)}s", info_font, t_color, WIDTH//2 - 20, 20)

            if game_state.state == State.GAME_OVER:
                draw_centered_text(screen, "GAME OVER!", title_font, (255, 200, 50), HEIGHT//2 - 50)
                draw_centered_text(screen, "Press ESC to return", info_font, WHITE, HEIGHT//2 + 50)
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                state = "CONFIRM_QUIT"
                pygame.time.delay(200)

        # STATE: CONFIRM QUIT
        elif state == "CONFIRM_QUIT":
            screen.fill((20, 20, 40))
            draw_centered_text(screen, "Quit to Main Menu?", title_font, WHITE, HEIGHT//2 - 100)
            draw_centered_text(screen, "Press ENTER to Quit", menu_font, (255, 100, 100), HEIGHT//2 + 20)
            draw_centered_text(screen, "Press ESC to Cancel", menu_font, GRAY, HEIGHT//2 + 80)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
                state = "MAIN_MENU"
                pygame.time.delay(200)
            elif keys[pygame.K_ESCAPE]:
                state = "PLAYING"
                pygame.time.delay(200)

        # STATE: HOW TO PLAY
        elif state == "HOW_TO_PLAY":
            screen.fill((20, 20, 40))
            draw_centered_text(screen, "How to Play Instructions", menu_font, WHITE, HEIGHT//2 - 40)
            draw_centered_text(screen, "Press ESC to return to Menu", menu_font, GRAY, HEIGHT//2 + 40)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                state = "MAIN_MENU"

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
