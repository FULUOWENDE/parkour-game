"""Menu system for 赶早八 Campus Rush."""
import math
import os
import sys

import pygame

from src.constants import (
    CHAR_LIST,
    GROUND_Y,
    HEIGHT,
    MENU_ACCENT,
    MENU_BG,
    MENU_BTN_DISABLED,
    MENU_BTN_HOVER,
    MENU_BTN_NORMAL,
    MENU_BTN_TEXT,
    MENU_CARD_BG,
    MENU_DANGER,
    MENU_OVERLAY,
    MENU_SUBTLE,
    MENU_TITLE_COLOR,
    MODE_LIST,
    OUTLINE,
    OVERHEAD_BOTTOM,
    PLAYER_H,
    PLAYER_SLIDE_H,
    PLAYER_W,
    WIDTH,
)
from src.utils import draw_circle_outlined, draw_rounded_rect

# ── Font loading ──────────────────────────────────────────────────
_FONT_REGULAR = os.path.join(os.path.dirname(__file__), "resources", "fonts", "NotoSansSC-Regular.ttf")
_FONT_BOLD = os.path.join(os.path.dirname(__file__), "resources", "fonts", "NotoSansSC-Bold.ttf")
_FONT_CACHE = {}


def _get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        path = _FONT_BOLD if bold else _FONT_REGULAR
        try:
            _FONT_CACHE[key] = pygame.font.Font(path, size)
        except Exception:
            _FONT_CACHE[key] = pygame.font.Font(None, size)
    return _FONT_CACHE[key]


# ═══════════════════════════════════════════════════════════════════
#  BUTTON UTILITY
# ═══════════════════════════════════════════════════════════════════

class Button:
    """A clickable/hoverable rectangular button."""

    def __init__(self, rect, text, action, font_size=22, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font_size = font_size
        self.enabled = enabled
        self.hovered = False
        self._font = None

    @property
    def font(self):
        if self._font is None:
            self._font = _get_font(self.font_size)
        return self._font

    def update(self, mouse_pos):
        if self.enabled:
            self.hovered = self.rect.collidepoint(mouse_pos)
        else:
            self.hovered = False

    def handle_click(self, mouse_pos):
        if self.enabled and self.rect.collidepoint(mouse_pos):
            return self.action
        return None

    def draw(self, surface):
        if not self.enabled:
            color = MENU_BTN_DISABLED
            text_color = (160, 160, 170)
        elif self.hovered:
            color = MENU_BTN_HOVER
            text_color = (20, 30, 40)
        else:
            color = MENU_BTN_NORMAL
            text_color = MENU_BTN_TEXT

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, OUTLINE, self.rect, width=2, border_radius=8)

        txt = self.font.render(self.text, True, text_color)
        tw, th = txt.get_size()
        surface.blit(txt, (self.rect.centerx - tw // 2, self.rect.centery - th // 2))


# ═══════════════════════════════════════════════════════════════════
#  0. MAIN MENU
# ═══════════════════════════════════════════════════════════════════

def draw_main_menu(screen, buttons, selected_idx, help_visible, frame, high_score=0):
    """Draw the main menu screen."""
    # Background gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(MENU_BG[0] * (1 - t * 0.3))
        g = int(MENU_BG[1] * (1 - t * 0.2))
        b = int(MENU_BG[2] * (1 + t * 0.15))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    cy = HEIGHT // 2

    # Title
    font_title = _get_font(52, bold=True)
    title = font_title.render("赶 早 八", True, MENU_TITLE_COLOR)
    tw, th = title.get_size()
    screen.blit(title, (WIDTH // 2 - tw // 2, cy - 155))

    # Subtitle
    font_sub = _get_font(26)
    sub = font_sub.render("Campus Rush", True, MENU_ACCENT)
    sw, sh = sub.get_size()
    screen.blit(sub, (WIDTH // 2 - sw // 2, cy - 90))

    # Decorative line
    line_y = cy - 65
    line_w = 160
    lx = WIDTH // 2 - line_w // 2
    pygame.draw.line(screen, MENU_ACCENT, (lx, line_y), (lx + 50, line_y), 3)
    pygame.draw.circle(screen, MENU_ACCENT, (lx + 70, line_y), 4)
    pygame.draw.line(screen, MENU_ACCENT, (lx + 90, line_y), (lx + line_w, line_y), 3)

    # Buttons
    btn_w, btn_h = 200, 44
    btn_x = WIDTH // 2 - btn_w // 2
    start_y = cy - 20

    # Rebuild button rects with correct positions
    buttons.clear()
    buttons.append(Button((btn_x, start_y, btn_w, btn_h), "开始游戏", "start"))
    buttons.append(Button((btn_x, start_y + 54, btn_w, btn_h), "游戏说明", "help"))
    buttons.append(Button((btn_x, start_y + 108, btn_w, btn_h), "退出游戏", "quit"))

    # Update hover state and draw
    mouse_pos = pygame.mouse.get_pos()
    for i, btn in enumerate(buttons):
        btn.update(mouse_pos)
        # Highlight selected (keyboard nav)
        if i == selected_idx:
            btn.hovered = True
        btn.draw(screen)

    # High score footer
    if high_score > 0:
        font_sm = _get_font(14)
        hs = font_sm.render(f"历史最高分：{high_score}", True, MENU_SUBTLE)
        hsw, hsh = hs.get_size()
        screen.blit(hs, (WIDTH // 2 - hsw // 2, HEIGHT - 40))

    # Version / credit
    font_tiny = _get_font(11)
    credit = font_tiny.render("v1.0 · 江西师大数字游民出品", True, (140, 160, 190))
    cw, ch = credit.get_size()
    screen.blit(credit, (WIDTH // 2 - cw // 2, HEIGHT - 22))

    # Help popup
    if help_visible:
        _draw_help_overlay(screen)


def _draw_help_overlay(screen):
    """Draw a help/instructions popup overlay."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    # Popup box
    popup_w, popup_h = 460, 340
    popup_x = WIDTH // 2 - popup_w // 2
    popup_y = HEIGHT // 2 - popup_h // 2
    popup = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
    pygame.draw.rect(popup, (30, 40, 60, 230), popup.get_rect(), border_radius=12)
    pygame.draw.rect(popup, OUTLINE, popup.get_rect(), width=2, border_radius=12)
    screen.blit(popup, (popup_x, popup_y))

    font_lg = _get_font(26, bold=True)
    font_md = _get_font(16)
    font_sm = _get_font(14)

    # Title
    title = font_lg.render("游戏说明", True, MENU_ACCENT)
    tw, th = title.get_size()
    screen.blit(title, (WIDTH // 2 - tw // 2, popup_y + 20))

    # Instructions
    lines = [
        ("🎮 操作方式", True),
        ("空格 / ↑ / W  —  跳跃（支持二段跳）", False),
        ("↓ / S  —  下蹲滑铲（躲避高空障碍）", False),
        ("鼠标点击上半屏跳跃 / 下半屏下蹲", False),
        ("", False),
        ("🚧 障碍物类型", True),
        ("地面障碍（垃圾桶/指示牌/警戒线等）→ 跳跃躲避", False),
        ("高空障碍（树枝/横幅/道闸/雨滴）→ 下蹲躲避", False),
        ("", False),
        ("💡 道具说明", True),
        ("📖 免撞书本 — 金色护盾，抵挡一次碰撞", False),
        ("🥟 变速包子 — 蓝色减速，降低游戏速度", False),
    ]

    y_offset = popup_y + 60
    for text, is_header in lines:
        if not text:
            y_offset += 4
            continue
        font = font_md if is_header else font_sm
        color = MENU_ACCENT if is_header else MENU_SUBTLE
        rendered = font.render(text, True, color)
        screen.blit(rendered, (popup_x + 30, y_offset))
        y_offset += 22 if is_header else 20

    # Close hint
    close_hint = font_sm.render("按 Esc 或点击空白处关闭", True, (150, 150, 170))
    cw, ch = close_hint.get_size()
    screen.blit(close_hint, (WIDTH // 2 - cw // 2, popup_y + popup_h - 30))


# ═══════════════════════════════════════════════════════════════════
#  1. CHARACTER SELECT
# ═══════════════════════════════════════════════════════════════════

def draw_char_select(screen, char_idx, frame):
    """Draw the character selection screen."""
    # Background
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(60 + t * 20)
        g = int(100 + t * 30)
        b = int(160 + t * 10)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Title
    font_title = _get_font(36, bold=True)
    title = font_title.render("选择你的早八人设", True, MENU_TITLE_COLOR)
    tw, th = title.get_size()
    screen.blit(title, (WIDTH // 2 - tw // 2, 28))

    # Subtitle
    font_sub = _get_font(14)
    sub = font_sub.render("← → 方向键切换  |  回车键确认  |  Esc 返回", True, MENU_SUBTLE)
    sw, sh = sub.get_size()
    screen.blit(sub, (WIDTH // 2 - sw // 2, 68))

    # Character preview cards
    total_chars = len(CHAR_LIST)
    card_w, card_h = 160, 260
    card_spacing = 24
    total_w = total_chars * card_w + (total_chars - 1) * card_spacing
    start_x = WIDTH // 2 - total_w // 2
    card_y = 105

    for i, char in enumerate(CHAR_LIST):
        cx = start_x + i * (card_w + card_spacing)
        is_selected = i == char_idx

        # Card background
        card_rect = pygame.Rect(cx, card_y, card_w, card_h)
        if is_selected:
            # Selected card — brighter, with accent border
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (255, 255, 255, 35), card_surf.get_rect(), border_radius=10)
            screen.blit(card_surf, (cx, card_y))
            # Accent border
            border_color = MENU_ACCENT
            border_w = 3
        else:
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, MENU_CARD_BG, card_surf.get_rect(), border_radius=10)
            screen.blit(card_surf, (cx, card_y))
            border_color = (100, 140, 180)
            border_w = 1

        pygame.draw.rect(screen, border_color, card_rect, width=border_w, border_radius=10)

        # Character preview (mini player figure)
        _draw_mini_player(screen, char, cx + card_w // 2, card_y + 85, frame, is_selected)

        # Character name
        font_name = _get_font(18, bold=True)
        name_color = MENU_ACCENT if is_selected else MENU_TITLE_COLOR
        name_txt = font_name.render(char["name"], True, name_color)
        nw, nh = name_txt.get_size()
        screen.blit(name_txt, (cx + card_w // 2 - nw // 2, card_y + 155))

        # Stats
        font_stat = _get_font(12)
        stats = [
            f"跳跃 {_stat_bar(char['jump_mul'])}",
            f"下蹲 {_stat_bar(char['slide_mul'])}",
            f"速度 {_stat_bar(char['speed_mul'])}",
        ]
        for si, stat_text in enumerate(stats):
            stat_color = MENU_SUBTLE if is_selected else (160, 170, 190)
            st = font_stat.render(stat_text, True, stat_color)
            stw, sth = st.get_size()
            screen.blit(st, (cx + card_w // 2 - stw // 2, card_y + 180 + si * 18))

        # Description
        font_desc = _get_font(11)
        desc = font_desc.render(char["desc"], True, (180, 190, 210) if is_selected else (140, 150, 170))
        dw, dh = desc.get_size()
        screen.blit(desc, (cx + card_w // 2 - dw // 2, card_y + card_h - 22))

    # Navigation arrows
    arrow_y = card_y + card_h // 2
    if char_idx > 0:
        _draw_arrow(screen, start_x - 36, arrow_y, "left", True)
    else:
        _draw_arrow(screen, start_x - 36, arrow_y, "left", False)

    if char_idx < total_chars - 1:
        _draw_arrow(screen, start_x + total_w + 16, arrow_y, "right", True)
    else:
        _draw_arrow(screen, start_x + total_w + 16, arrow_y, "right", False)

    # Bottom buttons
    btn_w, btn_h = 180, 40
    btn_y = card_y + card_h + 30
    confirm_btn = Button(
        (WIDTH // 2 - btn_w - 12, btn_y, btn_w, btn_h),
        "确认选择 → 选模式", "confirm", font_size=18
    )
    back_btn = Button(
        (WIDTH // 2 + 12, btn_y, btn_w, btn_h),
        "返回主菜单", "back", font_size=18
    )

    mouse_pos = pygame.mouse.get_pos()
    confirm_btn.update(mouse_pos)
    back_btn.update(mouse_pos)
    confirm_btn.draw(screen)
    back_btn.draw(screen)

    return confirm_btn, back_btn


def _stat_bar(value):
    """Return a visual stat bar string based on multiplier value."""
    if value >= 1.15:
        return "★★★★★"
    elif value >= 1.08:
        return "★★★★☆"
    elif value >= 1.02:
        return "★★★☆☆"
    elif value >= 0.95:
        return "★★★☆☆"
    elif value >= 0.88:
        return "★★☆☆☆"
    else:
        return "★☆☆☆☆"


def _draw_mini_player(surface, char, cx, base_y, frame, selected):
    """Draw a small preview of the player character."""
    # Bobbing animation
    bob = math.sin(frame * 0.06) * 4
    by = base_y + bob

    body_color = char["color_body"]
    skin_color = char["color_skin"]
    jeans_color = char["color_jeans"]
    bag_color = char["color_bag"]
    hair_color = char["color_hair"]
    shoe_color = char["color_shoe"]

    # Scale factor for mini version
    s = 0.55
    w = int(PLAYER_W * s)
    h = int(PLAYER_H * s)
    x = cx - w // 2
    y = by - h // 2

    # Shadow
    shadow_rect = pygame.Rect(x + 2, by + h // 2 - 2, w - 4, 4)
    pygame.draw.ellipse(surface, (0, 0, 0, 30), shadow_rect)

    leg_swing = math.sin(frame * 0.12) * 7 * s
    foot_y = y + h + 1 * s

    # Legs
    lfx = cx - 3 * s + leg_swing
    rfx = cx + 3 * s - leg_swing
    pygame.draw.line(surface, OUTLINE, (cx - 3 * s, foot_y - 10 * s), (lfx, foot_y + 8 * s), max(1, int(4 * s)))
    pygame.draw.line(surface, jeans_color, (cx - 3 * s, foot_y - 10 * s), (lfx, foot_y + 8 * s), max(1, int(3 * s)))
    pygame.draw.line(surface, OUTLINE, (cx + 3 * s, foot_y - 10 * s), (rfx, foot_y + 8 * s), max(1, int(4 * s)))
    pygame.draw.line(surface, jeans_color, (cx + 3 * s, foot_y - 10 * s), (rfx, foot_y + 8 * s), max(1, int(3 * s)))
    # Shoes
    for shx in [lfx, rfx]:
        pygame.draw.ellipse(surface, OUTLINE, (shx - 4 * s, foot_y + 6 * s, 8 * s, 4 * s))
        pygame.draw.ellipse(surface, shoe_color, (shx - 3 * s, foot_y + 7 * s, 6 * s, 3 * s))

    # Backpack
    bag_rect = pygame.Rect(x + w - 3 * s, y + 10 * s, 6 * s, h - 16 * s)
    draw_rounded_rect(surface, bag_rect, bag_color, int(2 * s), outline=0)

    # Body
    body_rect = pygame.Rect(x + 2 * s, y + 12 * s, w - 4 * s, h - 18 * s)
    draw_rounded_rect(surface, body_rect, body_color, int(4 * s), outline=0)

    # Arms
    arm_swing = math.cos(frame * 0.12) * 5 * s
    pygame.draw.line(surface, OUTLINE, (cx - 1 * s, y + 16 * s), (cx - 1 * s + arm_swing, y + 24 * s), max(1, int(3 * s)))
    pygame.draw.line(surface, body_color, (cx - 1 * s, y + 16 * s), (cx - 1 * s + arm_swing, y + 24 * s), max(1, int(2 * s)))
    pygame.draw.line(surface, OUTLINE, (cx + 1 * s, y + 16 * s), (cx + 1 * s - arm_swing, y + 24 * s), max(1, int(3 * s)))
    pygame.draw.line(surface, body_color, (cx + 1 * s, y + 16 * s), (cx + 1 * s - arm_swing, y + 24 * s), max(1, int(2 * s)))

    # Head
    head_cy = int(y + 7 * s)
    # Hair
    hair_rect = pygame.Rect(cx - 6 * s, head_cy - 9 * s, 12 * s, 8 * s)
    draw_rounded_rect(surface, hair_rect, hair_color, int(3 * s), outline=0)
    # Head circle
    draw_circle_outlined(surface, (int(cx), head_cy), int(7 * s), skin_color, outline=0)
    # Eye
    eye_x = int(cx + 3 * s)
    eye_y = int(head_cy - 2 * s)
    pygame.draw.ellipse(surface, (255, 255, 255), (eye_x, eye_y, int(5 * s), int(5 * s)))
    pygame.draw.circle(surface, (20, 20, 20), (eye_x + 2, eye_y + 2), int(2 * s))

    # Selection indicator
    if selected:
        pulse = 0.8 + 0.2 * math.sin(frame * 0.08)
        alpha = int(pulse * 200)
        ring = pygame.Surface((int(w * 1.4), int(h * 1.4)), pygame.SRCALPHA)
        ring_rect = ring.get_rect()
        pygame.draw.ellipse(ring, (255, 200, 50, alpha), ring_rect, width=2)
        surface.blit(ring, (cx - ring_rect.w // 2, by - ring_rect.h // 2))


def _draw_arrow(surface, cx, cy, direction, active):
    """Draw a left or right navigation arrow."""
    color = MENU_ACCENT if active else (80, 100, 130)
    size = 10
    if direction == "left":
        pts = [(cx + size, cy - size), (cx - size // 2, cy), (cx + size, cy + size)]
    else:
        pts = [(cx - size, cy - size), (cx + size // 2, cy), (cx - size, cy + size)]
    pygame.draw.polygon(surface, color, pts)


# ═══════════════════════════════════════════════════════════════════
#  2. MODE SELECT
# ═══════════════════════════════════════════════════════════════════

def draw_mode_select(screen, mode_idx, frame):
    """Draw the game mode selection screen."""
    # Background
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(40 + t * 30)
        g = int(80 + t * 40)
        b = int(140 + t * 20)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Title
    font_title = _get_font(36, bold=True)
    title = font_title.render("选择游戏模式", True, MENU_TITLE_COLOR)
    tw, th = title.get_size()
    screen.blit(title, (WIDTH // 2 - tw // 2, 28))

    font_sub = _get_font(14)
    sub = font_sub.render("← → 方向键切换  |  回车键确认  |  Esc 返回", True, MENU_SUBTLE)
    sw, sh = sub.get_size()
    screen.blit(sub, (WIDTH // 2 - sw // 2, 68))

    # Mode cards
    total_modes = len(MODE_LIST)
    card_w, card_h = 220, 280
    card_spacing = 30
    total_w = total_modes * card_w + (total_modes - 1) * card_spacing
    start_x = WIDTH // 2 - total_w // 2
    card_y = 105

    # Mode icons (emoji)
    mode_icons = ["📚", "⚡", "🌸"]

    for i, mode in enumerate(MODE_LIST):
        cx = start_x + i * (card_w + card_spacing)
        is_selected = i == mode_idx

        # Card background
        card_rect = pygame.Rect(cx, card_y, card_w, card_h)
        if is_selected:
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (255, 255, 255, 40), card_surf.get_rect(), border_radius=12)
            screen.blit(card_surf, (cx, card_y))
            border_color = MENU_ACCENT
            border_w = 3
        else:
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, MENU_CARD_BG, card_surf.get_rect(), border_radius=12)
            screen.blit(card_surf, (cx, card_y))
            border_color = (100, 140, 180)
            border_w = 1

        pygame.draw.rect(screen, border_color, card_rect, width=border_w, border_radius=12)

        # Icon
        font_icon = _get_font(48)
        icon = font_icon.render(mode_icons[i], True, MENU_TITLE_COLOR)
        iw, ih = icon.get_size()
        icon_x = cx + card_w // 2 - iw // 2
        icon_y = card_y + 24
        # Icon circle background
        circle_cx = cx + card_w // 2
        circle_cy = icon_y + ih // 2
        circle_r = 38
        if is_selected:
            pygame.draw.circle(screen, (255, 255, 255, 20), (circle_cx, circle_cy), circle_r)
        pygame.draw.circle(screen, border_color, (circle_cx, circle_cy), circle_r, width=1)
        screen.blit(icon, (icon_x, icon_y))

        # Mode name
        font_name = _get_font(22, bold=True)
        name_color = MENU_ACCENT if is_selected else MENU_TITLE_COLOR
        name_txt = font_name.render(mode["name"], True, name_color)
        nw, nh = name_txt.get_size()
        screen.blit(name_txt, (cx + card_w // 2 - nw // 2, card_y + 115))

        # Description
        font_desc = _get_font(14)
        desc_color = MENU_SUBTLE if is_selected else (170, 180, 200)
        desc_txt = font_desc.render(mode["desc"], True, desc_color)
        dw, dh = desc_txt.get_size()
        screen.blit(desc_txt, (cx + card_w // 2 - dw // 2, card_y + 148))

        # Detail
        font_detail = _get_font(12)
        detail_color = (190, 200, 220) if is_selected else (140, 150, 170)
        # Word wrap the detail text
        detail_lines = _wrap_text(mode["detail"], font_detail, card_w - 30)
        for li, dline in enumerate(detail_lines):
            dt = font_detail.render(dline, True, detail_color)
            dtw, dth = dt.get_size()
            screen.blit(dt, (cx + card_w // 2 - dtw // 2, card_y + 175 + li * 18))

        # Difficulty indicator
        diff_y = card_y + card_h - 35
        if i == 0:
            diff_text = "难度：★★☆☆☆"
        elif i == 1:
            diff_text = "难度：★★★★★"
        else:
            diff_text = "难度：★☆☆☆☆"
        diff_color = MENU_ACCENT if is_selected else (160, 170, 190)
        font_diff = _get_font(13)
        dt = font_diff.render(diff_text, True, diff_color)
        dtw, dth = dt.get_size()
        screen.blit(dt, (cx + card_w // 2 - dtw // 2, diff_y))

        # Best score for this mode (placeholder for now)
        font_best = _get_font(11)
        best = font_best.render("期待你的挑战！", True, (130, 140, 160))
        bw, bh = best.get_size()
        screen.blit(best, (cx + card_w // 2 - bw // 2, diff_y + 18))

    # Navigation arrows
    arrow_y = card_y + card_h // 2
    if mode_idx > 0:
        _draw_arrow(screen, start_x - 36, arrow_y, "left", True)
    else:
        _draw_arrow(screen, start_x - 36, arrow_y, "left", False)
    if mode_idx < total_modes - 1:
        _draw_arrow(screen, start_x + total_w + 16, arrow_y, "right", True)
    else:
        _draw_arrow(screen, start_x + total_w + 16, arrow_y, "right", False)

    # Bottom buttons
    btn_w, btn_h = 200, 40
    btn_y = card_y + card_h + 30
    # "开始游戏" button with accent
    start_btn = Button(
        (WIDTH // 2 - btn_w - 12, btn_y, btn_w, btn_h),
        "🎮 开始游戏", "confirm", font_size=20
    )
    back_btn = Button(
        (WIDTH // 2 + 12, btn_y, btn_w, btn_h),
        "← 返回选人", "back", font_size=18
    )

    mouse_pos = pygame.mouse.get_pos()
    start_btn.update(mouse_pos)
    back_btn.update(mouse_pos)
    start_btn.draw(screen)
    back_btn.draw(screen)

    return start_btn, back_btn


def _wrap_text(text, font, max_width):
    """Wrap text to fit within max_width pixels."""
    words = list(text)  # Chinese text — wrap per character
    lines = []
    current = ""
    for ch in words:
        test = current + ch
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines if lines else [text]


# ═══════════════════════════════════════════════════════════════════
#  4. GAME OVER MENU
# ═══════════════════════════════════════════════════════════════════

def draw_game_over_menu(screen, score, high_score, char_idx, mode_idx,
                        selected_btn, new_record, frame):
    """Draw the game over / results screen overlay."""
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 10, 15, 175))
    screen.blit(overlay, (0, 0))

    cy = HEIGHT // 2

    # Panel
    panel_w, panel_h = 480, 420
    panel_x = WIDTH // 2 - panel_w // 2
    panel_y = cy - panel_h // 2 - 10
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (25, 20, 35, 235), panel.get_rect(), border_radius=14)
    pygame.draw.rect(panel, (60, 50, 70), panel.get_rect(), width=2, border_radius=14)
    screen.blit(panel, (panel_x, panel_y))

    # Game Over title
    font_go = _get_font(40, bold=True)
    go_txt = font_go.render("GAME OVER", True, (255, 70, 70))
    gw, gh = go_txt.get_size()
    screen.blit(go_txt, (WIDTH // 2 - gw // 2, panel_y + 18))

    # Score
    font_score = _get_font(48, bold=True)
    score_txt = font_score.render(f"{int(score):06d}", True, MENU_TITLE_COLOR)
    sw, sh = score_txt.get_size()
    screen.blit(score_txt, (WIDTH // 2 - sw // 2, panel_y + 62))

    font_label = _get_font(14)
    score_label = font_label.render("本局得分", True, MENU_SUBTLE)
    slw, slh = score_label.get_size()
    screen.blit(score_label, (WIDTH // 2 - slw // 2, panel_y + 118))

    # New record banner
    if new_record:
        font_rec = _get_font(20, bold=True)
        rec_txt = font_rec.render("★  新 纪 录  ★", True, MENU_ACCENT)
        rw, rh = rec_txt.get_size()
        # Pulsing background
        pulse = 0.4 + 0.6 * math.sin(frame * 0.06)
        rec_bg = pygame.Surface((rw + 30, rh + 12), pygame.SRCALPHA)
        pygame.draw.rect(rec_bg, (255, 200, 50, int(pulse * 80)), rec_bg.get_rect(), border_radius=8)
        screen.blit(rec_bg, (WIDTH // 2 - rw // 2 - 15, panel_y + 136))
        screen.blit(rec_txt, (WIDTH // 2 - rw // 2, panel_y + 140))
    else:
        font_best = _get_font(15)
        best_txt = font_best.render(f"历史最高分：{high_score:06d}", True, (180, 180, 190))
        bw, bh = best_txt.get_size()
        screen.blit(best_txt, (WIDTH // 2 - bw // 2, panel_y + 142))

    # Info line: character + mode
    font_info = _get_font(14)
    char_name = CHAR_LIST[char_idx]["name"] if char_idx < len(CHAR_LIST) else "未知"
    mode_name = MODE_LIST[mode_idx]["name"] if mode_idx < len(MODE_LIST) else "未知"
    info_text = f"角色：{char_name}  |  模式：{mode_name}"
    info_txt = font_info.render(info_text, True, MENU_SUBTLE)
    iw, ih = info_txt.get_size()
    screen.blit(info_txt, (WIDTH // 2 - iw // 2, panel_y + 177))

    # Divider line
    div_y = panel_y + 200
    pygame.draw.line(screen, (60, 55, 75), (panel_x + 40, div_y), (panel_x + panel_w - 40, div_y), 1)

    # Action buttons
    btn_w, btn_h = 240, 44
    btn_x = WIDTH // 2 - btn_w // 2
    btn_start_y = div_y + 20
    btn_gap = 52

    buttons = [
        Button((btn_x, btn_start_y, btn_w, btn_h), "🔄  再来一局", "replay", font_size=20),
        Button((btn_x, btn_start_y + btn_gap, btn_w, btn_h), "🎯  重新选模式", "reselect", font_size=18),
        Button((btn_x, btn_start_y + btn_gap * 2, btn_w, btn_h), "🏠  返回主菜单", "menu", font_size=18),
    ]

    mouse_pos = pygame.mouse.get_pos()
    for i, btn in enumerate(buttons):
        btn.update(mouse_pos)
        if i == selected_btn:
            btn.hovered = True
        btn.draw(screen)

    # Keyboard hint
    font_hint = _get_font(11)
    hint = font_hint.render("↑↓ 方向键选择  |  回车键确认  |  鼠标点击", True, (120, 120, 140))
    hw, hh = hint.get_size()
    screen.blit(hint, (WIDTH // 2 - hw // 2, panel_y + panel_h - 22))

    return buttons
