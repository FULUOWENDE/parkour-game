import math
import random

import pygame

from src.constants import (
    BANNER_POLE,
    BANNER_POLE_HL,
    BANNER_RED,
    BANNER_RED_DARK,
    BANNER_RED_LIGHT,
    BANNER_TEXT,
    BARRIER_COUNTER,
    BARRIER_POST,
    BARRIER_POST_HL,
    BARRIER_RED,
    BIKE_GREEN,
    BIKE_RIDER,
    BIKE_TIRE,
    BUMP_BLACK,
    BUMP_YELLOW,
    CART_HIGHLIGHT,
    CART_RED,
    CART_SILVER,
    CART_WHEEL,
    CONE_HIGHLIGHT,
    CONE_ORANGE,
    CONE_SHADOW,
    CONE_WHITE,
    GROUND_Y,
    MIN_SPAWN_GAP,
    OUTLINE,
    OVERHEAD_BOTTOM,
    PLAYER_SKIN,
    SHADOW,
    SIGN_ARROW,
    SIGN_BOARD,
    SIGN_POLE,
    SIGN_TEXT,
    TAPE_YELLOW,
    TRASH_CAN,
    TRASH_HIGHLIGHT,
    TRASH_LID,
    TRASH_SHADOW,
    TREE_LEAF,
    TREE_LEAF_DARK,
    TREE_LEAF_LIGHT,
    TREE_LEAF_MID,
    TREE_TRUNK,
    TREE_TRUNK_DARK,
    TREE_TRUNK_LIGHT,
    WIDTH,
)
from src.utils import (
    draw_circle_outlined,
    draw_ellipse_outlined,
    draw_polygon_outlined,
    draw_rounded_rect,
)

# ── Font cache for obstacle text ────────────────────────────────
_FONT_CACHE = {}


def _get_obs_font(size):
    if size not in _FONT_CACHE:
        try:
            font = pygame.font.SysFont("stheitimedium", size)
            test = font.render("早", True, (255, 255, 255))
            if test.get_width() < 5:
                raise ValueError("No Chinese glyph")
        except Exception:
            font = pygame.font.Font(None, size)
        _FONT_CACHE[size] = font
    return _FONT_CACHE[size]


# ── Base Obstacle ───────────────────────────────────────────────
class Obstacle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.scored = False
        self.overhead = False

    def update(self, speed):
        self.x -= speed

    def is_offscreen(self):
        return self.x + self.w < -50

    def draw(self, surface):
        raise NotImplementedError


# ═══════════════════════════════════════════════════════════════════
#  GROUND OBSTACLES  (jump over)
# ═══════════════════════════════════════════════════════════════════

# ── TrashCan (垃圾桶) ──────────────────────────────────────────
class TrashCan(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 40, 34, 40)

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # drop shadow
        shadow_surf = pygame.Surface((w + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, SHADOW, shadow_surf.get_rect())
        surface.blit(shadow_surf, (x - 4, GROUND_Y - 4))

        # body — cylindrical with gradient
        for i in range(w):
            t = i / w
            # darker at edges, lighter left of center (light from left)
            r = int(TRASH_CAN[0] * (0.6 + 0.4 * (1 - abs(t - 0.35) * 1.5)))
            g = int(TRASH_CAN[1] * (0.6 + 0.4 * (1 - abs(t - 0.35) * 1.5)))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            pygame.draw.line(surface, (r, g, TRASH_CAN[2]), (x + i, y + 8), (x + i, y + h))

        # corrugated ridges
        for ry in range(y + 14, y + h - 6, 6):
            pygame.draw.line(surface, TRASH_SHADOW, (x + 2, ry), (x + w - 2, ry), 1)

        # lid — domed
        lid_rect = pygame.Rect(x - 2, y - 2, w + 4, 14)
        pygame.draw.ellipse(surface, TRASH_LID, lid_rect)
        pygame.draw.ellipse(surface, OUTLINE, lid_rect, 1)
        # lid highlight
        hl_rect = pygame.Rect(x + 2, y, w - 4, 6)
        pygame.draw.ellipse(surface, TRASH_HIGHLIGHT, hl_rect)

        # lid handle
        handle_rect = pygame.Rect(x + w // 2 - 5, y - 4, 10, 10)
        pygame.draw.ellipse(surface, (100, 110, 120), handle_rect)
        pygame.draw.ellipse(surface, OUTLINE, handle_rect, 1)

        # recycle logo (simplified triangle)
        cx, cy = int(x + w // 2), int(y + 30)
        pts = [(cx, cy - 5), (cx + 5, cy + 3), (cx - 5, cy + 3)]
        pygame.draw.polygon(surface, (130, 190, 140), pts, 1)
        # small arrows
        for ang in [0, 2.1, 4.2]:
            ax = cx + math.cos(ang) * 4
            ay = cy + math.sin(ang) * 3
            pygame.draw.circle(surface, (150, 210, 160), (int(ax), int(ay)), 2)


# ── SignPost (校园指示牌) ──────────────────────────────────────
class SignPost(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 72, 30, 72)
        # pre-render text
        font = _get_obs_font(12)
        self._text = font.render("教学楼", True, SIGN_TEXT)
        self._arrow = font.render("→", True, SIGN_ARROW)

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow
        shadow_surf = pygame.Surface((12, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, SHADOW, shadow_surf.get_rect())
        surface.blit(shadow_surf, (x + w // 2 - 6, GROUND_Y - 3))

        # pole — metallic with highlight
        pole_w = 5
        pole_x = x + (w - pole_w) / 2
        pole_rect = pygame.Rect(pole_x, y + 26, pole_w, h - 26)
        pygame.draw.rect(surface, SIGN_POLE, pole_rect)
        # pole highlight
        pygame.draw.rect(surface, (180, 180, 190), (pole_x, y + 26, 2, h - 26))
        pygame.draw.rect(surface, OUTLINE, pole_rect, 1)

        # pole base
        base_rect = pygame.Rect(pole_x - 3, GROUND_Y - 6, pole_w + 6, 6)
        pygame.draw.rect(surface, SIGN_POLE, base_rect)
        pygame.draw.rect(surface, OUTLINE, base_rect, 1)

        # signboard
        board_rect = pygame.Rect(x - 2, y, w + 4, 28)
        draw_rounded_rect(surface, board_rect, SIGN_BOARD, 3, outline=1)
        # board highlight (top edge)
        hl_rect = pygame.Rect(x, y + 1, w, 3)
        pygame.draw.rect(surface, (120, 200, 150), hl_rect, border_radius=2)

        # text on board
        tw, th = self._text.get_size()
        surface.blit(self._text, (int(x + w / 2 - tw / 2), int(y + 6)))
        aw, ah = self._arrow.get_size()
        surface.blit(self._arrow, (int(x + w / 2 - aw / 2), int(y + 16)))


# ── TapeBarrier (警戒线路障) ───────────────────────────────────
class TapeBarrier(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 38, 80, 38)

    def draw(self, surface):
        x, y = self.x, self.y

        # shadow
        shadow_surf = pygame.Surface((self.w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, SHADOW, shadow_surf.get_rect())
        surface.blit(shadow_surf, (x, GROUND_Y - 4))

        # left cone
        self._draw_cone(surface, x + 6, y + 8)
        # right cone
        self._draw_cone(surface, x + 50, y + 8)

        # caution tape — yellow with stripe pattern
        tape_y = y + 10
        # outline
        pygame.draw.line(surface, OUTLINE, (x + 18, tape_y), (x + 62, tape_y), 6)
        # yellow tape
        pygame.draw.line(surface, TAPE_YELLOW, (x + 18, tape_y), (x + 62, tape_y), 4)
        # diagonal stripe pattern on tape
        for sx in range(int(x + 20), int(x + 60), 8):
            stripe = pygame.Surface((6, 4), pygame.SRCALPHA)
            pygame.draw.line(stripe, (180, 80, 0, 180), (0, 0), (6, 4), 2)
            surface.blit(stripe, (sx, tape_y - 2))

    def _draw_cone(self, surface, cx, top_y):
        cone_w = 16
        cone_h = 26
        # cone body
        pts = [
            (cx - cone_w // 2, top_y + cone_h),
            (cx + cone_w // 2, top_y + cone_h),
            (cx + 3, top_y),
            (cx - 3, top_y),
        ]
        pygame.draw.polygon(surface, CONE_SHADOW, pts)
        # highlight (lighter on left side)
        hl_pts = [
            (cx - cone_w // 2, top_y + cone_h),
            (cx, top_y + cone_h),
            (cx, top_y),
            (cx - 3, top_y),
        ]
        pygame.draw.polygon(surface, CONE_HIGHLIGHT, hl_pts)
        # main color
        main_pts = [
            (cx - cone_w // 2 + 2, top_y + cone_h - 2),
            (cx + cone_w // 2 - 2, top_y + cone_h - 2),
            (cx + 1, top_y + 2),
            (cx - 1, top_y + 2),
        ]
        pygame.draw.polygon(surface, CONE_ORANGE, main_pts)
        # outline
        pygame.draw.polygon(surface, OUTLINE, pts, 1)

        # white reflective stripes
        for i, sy in enumerate([top_y + 16, top_y + 21]):
            sw = 12 - i * 2
            strip_pts = [
                (cx - sw // 2, sy),
                (cx + sw // 2, sy),
                (cx + sw // 2 - 1, sy + 2),
                (cx - sw // 2 + 1, sy + 2),
            ]
            pygame.draw.polygon(surface, CONE_WHITE, strip_pts)


# ── CartHandle (食堂餐车) ──────────────────────────────────────
class CartHandle(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 58, 56, 24)

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow
        shadow_surf = pygame.Surface((w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, SHADOW, shadow_surf.get_rect())
        surface.blit(shadow_surf, (x, GROUND_Y - 4))

        # cart body (below handle)
        body_rect = pygame.Rect(x + 6, GROUND_Y - 24, w - 12, 24)
        draw_rounded_rect(surface, body_rect, CART_RED, 6, outline=1)
        # body highlight
        hl_rect = pygame.Rect(x + 10, GROUND_Y - 22, w - 20, 6)
        pygame.draw.rect(surface, CART_HIGHLIGHT, hl_rect, border_radius=3)

        # wheels
        for wx in [x + 12, x + w - 16]:
            # tire
            draw_circle_outlined(surface, (int(wx), int(GROUND_Y - 5)), 7, CART_WHEEL, outline=1)
            # hub
            pygame.draw.circle(surface, (160, 160, 170), (int(wx), int(GROUND_Y - 5)), 3)

        # handlebar (collision area)
        bar_rect = pygame.Rect(x, y + 2, w, 12)
        draw_rounded_rect(surface, bar_rect, CART_SILVER, 5, outline=1)
        # bar highlight
        bar_hl = pygame.Rect(x + 2, y + 3, w - 4, 3)
        pygame.draw.rect(surface, (220, 225, 235), bar_hl, border_radius=2)

        # steam wisps
        steam_surf = pygame.Surface((16, 14), pygame.SRCALPHA)
        for sx, sy, sr in [(4, 10, 4), (12, 6, 3), (8, 2, 3)]:
            pygame.draw.circle(steam_surf, (255, 255, 255, 70), (sx, sy), sr)
        surface.blit(steam_surf, (x + w // 2 - 8, y - 12))


# ── SpeedBump (减速带) ─────────────────────────────────────────
class SpeedBump(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 16, 60, 16)

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow
        shadow_surf = pygame.Surface((w + 6, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, SHADOW, shadow_surf.get_rect())
        surface.blit(shadow_surf, (x - 3, GROUND_Y - 4))

        # bump body — rounded with 3D shading
        bump_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, BUMP_YELLOW, bump_rect, border_radius=5)
        # top highlight (raised portion)
        hl_rect = pygame.Rect(x + 4, y + 1, w - 8, 5)
        pygame.draw.rect(surface, (255, 240, 100), hl_rect, border_radius=3)
        # bottom shadow
        sd_rect = pygame.Rect(x + 4, y + h - 4, w - 8, 4)
        pygame.draw.rect(surface, (200, 170, 30), sd_rect, border_radius=2)

        # diagonal black warning stripes
        for i in range(5):
            sx = x + i * 12 - 4
            stripe_pts = [
                (sx, y + 3),
                (sx + 8, y + 3),
                (sx + 8, y + h - 3),
                (sx, y + h - 3),
            ]
            pygame.draw.polygon(surface, BUMP_BLACK, stripe_pts)

        # outline
        pygame.draw.rect(surface, OUTLINE, bump_rect, width=1, border_radius=5)


# ── ElectricBike (电动车) ──────────────────────────────────────
class ElectricBike(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 60, 48, 32)

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow
        shadow_surf = pygame.Surface((w + 4, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, SHADOW, shadow_surf.get_rect())
        surface.blit(shadow_surf, (x - 2, GROUND_Y - 5))

        # wheels
        for wx, wy in [(x + 9, GROUND_Y - 7), (x + w - 9, GROUND_Y - 7)]:
            # tire
            draw_circle_outlined(surface, (int(wx), int(wy)), 8, BIKE_TIRE, outline=1)
            # rim highlight
            pygame.draw.circle(surface, (100, 100, 100), (int(wx), int(wy)), 5)
            # hub
            pygame.draw.circle(surface, (200, 200, 210), (int(wx), int(wy)), 3)

        # scooter body — flat floor + front shield
        # floorboard
        floor_rect = pygame.Rect(x + 6, y + 16, w - 12, 8)
        draw_rounded_rect(surface, floor_rect, BIKE_GREEN, 3, outline=1)
        # front shield (sloped)
        shield_pts = [
            (x + w - 14, y + 6),
            (x + w - 6, y + 6),
            (x + w - 4, y + 18),
            (x + w - 12, y + 18),
        ]
        draw_polygon_outlined(surface, BIKE_GREEN, shield_pts, outline=1)

        # seat
        seat_rect = pygame.Rect(x + 12, y + 6, 14, 8)
        draw_rounded_rect(surface, seat_rect, (30, 30, 35), 3, outline=1)

        # headlight
        hl_rect = pygame.Rect(x + w - 5, y + 10, 6, 6)
        pygame.draw.ellipse(surface, (255, 255, 200), hl_rect)
        pygame.draw.ellipse(surface, OUTLINE, hl_rect, 1)

        # rider
        rider_cx = int(x + 18)
        rider_cy = int(y - 2)
        # helmet
        helmet_rect = pygame.Rect(rider_cx - 6, rider_cy - 2, 12, 10)
        pygame.draw.ellipse(surface, BIKE_RIDER, helmet_rect)
        pygame.draw.ellipse(surface, OUTLINE, helmet_rect, 1)
        # visor
        visor_rect = pygame.Rect(rider_cx + 2, rider_cy + 2, 5, 4)
        pygame.draw.ellipse(surface, (40, 40, 40), visor_rect)
        # body
        body_pts = [
            (rider_cx - 4, rider_cy + 6),
            (rider_cx + 4, rider_cy + 6),
            (rider_cx + 3, y + 16),
            (rider_cx - 3, y + 16),
        ]
        draw_polygon_outlined(surface, (60, 80, 160), body_pts, outline=1)

        # handlebars
        hb_x = int(x + w - 10)
        pygame.draw.line(surface, OUTLINE, (hb_x, y + 14), (hb_x, y + 4), 4)
        pygame.draw.line(surface, CART_SILVER, (hb_x, y + 14), (hb_x, y + 4), 2)
        # handlebar grips
        pygame.draw.circle(surface, (40, 40, 40), (hb_x, y + 4), 2)


# ═══════════════════════════════════════════════════════════════════
#  OVERHEAD OBSTACLES  (slide under — can't be jumped)
# ═══════════════════════════════════════════════════════════════════

# ── TreeBranch (低垂树枝) ──────────────────────────────────────
class TreeBranch(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 28, 72, 28)
        self.overhead = True

    def draw(self, surface):
        x, y = self.x, self.y  # y = OVERHEAD_BOTTOM - 28
        w = self.w
        cx = x + w // 2
        bot = OVERHEAD_BOTTOM

        # main trunk (extends up and right)
        trunk_top = 80
        trunk_pts = [
            (cx + 8, bot),         # bottom right
            (cx - 12, bot),        # bottom left
            (cx - 6, bot - 40),    # mid left
            (cx + 10, bot - 80),   # mid upper
            (cx + 18, trunk_top),  # top right
            (cx + 10, trunk_top),  # top left
        ]
        pygame.draw.polygon(surface, TREE_TRUNK_DARK, trunk_pts)
        # trunk highlight
        trunk_hl = [
            (cx + 4, bot),
            (cx + 8, bot),
            (cx + 14, trunk_top - 20),
            (cx + 8, trunk_top - 20),
        ]
        pygame.draw.polygon(surface, TREE_TRUNK_LIGHT, trunk_hl)
        # trunk outline
        pygame.draw.polygon(surface, OUTLINE, trunk_pts, 1)

        # foliage clusters — layered circles for depth
        foliage_clusters = [
            # (cx_offset, cy_offset, radius, color)
            (cx - 18, bot - 50, 22, TREE_LEAF_DARK),
            (cx - 8, bot - 65, 18, TREE_LEAF_MID),
            (cx + 14, bot - 70, 16, TREE_LEAF_DARK),
            (cx - 22, bot - 35, 14, TREE_LEAF),
            (cx + 6, bot - 55, 15, TREE_LEAF_LIGHT),
            (cx - 14, bot - 20, 12, TREE_LEAF_MID),
            (cx + 18, bot - 45, 13, TREE_LEAF),
            (cx - 28, bot - 40, 10, TREE_LEAF_LIGHT),
            (cx + 22, bot - 25, 10, TREE_LEAF_DARK),
        ]
        for fx, fy, fr, fc in foliage_clusters:
            pygame.draw.circle(surface, fc, (int(fx), int(fy)), fr)
            # mini highlight dot on each cluster
            pygame.draw.circle(surface, TREE_LEAF_LIGHT, (int(fx) - 3, int(fy) - 3), max(2, fr // 5))

        # small dangling branches at bottom
        for dbx, dby in [(cx - 10, bot - 2), (cx - 2, bot + 2), (cx + 10, bot - 4)]:
            pygame.draw.line(surface, TREE_TRUNK, (dbx, dby), (dbx + 3, dby + 8), 2)
            pygame.draw.circle(surface, TREE_LEAF_MID, (dbx + 3, dby + 8), 3)

        # trunk bark texture lines
        for tx in range(int(cx) - 4, int(cx) + 12, 6):
            pygame.draw.line(surface, TREE_TRUNK_DARK, (tx, bot - 30), (tx, bot - 10), 1)


# ── CampusBanner (校园宣传横幅) ─────────────────────────────────
class CampusBanner(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 30, 100, 30)
        self.overhead = True
        self._banner_texts = [
            _get_obs_font(13).render("热烈欢迎", True, BANNER_TEXT),
            _get_obs_font(13).render("新同学", True, BANNER_TEXT),
        ]

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # poles
        pole_w = 6
        pole_top = 130
        for px in [x + 6, x + w - 12]:
            pole_rect = pygame.Rect(px, pole_top, pole_w, GROUND_Y - pole_top)
            pygame.draw.rect(surface, BANNER_POLE, pole_rect)
            pygame.draw.rect(surface, BANNER_POLE_HL, (px, pole_top, 2, GROUND_Y - pole_top))
            pygame.draw.rect(surface, OUTLINE, pole_rect, 1)
            # pole cap
            cap_rect = pygame.Rect(px - 1, pole_top - 2, pole_w + 2, 6)
            pygame.draw.ellipse(surface, BANNER_POLE, cap_rect)
            pygame.draw.ellipse(surface, OUTLINE, cap_rect, 1)

        # red banner fabric
        banner_top = y + 2
        banner_h = h - 4
        banner_rect = pygame.Rect(x + 12, banner_top, w - 24, banner_h)
        pygame.draw.rect(surface, BANNER_RED, banner_rect)
        # fabric folds (vertical darker lines)
        for fx in range(int(x + 24), int(x + w - 24), 14):
            pygame.draw.line(surface, BANNER_RED_DARK, (fx, banner_top + 2), (fx, banner_top + banner_h - 2), 1)
        # top edge highlight
        pygame.draw.rect(surface, BANNER_RED_LIGHT, (x + 12, banner_top, w - 24, 3))
        # outline
        pygame.draw.rect(surface, OUTLINE, banner_rect, 1)

        # rope knots at pole connections
        for kx in [x + 8, x + w - 14]:
            pygame.draw.rect(surface, (200, 180, 100), (kx - 2, banner_top + 2, 5, 6))
            pygame.draw.rect(surface, OUTLINE, (kx - 2, banner_top + 2, 5, 6), 1)

        # text on banner
        tx = int(x + 18)
        for text_surf in self._banner_texts:
            surface.blit(text_surf, (tx, int(banner_top + 4)))
            tx += text_surf.get_width() + 10


# ── BarrierGate (校园道闸杆) ────────────────────────────────────
class BarrierGate(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 26, 84, 26)
        self.overhead = True

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.w, self.h
        arm_y = y + 10
        arm_h = 10

        # post (right side)
        post_x = x + w - 14
        post_top = 200
        post_w = 10
        post_rect = pygame.Rect(post_x, post_top, post_w, GROUND_Y - post_top)
        pygame.draw.rect(surface, BARRIER_POST, post_rect)
        pygame.draw.rect(surface, BARRIER_POST_HL, (post_x, post_top, 3, GROUND_Y - post_top))
        pygame.draw.rect(surface, OUTLINE, post_rect, 1)

        # counterweight box at top of post
        cw_rect = pygame.Rect(post_x - 4, post_top - 12, post_w + 8, 14)
        pygame.draw.rect(surface, BARRIER_COUNTER, cw_rect)
        pygame.draw.rect(surface, (80, 80, 90), (post_x - 2, post_top - 10, 4, 10))
        pygame.draw.rect(surface, OUTLINE, cw_rect, 1)

        # barrier arm — red/white stripes
        arm_rect = pygame.Rect(x, arm_y, w - 14, arm_h)
        pygame.draw.rect(surface, (240, 240, 240), arm_rect)
        # red stripes
        stripe_count = 7
        stripe_w = (w - 14) / stripe_count
        for si in range(stripe_count):
            if si % 2 == 0:
                sx = x + si * stripe_w
                stripe_rect = pygame.Rect(sx, arm_y, math.ceil(stripe_w), arm_h)
                pygame.draw.rect(surface, BARRIER_RED, stripe_rect)
        # arm outline
        pygame.draw.rect(surface, OUTLINE, arm_rect, 1)
        # arm highlight
        pygame.draw.rect(surface, (255, 255, 255, 100), (x + 2, arm_y + 1, w - 18, 2))


# ═══════════════════════════════════════════════════════════════════
#  OBSTACLE TYPE REGISTRY & FACTORY
# ═══════════════════════════════════════════════════════════════════
# Indices 0-5: ground obstacles (jump over)
# Indices 6-8: overhead obstacles (slide under)
OBSTACLE_TYPES = [
    TrashCan,      # 0
    SignPost,      # 1
    TapeBarrier,   # 2
    CartHandle,    # 3
    SpeedBump,     # 4
    ElectricBike,  # 5
    TreeBranch,    # 6
    CampusBanner,  # 7
    BarrierGate,   # 8
]


def obstacle_factory(score):
    if score < 300:
        # Easy: mostly simple ground obstacles, occasional overhead
        pool = [0, 0, 0, 1, 2, 6]
    elif score < 800:
        # Medium: all types, balanced mix
        pool = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    else:
        # Hard: more overhead obstacles, more variety
        pool = [0, 1, 1, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8]
    idx = random.choice(pool)
    return OBSTACLE_TYPES[idx](WIDTH + 40)
