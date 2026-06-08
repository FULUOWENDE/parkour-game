"""赶早八 Campus Rush — Main entry point with state machine."""
import sys

import pygame

from src.constants import (
    CHAR_LIST,
    FPS,
    HEIGHT,
    MENU_BG,
    MODE_LIST,
    TITLE,
    WIDTH,
    GameState,
)
from src.game import Game
from src.menu import (
    draw_char_select,
    draw_game_over_menu,
    draw_main_menu,
    draw_mode_select,
)
from src.sound import SoundManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # ── Sound system ──
    sound_manager = SoundManager(enabled=True)
    sound_manager.switch_bgm("menu")

    game = Game(screen, sound_manager=sound_manager)
    game_state = GameState.MAIN_MENU

    # ── Menu state variables ──
    selected_char_idx = 0
    selected_mode_idx = 0
    menu_buttons = []          # main menu buttons (rebuilt each frame)
    menu_selected_idx = 0      # keyboard nav index for main menu
    help_visible = False
    go_selected_btn = 0        # keyboard nav index for game-over buttons
    frame = 0                  # global frame counter for animations

    while True:
        dt = clock.tick(FPS) / 1000
        frame += 1

        # ═══════════════════════════════════════════════════════════
        #  EVENT HANDLING
        # ═══════════════════════════════════════════════════════════
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.cleanup()
                sound_manager.cleanup()
                pygame.quit()
                sys.exit()

            # ── MAIN MENU events ──
            if game_state == GameState.MAIN_MENU:
                if event.type == pygame.KEYDOWN:
                    if help_visible:
                        # Any key closes help popup
                        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                            help_visible = False
                        else:
                            help_visible = False
                    else:
                        if event.key == pygame.K_UP:
                            menu_selected_idx = (menu_selected_idx - 1) % 3
                        elif event.key == pygame.K_DOWN:
                            menu_selected_idx = (menu_selected_idx + 1) % 3
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if menu_selected_idx == 0:
                                game_state = GameState.SELECT_CHAR
                            elif menu_selected_idx == 1:
                                help_visible = True
                            elif menu_selected_idx == 2:
                                game.cleanup()
                                sound_manager.cleanup()
                                pygame.quit()
                                sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if help_visible:
                        help_visible = False
                    else:
                        for btn in menu_buttons:
                            action = btn.handle_click(event.pos)
                            if action == "start":
                                game_state = GameState.SELECT_CHAR
                            elif action == "help":
                                help_visible = True
                            elif action == "quit":
                                game.cleanup()
                                sound_manager.cleanup()
                                pygame.quit()
                                sys.exit()

            # ── SELECT CHAR events ──
            elif game_state == GameState.SELECT_CHAR:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.MAIN_MENU
                        sound_manager.switch_bgm("menu")
                    elif event.key == pygame.K_LEFT:
                        selected_char_idx = (selected_char_idx - 1) % len(CHAR_LIST)
                    elif event.key == pygame.K_RIGHT:
                        selected_char_idx = (selected_char_idx + 1) % len(CHAR_LIST)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state = GameState.SELECT_MODE

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check confirm/back buttons
                    if char_confirm_btn and char_confirm_btn.handle_click(event.pos) == "confirm":
                        game_state = GameState.SELECT_MODE
                    elif char_back_btn and char_back_btn.handle_click(event.pos) == "back":
                        game_state = GameState.MAIN_MENU
                        sound_manager.switch_bgm("menu")
                    # Check click on character cards (approximate)
                    if event.pos[1] < 100 or event.pos[1] > 480:
                        pass  # outside card area
                    else:
                        card_w = 160
                        card_spacing = 24
                        total_chars = len(CHAR_LIST)
                        total_w = total_chars * card_w + (total_chars - 1) * card_spacing
                        start_x = WIDTH // 2 - total_w // 2
                        for i in range(total_chars):
                            cx = start_x + i * (card_w + card_spacing)
                            if cx <= event.pos[0] <= cx + card_w:
                                selected_char_idx = i
                                break

            # ── SELECT MODE events ──
            elif game_state == GameState.SELECT_MODE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.SELECT_CHAR
                    elif event.key == pygame.K_LEFT:
                        selected_mode_idx = (selected_mode_idx - 1) % len(MODE_LIST)
                    elif event.key == pygame.K_RIGHT:
                        selected_mode_idx = (selected_mode_idx + 1) % len(MODE_LIST)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game.start_game(char_idx=selected_char_idx, mode=selected_mode_idx)
                        game_state = GameState.GAME_RUN
                        sound_manager.switch_bgm("early")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if mode_start_btn and mode_start_btn.handle_click(event.pos) == "confirm":
                        game.start_game(char_idx=selected_char_idx, mode=selected_mode_idx)
                        game_state = GameState.GAME_RUN
                        sound_manager.switch_bgm("early")
                    elif mode_back_btn and mode_back_btn.handle_click(event.pos) == "back":
                        game_state = GameState.SELECT_CHAR
                    # Check click on mode cards
                    if event.pos[1] < 100 or event.pos[1] > 480:
                        pass
                    else:
                        card_w = 220
                        card_spacing = 30
                        total_modes = len(MODE_LIST)
                        total_w = total_modes * card_w + (total_modes - 1) * card_spacing
                        start_x = WIDTH // 2 - total_w // 2
                        for i in range(total_modes):
                            cx = start_x + i * (card_w + card_spacing)
                            if cx <= event.pos[0] <= cx + card_w:
                                selected_mode_idx = i
                                break

            # ── GAME RUN events ──
            elif game_state == GameState.GAME_RUN:
                if not game.handle_event(event):
                    game.cleanup()
                    sound_manager.cleanup()
                    pygame.quit()
                    sys.exit()

            # ── GAME OVER events ──
            elif game_state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        go_selected_btn = (go_selected_btn - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        go_selected_btn = (go_selected_btn + 1) % 3
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if go_selected_btn == 0:
                            # 再来一局 — same char & mode, immediate start
                            game.start_game(char_idx=selected_char_idx, mode=selected_mode_idx, immediate=True)
                            game_state = GameState.GAME_RUN
                            sound_manager.switch_bgm("early")
                        elif go_selected_btn == 1:
                            # 重新选模式
                            game_state = GameState.SELECT_MODE
                        elif go_selected_btn == 2:
                            # 返回主菜单
                            game_state = GameState.MAIN_MENU
                            menu_selected_idx = 0
                            sound_manager.switch_bgm("menu")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, btn in enumerate(game_over_buttons):
                        action = btn.handle_click(event.pos)
                        if action == "replay":
                            game.start_game(char_idx=selected_char_idx, mode=selected_mode_idx, immediate=True)
                            game_state = GameState.GAME_RUN
                            sound_manager.switch_bgm("early")
                        elif action == "reselect":
                            game_state = GameState.SELECT_MODE
                        elif action == "menu":
                            game_state = GameState.MAIN_MENU
                            menu_selected_idx = 0
                            sound_manager.switch_bgm("menu")

        # ═══════════════════════════════════════════════════════════
        #  RENDERING
        # ═══════════════════════════════════════════════════════════
        screen.fill(MENU_BG)

        if game_state == GameState.MAIN_MENU:
            draw_main_menu(screen, menu_buttons, menu_selected_idx, help_visible, frame, game.ui.high_score)

        elif game_state == GameState.SELECT_CHAR:
            char_confirm_btn, char_back_btn = draw_char_select(screen, selected_char_idx, frame)

        elif game_state == GameState.SELECT_MODE:
            mode_start_btn, mode_back_btn = draw_mode_select(screen, selected_mode_idx, frame)

        elif game_state == GameState.GAME_RUN:
            game.update()
            game.draw_scene()
            # Transition check before drawing overlay to avoid flicker
            if game.is_game_over:
                game_state = GameState.GAME_OVER
                go_selected_btn = 0
            else:
                game.draw_overlay()

        elif game_state == GameState.GAME_OVER:
            # Draw frozen game scene behind the menu
            game.draw_scene()
            game_over_buttons = draw_game_over_menu(
                screen,
                game.score,
                game.ui.high_score,
                selected_char_idx,
                selected_mode_idx,
                go_selected_btn,
                game.is_new_record,
                frame,
            )

        pygame.display.flip()


if __name__ == "__main__":
    main()
