import math
import os

import pygame

from src.constants import (
    CHAR_LIST,
    HEIGHT,
    LEVEL_LIST,
    MENU_BTN_DISABLED,
    MENU_BTN_HOVER,
    MENU_BTN_NORMAL,
    MENU_BTN_TEXT,
    MODE_LIST,
    SHOP_ITEMS,
    WIDTH,
)

RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resources")
ITEM_DIR = os.path.join(RESOURCE_DIR, "items")
MODE_DIR = os.path.join(RESOURCE_DIR, "modes")
UI_DIR = os.path.join(RESOURCE_DIR, "ui")
FONT_REGULAR = os.path.join(RESOURCE_DIR, "fonts", "NotoSansSC-Regular.ttf")
FONT_BOLD = os.path.join(RESOURCE_DIR, "fonts", "NotoSansSC-Bold.ttf")

_FONT_CACHE = {}
_IMAGE_CACHE = {}


def _get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        path = FONT_BOLD if bold else FONT_REGULAR
        try:
            _FONT_CACHE[key] = pygame.font.Font(path, size)
        except Exception:
            _FONT_CACHE[key] = pygame.font.Font(None, size)
    return _FONT_CACHE[key]


def _load_image(path, size=None, alpha=True):
    key = (path, size, alpha)
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        if size:
            img = pygame.transform.smoothscale(img, size)
    except Exception:
        img = None
    _IMAGE_CACHE[key] = img
    return img


def _draw_text(surface, text, font, color, center=None, topleft=None, shadow=True):
    if shadow:
        shade = font.render(text, True, (255, 255, 255))
        shade.set_alpha(145)
        rect = shade.get_rect()
        if center:
            rect.center = (center[0] + 2, center[1] + 3)
        else:
            rect.topleft = (topleft[0] + 2, topleft[1] + 3)
        surface.blit(shade, rect)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = center
    else:
        rect.topleft = topleft
    surface.blit(rendered, rect)
    return rect


def _panel(surface, rect, fill=(255, 247, 222), radius=20):
    pygame.draw.rect(surface, (80, 50, 33), rect, border_radius=radius)
    inner = pygame.Rect(rect).inflate(-8, -8)
    pygame.draw.rect(surface, fill, inner, border_radius=max(4, radius - 5))
    return inner


def _draw_dopamine_background(surface, frame):
    top = (255, 239, 137)
    mid = (255, 190, 122)
    bottom = (137, 225, 191)
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        if t < 0.58:
            local = t / 0.58
            color = tuple(int(top[i] + (mid[i] - top[i]) * local) for i in range(3))
        else:
            local = (t - 0.58) / 0.42
            color = tuple(int(mid[i] + (bottom[i] - mid[i]) * local) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

    for i, (x, y, r, color) in enumerate([
        (90, 88, 58, (83, 197, 255)),
        (780, 86, 76, (255, 112, 150)),
        (850, 382, 46, (128, 229, 111)),
        (112, 420, 52, (255, 111, 86)),
        (500, 76, 34, (255, 219, 65)),
        (360, 430, 42, (115, 207, 255)),
    ]):
        bob = math.sin(frame * 0.025 + i) * 8
        pygame.draw.circle(surface, color, (int(x), int(y + bob)), r)
        pygame.draw.circle(surface, (80, 50, 33), (int(x), int(y + bob)), r, width=3)
        pygame.draw.circle(surface, (255, 255, 255), (int(x - r * 0.25), int(y + bob - r * 0.28)), max(4, r // 8))


class Button:
    def __init__(self, rect, text, action, font_size=22, color=None, text_color=None, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = _get_font(font_size, bold=True)
        self.color = color
        self.text_color = text_color
        self.enabled = enabled
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos):
        if self.enabled and self.rect.collidepoint(mouse_pos):
            return self.action
        return None

    def draw(self, surface, selected=False):
        if not self.enabled:
            fill = MENU_BTN_DISABLED
            text = (120, 120, 120)
        elif self.hovered or selected:
            fill = MENU_BTN_HOVER if self.color is None else tuple(min(255, c + 24) for c in self.color)
            text = (68, 44, 31)
        else:
            fill = self.color or MENU_BTN_NORMAL
            text = self.text_color or MENU_BTN_TEXT
        offset = 1 if self.hovered or selected else 0
        pygame.draw.rect(surface, (118, 77, 47), self.rect.move(0, 6 - offset), border_radius=14)
        pygame.draw.rect(surface, (76, 48, 33), self.rect.move(0, offset), border_radius=14)
        inner = self.rect.inflate(-6, -6).move(0, offset)
        pygame.draw.rect(surface, fill, inner, border_radius=11)
        label = self.font.render(self.text, True, text)
        surface.blit(label, label.get_rect(center=inner.center))


def draw_welcome(screen, buttons, frame):
    _draw_dopamine_background(screen, frame)
    card = pygame.Rect(WIDTH // 2 - 310, 72, 620, 375)
    _panel(screen, card, radius=28)
    pygame.draw.rect(screen, (255, 111, 86), (card.x + 22, card.y + 22, 66, 22), border_radius=12)
    pygame.draw.rect(screen, (83, 197, 255), (card.right - 90, card.y + 26, 54, 18), border_radius=9)
    pygame.draw.circle(screen, (255, 219, 65), (card.x + 95, card.bottom - 55), 19)
    pygame.draw.circle(screen, (128, 229, 111), (card.right - 98, card.bottom - 66), 24)
    title_y = card.y + 120 + math.sin(frame * 0.035) * 4
    _draw_text(screen, "早八跑酷", _get_font(74, bold=True), (255, 96, 121), center=(WIDTH // 2, title_y))
    _draw_text(screen, "你也讨厌早八吗", _get_font(31, bold=True), (65, 126, 217), center=(WIDTH // 2, card.y + 210), shadow=False)
    buttons.clear()
    buttons.append(Button((WIDTH // 2 - 118, card.y + 266, 236, 58), "开始游戏", "start", 26, color=(255, 181, 76), text_color=(70, 45, 30)))
    buttons[0].update(pygame.mouse.get_pos())
    buttons[0].draw(screen, selected=math.sin(frame * 0.08) > 0.88)
    _draw_text(screen, "Space / Enter 也可以开始", _get_font(15), (100, 90, 74), center=(WIDTH // 2, card.bottom - 31), shadow=False)


def draw_nickname_screen(screen, buttons, nickname, frame):
    _draw_dopamine_background(screen, frame)
    panel = pygame.Rect(WIDTH // 2 - 300, 105, 600, 330)
    _panel(screen, panel, radius=24)
    _draw_text(screen, "起一个早八昵称", _get_font(42, bold=True), (255, 96, 121), center=(WIDTH // 2, panel.y + 58))
    _draw_text(screen, "用于个人主页和排行榜", _get_font(18, bold=True), (80, 50, 33), center=(WIDTH // 2, panel.y + 100), shadow=False)

    input_rect = pygame.Rect(panel.x + 92, panel.y + 142, panel.w - 184, 58)
    pygame.draw.rect(screen, (255, 235, 193), input_rect, border_radius=14)
    pygame.draw.rect(screen, (80, 50, 33), input_rect, width=3, border_radius=14)
    shown = nickname if nickname else "输入或随机生成昵称"
    color = (80, 50, 33) if nickname else (130, 118, 100)
    _draw_text(screen, shown, _get_font(24, bold=True), color, center=input_rect.center, shadow=False)

    mouse = pygame.mouse.get_pos()
    specs = [
        ((panel.x + 82, panel.y + 230, 140, 48), "随机换一个", "random", (83, 197, 255)),
        ((panel.x + 230, panel.y + 230, 140, 48), "确认进入", "confirm", (255, 181, 76)),
        ((panel.x + 378, panel.y + 230, 140, 48), "返回", "back", (255, 112, 150)),
    ]
    buttons.clear()
    for rect, text, action, color in specs:
        btn = Button(rect, text, action, 19, color=color, text_color=(70, 45, 30))
        btn.update(mouse)
        btn.draw(screen)
        buttons.append(btn)


def draw_main_menu(screen, mode_buttons, small_buttons, selected_idx, frame, save_data):
    _draw_dopamine_background(screen, frame)
    _draw_text(screen, "早八跑酷", _get_font(42, bold=True), (255, 96, 121), center=(WIDTH // 2, 38))
    nickname = save_data.get("nickname") or "早八同学"
    stat = f"{nickname}   金币 {save_data.get('coins', 0)}   最高 {int(save_data.get('best_distance', 0))}m"
    _draw_text(screen, stat, _get_font(16, bold=True), (80, 50, 33), center=(WIDTH // 2, 78), shadow=False)

    mode_buttons.clear()
    mouse = pygame.mouse.get_pos()
    card_w, card_h = 310, 286
    start_x = WIDTH // 2 - card_w - 28
    y = 112
    for i, mode in enumerate(MODE_LIST):
        rect = pygame.Rect(start_x + i * (card_w + 56), y, card_w, card_h)
        hovered = rect.collidepoint(mouse) or selected_idx == i
        _panel(screen, rect, fill=(255, 247, 222) if hovered else (255, 235, 193), radius=20)
        img = _load_image(os.path.join(MODE_DIR, mode["image"]), (214, 166), alpha=False)
        if img:
            screen.blit(img, img.get_rect(center=(rect.centerx, rect.y + 100)))
        _draw_text(screen, mode["name"], _get_font(30, bold=True), (255, 96, 121) if i == 0 else (65, 126, 217), center=(rect.centerx, rect.y + 210))
        _draw_text(screen, mode["desc"], _get_font(15, bold=True), (88, 74, 60), center=(rect.centerx, rect.y + 247), shadow=False)
        mode_buttons.append(Button(rect, mode["name"], mode["id"], 24))

    small_buttons.clear()
    labels = [
        ("商店", "shop", (128, 229, 111)),
        ("角色", "characters", (255, 112, 150)),
        ("排行榜", "leaderboard", (83, 197, 255)),
        ("个人主页", "profile", (255, 218, 91)),
        ("退出游戏", "quit", (222, 93, 83)),
    ]
    btn_w, btn_h, gap = 134, 46, 16
    left = WIDTH // 2 - (btn_w * len(labels) + gap * (len(labels) - 1)) // 2
    for i, (text, action, color) in enumerate(labels):
        btn = Button((left + i * (btn_w + gap), 436, btn_w, btn_h), text, action, 18, color=color, text_color=(70, 45, 30))
        btn.update(mouse)
        btn.draw(screen, selected=selected_idx == i + 2)
        small_buttons.append(btn)


def draw_char_select(screen, char_idx, frame):
    _draw_dopamine_background(screen, frame)
    _draw_text(screen, "选择你的早八人设", _get_font(40, bold=True), (255, 96, 121), center=(WIDTH // 2, 52))
    cards = []
    for i, char in enumerate(CHAR_LIST):
        rect = pygame.Rect(190 + i * 320, 115, 260, 322)
        selected = i == char_idx
        _panel(screen, rect, fill=(255, 247, 222) if selected else (255, 235, 193), radius=18)
        _draw_preview_character(screen, rect.centerx, rect.y + 132, frame, female=char["id"] == "female")
        _draw_text(screen, char["name"], _get_font(24, bold=True), (80, 50, 33), center=(rect.centerx, rect.y + 232), shadow=False)
        _draw_text(screen, char["desc"], _get_font(14), (94, 82, 68), center=(rect.centerx, rect.y + 270), shadow=False)
        if selected:
            pygame.draw.rect(screen, (255, 96, 121), rect.inflate(-18, -18), width=5, border_radius=12)
        cards.append(rect)
    mouse = pygame.mouse.get_pos()
    confirm = Button((WIDTH // 2 - 208, 468, 190, 48), "确认选择", "confirm", 21, color=(255, 181, 76), text_color=(70, 45, 30))
    back = Button((WIDTH // 2 + 18, 468, 190, 48), "返回菜单", "back", 21, color=(83, 197, 255), text_color=(70, 45, 30))
    for btn in (confirm, back):
        btn.update(mouse)
        btn.draw(screen)
    return confirm, back, cards


def _draw_preview_character(surface, cx, foot_y, frame, female=False):
    phase = frame * 0.16
    skin = (255, 217, 178)
    hair = (61, 42, 34) if not female else (72, 42, 58)
    shirt = (71, 169, 213) if not female else (255, 128, 161)
    pants = (52, 82, 155) if not female else (119, 98, 177)
    shoe = (245, 240, 223) if not female else (67, 126, 210)
    bag = (244, 182, 74) if not female else (127, 207, 138)
    scale = 1.28
    _draw_runner(surface, cx, foot_y, phase, skin, hair, shirt, pants, shoe, bag, scale, female)


def draw_level_select(screen, selected_level_idx, unlocked_level, frame):
    _draw_dopamine_background(screen, frame)
    _draw_text(screen, "限时模式", _get_font(40, bold=True), (255, 96, 121), center=(WIDTH // 2, 48))
    _draw_text(screen, "距离拉长，速度和障碍密度会逐关上升", _get_font(18, bold=True), (80, 50, 33), center=(WIDTH // 2, 86), shadow=False)
    cards = []
    cols = 5
    card_w, card_h = 150, 124
    gap_x, gap_y = 24, 20
    start_x = WIDTH // 2 - (cols * card_w + (cols - 1) * gap_x) // 2
    start_y = 124
    for i, level in enumerate(LEVEL_LIST):
        row, col = divmod(i, cols)
        rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
        unlocked = level["id"] <= unlocked_level
        selected = i == selected_level_idx
        _panel(screen, rect, fill=(246, 255, 217) if unlocked else (214, 207, 190), radius=14)
        if selected and unlocked:
            pygame.draw.rect(screen, (255, 96, 121), rect.inflate(-15, -15), width=4, border_radius=8)
        title = level["name"] if unlocked else "未解锁"
        _draw_text(screen, title, _get_font(22, bold=True), (80, 50, 33), center=(rect.centerx, rect.y + 30), shadow=False)
        _draw_text(screen, f"{level['length']}m / 60秒", _get_font(14), (95, 85, 70), center=(rect.centerx, rect.y + 65), shadow=False)
        _draw_text(screen, f"奖励 {level['reward']} 金币", _get_font(14), (95, 85, 70), center=(rect.centerx, rect.y + 91), shadow=False)
        cards.append((rect, unlocked))
    mouse = pygame.mouse.get_pos()
    start_btn = Button((WIDTH // 2 - 205, 448, 190, 48), "开始挑战", "confirm", 21, color=(255, 181, 76), text_color=(70, 45, 30), enabled=selected_level_idx + 1 <= unlocked_level)
    back_btn = Button((WIDTH // 2 + 15, 448, 190, 48), "返回菜单", "back", 21, color=(83, 197, 255), text_color=(70, 45, 30))
    for btn in (start_btn, back_btn):
        btn.update(mouse)
        btn.draw(screen)
    return start_btn, back_btn, cards


def draw_shop(screen, selected_idx, save_data, frame):
    _draw_dopamine_background(screen, frame)
    _draw_text(screen, "早八商店", _get_font(40, bold=True), (255, 96, 121), center=(WIDTH // 2, 42))
    _draw_text(screen, f"金币余额：{save_data.get('coins', 0)}", _get_font(18, bold=True), (80, 50, 33), center=(WIDTH // 2, 88), shadow=False)
    inventory = save_data.get("inventory", {})
    cards = []
    cols = 3
    card_w, card_h = 262, 146
    start_x, start_y = 67, 126
    for i, item in enumerate(SHOP_ITEMS):
        row, col = divmod(i, cols)
        rect = pygame.Rect(start_x + col * 290, start_y + row * 170, card_w, card_h)
        _panel(screen, rect, fill=(255, 247, 222) if i == selected_idx else (255, 235, 193), radius=16)
        if i == selected_idx:
            pygame.draw.rect(screen, (255, 96, 121), rect.inflate(-16, -16), width=4, border_radius=9)
        img = _load_image(os.path.join(ITEM_DIR, item["image"]), (72, 72))
        icon_rect = pygame.Rect(rect.x + 18, rect.y + 20, 78, 78)
        pygame.draw.rect(screen, (255, 218, 91), icon_rect, border_radius=13)
        pygame.draw.rect(screen, (80, 50, 33), icon_rect, width=3, border_radius=13)
        if img:
            screen.blit(img, img.get_rect(center=icon_rect.center))
        _draw_text(screen, item["name"], _get_font(20, bold=True), (80, 50, 33), topleft=(rect.x + 112, rect.y + 22), shadow=False)
        _draw_text(screen, f"{item['price']} 金币  库存 {inventory.get(item['id'], 0)}", _get_font(14, bold=True), (93, 81, 66), topleft=(rect.x + 112, rect.y + 53), shadow=False)
        for j, line in enumerate(_wrap_text(item["desc"], _get_font(13), 128)[:2]):
            _draw_text(screen, line, _get_font(13), (103, 94, 78), topleft=(rect.x + 112, rect.y + 79 + j * 20), shadow=False)
        cards.append(rect)
    mouse = pygame.mouse.get_pos()
    buy_btn = Button((WIDTH // 2 - 210, 478, 190, 44), "购买道具", "buy", 20, color=(128, 229, 111), text_color=(70, 45, 30))
    back_btn = Button((WIDTH // 2 + 20, 478, 190, 44), "返回菜单", "back", 20, color=(83, 197, 255), text_color=(70, 45, 30))
    for btn in (buy_btn, back_btn):
        btn.update(mouse)
        btn.draw(screen)
    return buy_btn, back_btn, cards


def draw_leaderboard(screen, tab_idx, game, frame):
    _draw_dopamine_background(screen, frame)
    _draw_text(screen, "排行榜", _get_font(42, bold=True), (255, 96, 121), center=(WIDTH // 2, 42))
    mouse = pygame.mouse.get_pos()
    tab_buttons = [
        Button((WIDTH // 2 - 180, 78, 160, 42), "距离排行", "distance", 18, color=(83, 197, 255), text_color=(70, 45, 30)),
        Button((WIDTH // 2 + 20, 78, 160, 42), "财产排行", "wealth", 18, color=(255, 218, 91), text_color=(70, 45, 30)),
    ]
    for i, btn in enumerate(tab_buttons):
        btn.update(mouse)
        btn.draw(screen, selected=i == tab_idx)
    panel = pygame.Rect(190, 142, 580, 310)
    _panel(screen, panel)
    rows = game.distance_rankings() if tab_idx == 0 else game.wealth_rankings()
    headers = ("名次", "昵称", "距离") if tab_idx == 0 else ("名次", "昵称", "金币")
    x_cols = [panel.x + 70, panel.x + 250, panel.x + 455]
    for i, header in enumerate(headers):
        _draw_text(screen, header, _get_font(17, bold=True), (80, 50, 33), center=(x_cols[i], panel.y + 34), shadow=False)
    if not rows:
        _draw_text(screen, "还没有无尽模式记录，先去跑一局吧", _get_font(20, bold=True), (95, 82, 68), center=panel.center, shadow=False)
    for i, row in enumerate(rows[:8]):
        y = panel.y + 72 + i * 28
        value = row.get("distance", row.get("coins", 0))
        if tab_idx == 0:
            value = f"{int(value)}m"
        _draw_text(screen, str(i + 1), _get_font(15, bold=True), (80, 50, 33), center=(x_cols[0], y), shadow=False)
        _draw_text(screen, row.get("name", "早八同学"), _get_font(15, bold=True), (80, 50, 33), center=(x_cols[1], y), shadow=False)
        _draw_text(screen, str(value), _get_font(15, bold=True), (80, 50, 33), center=(x_cols[2], y), shadow=False)
    back = Button((WIDTH // 2 - 95, 466, 190, 46), "返回菜单", "back", 20, color=(83, 197, 255), text_color=(70, 45, 30))
    back.update(mouse)
    back.draw(screen)
    return tab_buttons, back


def draw_profile(screen, game, frame):
    _draw_dopamine_background(screen, frame)
    save = game.save_data
    _draw_text(screen, "个人主页", _get_font(42, bold=True), (255, 96, 121), center=(WIDTH // 2, 44))
    panel = pygame.Rect(150, 92, 660, 356)
    _panel(screen, panel)
    _draw_text(screen, f"昵称：{game.nickname}", _get_font(26, bold=True), (80, 50, 33), topleft=(panel.x + 44, panel.y + 38), shadow=False)
    _draw_text(screen, f"财产：{save.get('coins', 0)} 金币", _get_font(22, bold=True), (80, 50, 33), topleft=(panel.x + 44, panel.y + 86), shadow=False)
    _draw_text(screen, f"个人纪录：{int(save.get('best_distance', 0))}m", _get_font(22, bold=True), (80, 50, 33), topleft=(panel.x + 44, panel.y + 126), shadow=False)
    _draw_text(screen, "当前道具", _get_font(22, bold=True), (255, 96, 121), topleft=(panel.x + 44, panel.y + 182), shadow=False)
    inventory = save.get("inventory", {})
    for i, item in enumerate(SHOP_ITEMS):
        x = panel.x + 44 + (i % 3) * 190
        y = panel.y + 226 + (i // 3) * 54
        img = _load_image(os.path.join(ITEM_DIR, item["image"]), (36, 36))
        if img:
            screen.blit(img, (x, y))
        _draw_text(screen, f"{item['name']} x{inventory.get(item['id'], 0)}", _get_font(15, bold=True), (80, 50, 33), topleft=(x + 44, y + 8), shadow=False)
    mouse = pygame.mouse.get_pos()
    back = Button((WIDTH // 2 - 95, 466, 190, 46), "返回菜单", "back", 20, color=(83, 197, 255), text_color=(70, 45, 30))
    back.update(mouse)
    back.draw(screen)
    return back


def draw_game_over_menu(screen, result, selected_btn, frame):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((30, 24, 28, 158))
    screen.blit(overlay, (0, 0))
    panel = pygame.Rect(218, 34, 524, 474)
    _panel(screen, panel, radius=22)
    success = result.get("success", False)
    title = "成功到达教学楼" if success else "游戏结束"
    _draw_text(screen, title, _get_font(36, bold=True), (91, 176, 80) if success else (222, 76, 70), center=(panel.centerx, panel.y + 42), shadow=False)
    advisor = _load_image(os.path.join(UI_DIR, "advisor.png"), (190, 142))
    if advisor:
        portrait = pygame.Rect(panel.centerx - 104, panel.y + 78, 208, 158)
        pygame.draw.rect(screen, (255, 218, 91), portrait, border_radius=16)
        pygame.draw.rect(screen, (80, 50, 33), portrait, width=3, border_radius=16)
        screen.blit(advisor, advisor.get_rect(center=portrait.center))
    quote_rect = pygame.Rect(panel.x + 58, panel.y + 250, panel.w - 116, 84)
    pygame.draw.rect(screen, (255, 225, 232), quote_rect, border_radius=18)
    pygame.draw.rect(screen, (80, 50, 33), quote_rect, width=3, border_radius=18)
    quote = result.get("quote", "")
    for i, line in enumerate(_wrap_text(quote, _get_font(20, bold=True), quote_rect.w - 36)[:2]):
        _draw_text(screen, line, _get_font(20, bold=True), (142, 57, 52), center=(quote_rect.centerx, quote_rect.y + 27 + i * 28), shadow=False)
    stats = [("距离", f"{int(result.get('distance', 0))}m"), ("金币", str(int(result.get("coins", 0)))), ("用时", f"{int(result.get('time', 0))}s")]
    for i, (label, value) in enumerate(stats):
        rect = pygame.Rect(panel.x + 42 + i * 150, panel.y + 348, 124, 58)
        pygame.draw.rect(screen, (255, 235, 193), rect, border_radius=12)
        pygame.draw.rect(screen, (80, 50, 33), rect, width=3, border_radius=12)
        _draw_text(screen, label, _get_font(13, bold=True), (97, 85, 70), center=(rect.centerx, rect.y + 17), shadow=False)
        _draw_text(screen, value, _get_font(21, bold=True), (80, 50, 33), center=(rect.centerx, rect.y + 40), shadow=False)
    buttons = [
        Button((panel.centerx - 206, panel.y + 424, 190, 42), "再跑一次", "replay", 18, color=(255, 181, 76), text_color=(70, 45, 30)),
        Button((panel.centerx + 16, panel.y + 424, 190, 42), "返回菜单", "menu", 18, color=(83, 197, 255), text_color=(70, 45, 30)),
    ]
    mouse = pygame.mouse.get_pos()
    for i, btn in enumerate(buttons):
        btn.update(mouse)
        btn.draw(screen, selected=i == selected_btn)
    return buttons


def _draw_runner(surface, cx, foot_y, phase, skin, hair, shirt, pants, shoe, bag, scale=1.0, female=False):
    s = scale
    body_w, body_h = int(34 * s), int(46 * s)
    head_r = int(14 * s)
    hip_y = foot_y - int(43 * s)
    shoulder_y = foot_y - int(73 * s)
    body_rect = pygame.Rect(cx - body_w // 2, shoulder_y, body_w, body_h)
    leg = math.sin(phase) * 22 * s
    arm = -math.sin(phase) * 18 * s
    for lx in [-1, 1]:
        knee = (cx + lx * 7 * s + leg * lx * 0.35, hip_y + 18 * s)
        foot = (cx + lx * 8 * s + leg * lx, foot_y)
        pygame.draw.line(surface, (45, 35, 34), (cx + lx * 7 * s, hip_y), knee, int(7 * s))
        pygame.draw.line(surface, pants, (cx + lx * 7 * s, hip_y), knee, int(5 * s))
        pygame.draw.line(surface, (45, 35, 34), knee, foot, int(7 * s))
        pygame.draw.line(surface, skin, knee, foot, int(5 * s))
        pygame.draw.ellipse(surface, (45, 35, 34), (foot[0] - 12 * s, foot[1] - 5 * s, 24 * s, 10 * s))
        pygame.draw.ellipse(surface, shoe, (foot[0] - 10 * s, foot[1] - 4 * s, 20 * s, 7 * s))
    pygame.draw.rect(surface, (45, 35, 34), body_rect.inflate(6, 6), border_radius=int(9 * s))
    pygame.draw.rect(surface, shirt, body_rect, border_radius=int(8 * s))
    pygame.draw.rect(surface, (255, 248, 225), (body_rect.x + 7 * s, body_rect.y + 6 * s, body_w - 14 * s, 8 * s), border_radius=int(3 * s))
    bag_rect = pygame.Rect(body_rect.right - 4 * s, body_rect.y + 8 * s, 14 * s, 34 * s)
    pygame.draw.rect(surface, (45, 35, 34), bag_rect.inflate(4, 4), border_radius=int(5 * s))
    pygame.draw.rect(surface, bag, bag_rect, border_radius=int(4 * s))
    for side in [-1, 1]:
        hand = (cx + side * (18 * s + arm * side), shoulder_y + 42 * s)
        pygame.draw.line(surface, (45, 35, 34), (cx + side * 14 * s, shoulder_y + 12 * s), hand, int(7 * s))
        pygame.draw.line(surface, skin, (cx + side * 14 * s, shoulder_y + 12 * s), hand, int(5 * s))
        pygame.draw.circle(surface, skin, (int(hand[0]), int(hand[1])), int(4 * s))
    head_c = (int(cx + 2 * s), int(shoulder_y - 13 * s))
    pygame.draw.circle(surface, (45, 35, 34), head_c, head_r + int(3 * s))
    pygame.draw.circle(surface, skin, head_c, head_r)
    hair_rect = pygame.Rect(head_c[0] - head_r, head_c[1] - head_r - 3 * s, head_r * 2, head_r + 7 * s)
    pygame.draw.rect(surface, hair, hair_rect, border_radius=int(9 * s))
    if female:
        pony_x = head_c[0] - int(18 * s) + int(math.sin(phase) * 4 * s)
        pygame.draw.ellipse(surface, hair, (pony_x - 22 * s, head_c[1] - 10 * s, 28 * s, 18 * s))
        pygame.draw.circle(surface, (255, 112, 150), (head_c[0] - int(10 * s), head_c[1] - int(14 * s)), int(4 * s))
    pygame.draw.circle(surface, (35, 30, 30), (head_c[0] + int(6 * s), head_c[1] - int(1 * s)), int(2.4 * s))
    pygame.draw.arc(surface, (158, 73, 55), (head_c[0] - 2 * s, head_c[1] + 5 * s, 11 * s, 7 * s), 0, math.pi, max(1, int(2 * s)))


def _wrap_text(text, font, max_width):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines or [text]
