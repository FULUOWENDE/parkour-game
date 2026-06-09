import random
import sys

import pygame

from src.constants import (
    CHAR_LIST,
    FPS,
    HEIGHT,
    LEVEL_LIST,
    NICKNAME_NAMES,
    NICKNAME_PREFIXES,
    SHOP_ITEMS,
    TITLE,
    WIDTH,
    GameState,
)
from src.game import Game
from src.menu import (
    draw_char_select,
    draw_game_over_menu,
    draw_leaderboard,
    draw_level_select,
    draw_main_menu,
    draw_nickname_screen,
    draw_profile,
    draw_shop,
    draw_welcome,
)
from src.sound import SoundManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    sound_manager = SoundManager(enabled=True)
    sound_manager.switch_bgm("menu")
    game = Game(screen, sound_manager=sound_manager)

    state = GameState.WELCOME
    frame = 0

    welcome_buttons = []
    nickname_buttons = []
    nickname_input = game.nickname if game.save_data.get("nickname") else _random_nickname()
    mode_buttons = []
    small_buttons = []
    menu_selected = 0
    leaderboard_tab = 0
    leaderboard_tab_buttons = []
    leaderboard_back_btn = None
    profile_back_btn = None
    selected_char = game.char_idx
    selected_level = 0
    selected_shop = 0
    game_over_selected = 0
    game_over_buttons = []
    transient_message = ""
    transient_timer = 0

    while True:
        dt = clock.tick(FPS) / 1000
        frame += 1
        if transient_timer > 0:
            transient_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.cleanup()
                sound_manager.cleanup()
                pygame.quit()
                sys.exit()

            if state == GameState.WELCOME:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = _state_after_welcome(game)
                    if state == GameState.NICKNAME:
                        pygame.key.start_text_input()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in welcome_buttons:
                        if btn.handle_click(event.pos) == "start":
                            state = _state_after_welcome(game)
                            if state == GameState.NICKNAME:
                                pygame.key.start_text_input()

            elif state == GameState.NICKNAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.WELCOME
                        pygame.key.stop_text_input()
                    elif event.key == pygame.K_RETURN:
                        game.set_nickname(nickname_input)
                        state = GameState.MAIN_MENU
                        pygame.key.stop_text_input()
                    elif event.key == pygame.K_BACKSPACE:
                        nickname_input = nickname_input[:-1]
                elif event.type == pygame.TEXTINPUT:
                    nickname_input = (nickname_input + event.text).strip()[:12]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in nickname_buttons:
                        action = btn.handle_click(event.pos)
                        if action == "random":
                            nickname_input = _random_nickname()
                        elif action == "confirm":
                            game.set_nickname(nickname_input)
                            state = GameState.MAIN_MENU
                            pygame.key.stop_text_input()
                        elif action == "back":
                            state = GameState.WELCOME
                            pygame.key.stop_text_input()

            elif state == GameState.MAIN_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        menu_selected = _move_menu_selection(menu_selected, -1)
                    elif event.key == pygame.K_RIGHT:
                        menu_selected = _move_menu_selection(menu_selected, 1)
                    elif event.key == pygame.K_UP:
                        menu_selected = 0 if menu_selected < 4 else 1
                    elif event.key == pygame.K_DOWN:
                        menu_selected = 2 if menu_selected == 0 else 3 if menu_selected == 1 else menu_selected
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        action = _menu_action(menu_selected)
                        if action == "quit":
                            _quit(game, sound_manager)
                        state, selected_level = _activate_action(action, game, selected_char, selected_level)
                        if state == GameState.GAME_RUN:
                            sound_manager.switch_bgm("early")
                    elif event.key == pygame.K_ESCAPE:
                        _quit(game, sound_manager)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for idx, btn in enumerate(mode_buttons + small_buttons):
                        action = btn.handle_click(event.pos)
                        if action:
                            if action == "quit":
                                _quit(game, sound_manager)
                            menu_selected = idx
                            state, selected_level = _activate_action(action, game, selected_char, selected_level)
                            if state == GameState.GAME_RUN:
                                sound_manager.switch_bgm("early")

            elif state == GameState.SELECT_CHAR:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.MAIN_MENU
                    elif event.key == pygame.K_LEFT:
                        selected_char = (selected_char - 1) % len(CHAR_LIST)
                    elif event.key == pygame.K_RIGHT:
                        selected_char = (selected_char + 1) % len(CHAR_LIST)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game.char_idx = selected_char
                        game.save()
                        state = GameState.MAIN_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if char_confirm_btn.handle_click(event.pos) == "confirm":
                        game.char_idx = selected_char
                        game.save()
                        state = GameState.MAIN_MENU
                    elif char_back_btn.handle_click(event.pos) == "back":
                        state = GameState.MAIN_MENU
                    else:
                        for i, rect in enumerate(char_cards):
                            if rect.collidepoint(event.pos):
                                selected_char = i

            elif state == GameState.SELECT_LEVEL:
                unlocked = int(game.save_data.get("unlocked_level", 1))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.MAIN_MENU
                    elif event.key == pygame.K_LEFT:
                        selected_level = (selected_level - 1) % len(LEVEL_LIST)
                    elif event.key == pygame.K_RIGHT:
                        selected_level = (selected_level + 1) % len(LEVEL_LIST)
                    elif event.key == pygame.K_UP:
                        selected_level = (selected_level - 5) % len(LEVEL_LIST)
                    elif event.key == pygame.K_DOWN:
                        selected_level = (selected_level + 5) % len(LEVEL_LIST)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and selected_level + 1 <= unlocked:
                        game.start_game(selected_char, "timed", selected_level)
                        state = GameState.GAME_RUN
                        sound_manager.switch_bgm("early")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if level_start_btn.handle_click(event.pos) == "confirm":
                        game.start_game(selected_char, "timed", selected_level)
                        state = GameState.GAME_RUN
                        sound_manager.switch_bgm("early")
                    elif level_back_btn.handle_click(event.pos) == "back":
                        state = GameState.MAIN_MENU
                    else:
                        for i, (rect, is_unlocked) in enumerate(level_cards):
                            if is_unlocked and rect.collidepoint(event.pos):
                                selected_level = i

            elif state == GameState.SHOP:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.MAIN_MENU
                    elif event.key == pygame.K_LEFT:
                        selected_shop = (selected_shop - 1) % len(SHOP_ITEMS)
                    elif event.key == pygame.K_RIGHT:
                        selected_shop = (selected_shop + 1) % len(SHOP_ITEMS)
                    elif event.key == pygame.K_UP:
                        selected_shop = (selected_shop - 3) % len(SHOP_ITEMS)
                    elif event.key == pygame.K_DOWN:
                        selected_shop = (selected_shop + 3) % len(SHOP_ITEMS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        _, transient_message = game.buy_item(selected_shop)
                        transient_timer = 90
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if shop_buy_btn.handle_click(event.pos) == "buy":
                        _, transient_message = game.buy_item(selected_shop)
                        transient_timer = 90
                    elif shop_back_btn.handle_click(event.pos) == "back":
                        state = GameState.MAIN_MENU
                    else:
                        for i, rect in enumerate(shop_cards):
                            if rect.collidepoint(event.pos):
                                selected_shop = i

            elif state == GameState.LEADERBOARD:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.MAIN_MENU
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
                        leaderboard_tab = 1 - leaderboard_tab
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if leaderboard_back_btn and leaderboard_back_btn.handle_click(event.pos) == "back":
                        state = GameState.MAIN_MENU
                    else:
                        for btn in leaderboard_tab_buttons:
                            action = btn.handle_click(event.pos)
                            if action == "distance":
                                leaderboard_tab = 0
                            elif action == "wealth":
                                leaderboard_tab = 1

            elif state == GameState.PROFILE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = GameState.MAIN_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if profile_back_btn and profile_back_btn.handle_click(event.pos) == "back":
                        state = GameState.MAIN_MENU

            elif state == GameState.GAME_RUN:
                if not game.handle_event(event):
                    _quit(game, sound_manager)

            elif state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        game_over_selected = 1 - game_over_selected
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if game_over_selected == 0:
                            game.replay_last()
                            state = GameState.GAME_RUN
                            sound_manager.switch_bgm("early")
                        else:
                            state = GameState.MAIN_MENU
                            sound_manager.switch_bgm("menu")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in game_over_buttons:
                        action = btn.handle_click(event.pos)
                        if action == "replay":
                            game.replay_last()
                            state = GameState.GAME_RUN
                            sound_manager.switch_bgm("early")
                        elif action == "menu":
                            state = GameState.MAIN_MENU
                            sound_manager.switch_bgm("menu")

        if state == GameState.WELCOME:
            draw_welcome(screen, welcome_buttons, frame)

        elif state == GameState.NICKNAME:
            draw_nickname_screen(screen, nickname_buttons, nickname_input, frame)

        elif state == GameState.MAIN_MENU:
            draw_main_menu(screen, mode_buttons, small_buttons, menu_selected, frame, game.save_data)

        elif state == GameState.SELECT_CHAR:
            char_confirm_btn, char_back_btn, char_cards = draw_char_select(screen, selected_char, frame)

        elif state == GameState.SELECT_LEVEL:
            level_start_btn, level_back_btn, level_cards = draw_level_select(
                screen,
                selected_level,
                int(game.save_data.get("unlocked_level", 1)),
                frame,
            )

        elif state == GameState.SHOP:
            shop_buy_btn, shop_back_btn, shop_cards = draw_shop(screen, selected_shop, game.save_data, frame)
            if transient_timer > 0:
                _draw_toast(screen, transient_message)

        elif state == GameState.LEADERBOARD:
            leaderboard_tab_buttons, leaderboard_back_btn = draw_leaderboard(screen, leaderboard_tab, game, frame)

        elif state == GameState.PROFILE:
            profile_back_btn = draw_profile(screen, game, frame)

        elif state == GameState.GAME_RUN:
            game.update()
            game.draw_scene()
            if game.is_game_over:
                state = GameState.GAME_OVER
                game_over_selected = 0
            else:
                game.draw_overlay()

        elif state == GameState.GAME_OVER:
            game.draw_scene()
            game_over_buttons = draw_game_over_menu(screen, game.result, game_over_selected, frame)

        pygame.display.flip()


def _activate_menu(index, game, selected_char, selected_level):
    action = _menu_action(index)
    return _activate_action(action, game, selected_char, selected_level)


def _menu_action(index):
    return ["endless", "timed", "shop", "characters", "leaderboard", "profile", "quit"][index]


def _move_menu_selection(current, delta):
    if current < 2:
        return (current + delta) % 2
    return 2 + ((current - 2 + delta) % 5)


def _activate_action(action, game, selected_char, selected_level):
    if action == "endless":
        game.start_game(selected_char, "endless")
        return GameState.GAME_RUN, selected_level
    if action == "timed":
        selected_level = min(selected_level, int(game.save_data.get("unlocked_level", 1)) - 1)
        return GameState.SELECT_LEVEL, selected_level
    if action == "shop":
        return GameState.SHOP, selected_level
    if action == "characters":
        return GameState.SELECT_CHAR, selected_level
    if action == "leaderboard":
        return GameState.LEADERBOARD, selected_level
    if action == "profile":
        return GameState.PROFILE, selected_level
    if action == "quit":
        return GameState.MAIN_MENU, selected_level
    return GameState.MAIN_MENU, selected_level


def _draw_toast(screen, text):
    font = pygame.font.Font(None, 1)
    try:
        from src.menu import _get_font

        font = _get_font(19, bold=True)
    except Exception:
        pass
    label = font.render(text, True, (80, 50, 33))
    rect = pygame.Rect(0, 0, label.get_width() + 44, 42)
    rect.center = (WIDTH // 2, HEIGHT - 28)
    pygame.draw.rect(screen, (80, 50, 33), rect, border_radius=15)
    pygame.draw.rect(screen, (255, 247, 222), rect.inflate(-6, -6), border_radius=12)
    screen.blit(label, label.get_rect(center=rect.center))


def _random_nickname():
    return random.choice(NICKNAME_PREFIXES) + random.choice(NICKNAME_NAMES)


def _state_after_welcome(game):
    return GameState.MAIN_MENU if game.save_data.get("nickname") else GameState.NICKNAME


def _quit(game, sound_manager):
    game.cleanup()
    sound_manager.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pygame.quit()
        sys.exit()
