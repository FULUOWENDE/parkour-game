import math
import os
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
    EBIKE_BASKET,
    EBIKE_DURATION,
    EBIKE_FENDER,
    EBIKE_FRAME,
    EBIKE_HANDLE,
    EBIKE_HUB,
    EBIKE_PEDAL,
    EBIKE_SEAT,
    EBIKE_TIRE_COLOR,
    GROUND_Y,
    MIN_SPAWN_GAP,
    OUTLINE,
    OVERHEAD_BOTTOM,
    PLAYER_SKIN,
    RAIN_COLOR,
    SHADOW,
    SHIELD_DURATION,
    SIGN_ARROW,
    SIGN_BOARD,
    SIGN_POLE,
    SIGN_TEXT,
    SPEED_SLOW_DURATION,
    SPEED_SLOW_FACTOR,
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
    WEATHER_RAINY,
    WEATHER_SNOWY,
    WEATHER_STORMY,
    WIDTH,
)
from src.utils import (
    draw_circle_outlined,
    draw_ellipse_outlined,
    draw_polygon_outlined,
    draw_rounded_rect,
)

# ── Font cache for obstacle text ────────────────────────────────
_OBSTACLE_FONT_PATH = os.path.join(os.path.dirname(__file__), "resources", "fonts", "NotoSansSC-Regular.ttf")
_OBSTACLE_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "resources", "obstacles")
_FONT_CACHE = {}
_IMAGE_CACHE = {}


def _get_obs_font(size):
    if size not in _FONT_CACHE:
        try:
            _FONT_CACHE[size] = pygame.font.Font(_OBSTACLE_FONT_PATH, size)
        except Exception:
            _FONT_CACHE[size] = pygame.font.Font(None, size)
    return _FONT_CACHE[size]


def _load_obstacle_image(image_name, size):
    key = (image_name, size)
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    path = os.path.join(_OBSTACLE_IMAGE_DIR, image_name)
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.smoothscale(image, size)
    except Exception:
        image = None
    _IMAGE_CACHE[key] = image
    return image


# ── SignPost / Banner text pools ───────────────────────────────
SIGN_TEXTS = ["教学楼", "食堂", "图书馆", "宿舍楼", "实验楼"]
BANNER_TEXTS = ["四六级加油", "早八不迟到", "社团招新"]


# ── Base Obstacle ───────────────────────────────────────────────
class Obstacle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.scored = False
        self.overhead = False
        self.is_item = False  # True for collectible power-ups

    def update(self, speed):
        self.x -= speed

    def is_offscreen(self):
        return self.x + self.w < -50

    def draw(self, surface, frame=0):
        raise NotImplementedError

    def apply_effect(self, game):
        """Override in item subclasses to apply effects when picked up."""
        pass


# ═══════════════════════════════════════════════════════════════════
#  GROUND OBSTACLES  (jump over)
# ═══════════════════════════════════════════════════════════════════

# ── TrashCan (垃圾桶) ──────────────────────────────────────────
class TrashCan(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 40, 34, 40)
        # pre-render shadow
        w = self.w
        self._shadow = pygame.Surface((w + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._shadow, SHADOW, self._shadow.get_rect())

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # drop shadow
        surface.blit(self._shadow, (x - 4, GROUND_Y - 4))

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
        # pre-render text with random destination
        font = _get_obs_font(12)
        sign_text = random.choice(SIGN_TEXTS)
        self._text = font.render(sign_text, True, SIGN_TEXT)
        self._arrow = font.render("→", True, SIGN_ARROW)
        # pre-render shadow
        self._shadow = pygame.Surface((12, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(self._shadow, SHADOW, self._shadow.get_rect())

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow
        surface.blit(self._shadow, (x + w // 2 - 6, GROUND_Y - 3))

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
        # pre-render shadow
        self._shadow = pygame.Surface((self.w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._shadow, SHADOW, self._shadow.get_rect())
        # pre-render single stripe tile
        self._stripe = pygame.Surface((6, 4), pygame.SRCALPHA)
        pygame.draw.line(self._stripe, (180, 80, 0, 180), (0, 0), (6, 4), 2)

    def draw(self, surface, frame=0):
        x, y = self.x, self.y

        # shadow
        surface.blit(self._shadow, (x, GROUND_Y - 4))

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
            surface.blit(self._stripe, (sx, tape_y - 2))

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
        # pre-render shadow
        self._shadow = pygame.Surface((self.w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._shadow, SHADOW, self._shadow.get_rect())
        # pre-render steam animation frames
        self._steam_frames = []
        for i in range(8):
            steam_surf = pygame.Surface((16, 14), pygame.SRCALPHA)
            scale = 0.6 + 0.4 * math.sin(i * math.pi / 4)
            for sx, sy, sr in [(4, 10, 4), (12, 6, 3), (8, 2, 3)]:
                r = max(1, int(sr * scale))
                pygame.draw.circle(steam_surf, (255, 255, 255, 70), (sx, sy), r)
            self._steam_frames.append(steam_surf)

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow (pre-rendered)
        surface.blit(self._shadow, (x, GROUND_Y - 4))

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

        # steam animation — cycle through pre-rendered frames
        steam_idx = (frame // 6) % 8
        surface.blit(self._steam_frames[steam_idx], (x + w // 2 - 8, y - 12))


# ── SpeedBump (减速带) ─────────────────────────────────────────
class SpeedBump(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 16, 60, 16)
        # pre-render shadow
        self._shadow = pygame.Surface((self.w + 6, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._shadow, SHADOW, self._shadow.get_rect())

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow (pre-rendered)
        surface.blit(self._shadow, (x - 3, GROUND_Y - 4))

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
        # pre-render shadow
        self._shadow = pygame.Surface((self.w + 4, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self._shadow, SHADOW, self._shadow.get_rect())
        # pre-render random decoration (school bag or food delivery bag)
        self._decoration = self._render_decoration()

    def _render_decoration(self):
        """Pre-render a school bag or food delivery bag on the back seat."""
        surf = pygame.Surface((16, 14), pygame.SRCALPHA)
        if random.random() < 0.5:
            # School bag — rectangular backpack
            bag_rect = pygame.Rect(2, 2, 12, 10)
            pygame.draw.rect(surf, (30, 40, 80), bag_rect, border_radius=2)
            pygame.draw.rect(surf, OUTLINE, bag_rect, 1, border_radius=2)
            # bag straps
            pygame.draw.line(surf, (20, 30, 60), (4, 2), (4, 0), 2)
            pygame.draw.line(surf, (20, 30, 60), (10, 2), (10, 0), 2)
            # small zipper highlight
            pygame.draw.line(surf, (80, 90, 130), (4, 4), (12, 4), 1)
        else:
            # Food delivery bag — rectangular thermal bag
            bag_rect = pygame.Rect(2, 2, 12, 10)
            pygame.draw.rect(surf, (220, 130, 40), bag_rect, border_radius=2)
            pygame.draw.rect(surf, OUTLINE, bag_rect, 1, border_radius=2)
            # "外卖" label dots (simplified)
            pygame.draw.circle(surf, (255, 255, 255), (8, 5), 2)
            pygame.draw.circle(surf, (255, 255, 255), (8, 9), 2)
            # bag top tie
            pygame.draw.line(surf, (180, 100, 30), (6, 2), (6, 0), 2)
            pygame.draw.line(surf, (180, 100, 30), (10, 2), (10, 0), 2)
        return surf

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # shadow (pre-rendered)
        surface.blit(self._shadow, (x - 2, GROUND_Y - 5))

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

        # decoration on back seat (school bag / food delivery bag)
        surface.blit(self._decoration, (x + 24, y - 6))

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

    def draw(self, surface, frame=0):
        x, y = self.x, self.y  # y = OVERHEAD_BOTTOM - 28
        w = self.w
        cx = x + w // 2
        bot = OVERHEAD_BOTTOM

        # leaf sway animation (sin wave based on frame)
        sway = math.sin(frame * 0.08) * 3

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

        # foliage clusters — layered circles for depth, with sway offset
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
            fx_swayed = fx + sway
            pygame.draw.circle(surface, fc, (int(fx_swayed), int(fy)), fr)
            # mini highlight dot on each cluster
            hl_x = int(fx_swayed) - 3
            hl_y = int(fy) - 3
            pygame.draw.circle(surface, TREE_LEAF_LIGHT, (hl_x, hl_y), max(2, fr // 5))

        # small dangling branches at bottom (also sway)
        for dbx, dby in [(cx - 10, bot - 2), (cx - 2, bot + 2), (cx + 10, bot - 4)]:
            dbx_s = dbx + sway * 1.2
            pygame.draw.line(surface, TREE_TRUNK, (dbx_s, dby), (dbx_s + 3, dby + 8), 2)
            pygame.draw.circle(surface, TREE_LEAF_MID, (int(dbx_s + 3), dby + 8), 3)

        # trunk bark texture lines
        for tx in range(int(cx) - 4, int(cx) + 12, 6):
            pygame.draw.line(surface, TREE_TRUNK_DARK, (tx, bot - 30), (tx, bot - 10), 1)


# ── CampusBanner (校园宣传横幅) ─────────────────────────────────
class CampusBanner(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 30, 100, 30)
        self.overhead = True
        # random banner text
        banner_text = random.choice(BANNER_TEXTS)
        self._banner_text = _get_obs_font(14).render(banner_text, True, BANNER_TEXT)

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # fabric wave: subtle y offset based on position and frame
        wave = math.sin((x + frame * 2) * 0.03) * 2

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

        # red banner fabric with wave offset
        banner_top = y + 2 + wave
        banner_h = h - 4
        banner_rect = pygame.Rect(x + 12, int(banner_top), w - 24, banner_h)
        pygame.draw.rect(surface, BANNER_RED, banner_rect)
        # fabric folds (vertical darker lines)
        for fx in range(int(x + 24), int(x + w - 24), 14):
            fy_start = int(banner_top + 2)
            fy_end = int(banner_top + banner_h - 2)
            pygame.draw.line(surface, BANNER_RED_DARK, (fx, fy_start), (fx, fy_end), 1)
        # top edge highlight
        pygame.draw.rect(surface, BANNER_RED_LIGHT, (x + 12, int(banner_top), w - 24, 3))
        # bottom edge wave (extra fabric droop)
        bot_droop = 3 + math.sin((x + frame * 2 + 8) * 0.03) * 1
        droop_rect = pygame.Rect(x + 12, int(banner_top + banner_h - 3), w - 24, int(bot_droop))
        pygame.draw.rect(surface, BANNER_RED_DARK, droop_rect)
        # outline
        pygame.draw.rect(surface, OUTLINE, banner_rect, 1)

        # rope knots at pole connections
        for kx in [x + 8, x + w - 14]:
            pygame.draw.rect(surface, (200, 180, 100), (kx - 2, int(banner_top) + 2, 5, 6))
            pygame.draw.rect(surface, OUTLINE, (kx - 2, int(banner_top) + 2, 5, 6), 1)

        # text on banner (centered)
        tw = self._banner_text.get_width()
        tx = int(x + 12 + (w - 24 - tw) / 2)
        surface.blit(self._banner_text, (tx, int(banner_top + 5)))


# ── BarrierGate (校园道闸杆) ────────────────────────────────────
class BarrierGate(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 26, 84, 26)
        self.overhead = True

    def draw(self, surface, frame=0):
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
#  POWER-UP ITEMS  (collectible, is_item=True)
# ═══════════════════════════════════════════════════════════════════

# ── BookShield (免撞书本 — 护盾 buff) ──────────────────────────
class BookShield(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 38, 34, 30)
        self.is_item = True
        # pre-render glow surface (reuse and adjust alpha per-frame)
        self._glow_base = pygame.Surface((self.w + 14, self.h + 14), pygame.SRCALPHA)
        for r in range(6, 2, -1):
            a = 60 // (r - 1)
            pygame.draw.ellipse(self._glow_base, (255, 215, 0, a), self._glow_base.get_rect(), width=r)

    def apply_effect(self, game):
        game.player.shield_timer = SHIELD_DURATION

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # floating bobbing effect (larger amplitude)
        bob = math.sin(frame * 0.05) * 5
        by = y + bob

        # pulsing glow (copy pre-rendered base, adjust overall alpha)
        pulse = 0.5 + 0.5 * math.sin(frame * 0.08)
        glow = self._glow_base.copy()
        glow.set_alpha(int(100 + pulse * 100))
        surface.blit(glow, (x - 7, by - 7))

        # book body (larger)
        book_rect = pygame.Rect(x + 2, by + 2, w - 4, h - 4)
        pygame.draw.rect(surface, (30, 50, 130), book_rect, border_radius=3)
        pygame.draw.rect(surface, (255, 215, 0), book_rect, width=2, border_radius=3)
        # spine highlight
        pygame.draw.rect(surface, (50, 75, 165), (x + 4, by + 3, 4, h - 8), border_radius=2)
        # pages edge (white lines)
        for py in range(int(by + 6), int(by + h - 8), 5):
            pygame.draw.line(surface, (255, 255, 240), (x + 10, py), (x + w - 6, py), 1)
        # golden "shield" icon (simplified ⛊ on cover)
        scx = x + w // 2
        scy = int(by + 10)
        # shield shape
        shield_pts = [
            (scx, scy - 5),
            (scx + 5, scy - 2),
            (scx + 4, scy + 4),
            (scx, scy + 6),
            (scx - 4, scy + 4),
            (scx - 5, scy - 2),
        ]
        pygame.draw.polygon(surface, (255, 215, 0), shield_pts)
        pygame.draw.polygon(surface, OUTLINE, shield_pts, 1)


# ── SpeedBun (变速包子 — 减速 buff) ────────────────────────────
class SpeedBun(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 36, 30, 28)
        self.is_item = True
        # pre-render glow base
        self._glow_base = pygame.Surface((self.w + 14, self.h + 14), pygame.SRCALPHA)
        for r in range(6, 2, -1):
            a = 60 // (r - 1)
            pygame.draw.ellipse(self._glow_base, (100, 200, 255, a), self._glow_base.get_rect(), width=r)

    def apply_effect(self, game):
        game.player.slow_timer = SPEED_SLOW_DURATION
        game.speed_multiplier = SPEED_SLOW_FACTOR

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # floating bobbing
        bob = math.sin(frame * 0.05 + 1.5) * 5
        by = y + bob

        # blue pulsing glow
        pulse = 0.5 + 0.5 * math.sin(frame * 0.08 + 1.5)
        glow = self._glow_base.copy()
        glow.set_alpha(int(100 + pulse * 100))
        surface.blit(glow, (x - 7, by - 7))

        # bun body (white oval, larger)
        bun_rect = pygame.Rect(x + 3, by + 5, w - 6, h - 8)
        pygame.draw.ellipse(surface, (255, 245, 230), bun_rect)
        pygame.draw.ellipse(surface, OUTLINE, bun_rect, 2)
        # bun top highlight
        hl_rect = pygame.Rect(x + 8, by + 6, w - 18, 8)
        pygame.draw.ellipse(surface, (255, 252, 245), hl_rect)
        # bun fold line (vertical crease)
        pygame.draw.line(surface, (220, 210, 190), (x + w // 2, by + 7), (x + w // 2, by + h - 10), 2)
        # snowflake icon on bun
        sf_cx = x + w // 2
        sf_cy = int(by + h // 2 + 2)
        for ang in [0, math.pi / 3, 2 * math.pi / 3]:
            dx = math.cos(ang) * 5
            dy = math.sin(ang) * 5
            pygame.draw.line(surface, (100, 180, 255), (sf_cx - dx, sf_cy - dy), (sf_cx + dx, sf_cy + dy), 2)
        # steam wisps above bun (pre-rendered)
        for sx, sy, sr in [(x + w // 2 - 5, by - 4, 3), (x + w // 2 + 6, by - 7, 2), (x + w // 2, by - 10, 2)]:
            steam_alpha = int(100 + 60 * math.sin(frame * 0.12 + sx))
            steam_a = max(0, min(255, steam_alpha))
            steam_s = pygame.Surface((sr * 2 + 2, sr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(steam_s, (255, 255, 255, steam_a), (sr + 1, sr + 1), sr)
            surface.blit(steam_s, (sx - sr, sy - sr))


# ── SharedEBike (共享电动车 — 加速 buff) ──────────────────────
class SharedEBike(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 32, 50, 32)
        self.is_item = True
        # pre-render glow base
        self._glow_base = pygame.Surface((self.w + 14, self.h + 14), pygame.SRCALPHA)
        for r in range(6, 2, -1):
            a = 60 // (r - 1)
            pygame.draw.ellipse(self._glow_base, (255, 180, 30, a), self._glow_base.get_rect(), width=r)

    def apply_effect(self, game):
        game.player.ebike_timer = EBIKE_DURATION

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h
        cx = x + w // 2
        bike_y = GROUND_Y

        # floating bobbing
        bob = math.sin(frame * 0.05 + 2.5) * 4
        by = y + bob

        # Orange pulsing glow
        pulse = 0.5 + 0.5 * math.sin(frame * 0.08 + 2.5)
        glow = self._glow_base.copy()
        glow.set_alpha(int(100 + pulse * 100))
        surface.blit(glow, (x - 7, by - 7))

        # ── Shadow ──
        shadow_rect = pygame.Rect(x - 2, GROUND_Y - 2, w + 4, 6)
        pygame.draw.ellipse(surface, SHADOW, shadow_rect)

        # ── Wheels ──
        wheel_r = 8
        for wx in [x + 10, x + w - 12]:
            # Tire
            pygame.draw.circle(surface, OUTLINE, (int(wx), bike_y - wheel_r), wheel_r, 1)
            pygame.draw.circle(surface, EBIKE_TIRE_COLOR, (int(wx), bike_y - wheel_r), wheel_r - 1)
            # Hub
            pygame.draw.circle(surface, EBIKE_HUB, (int(wx), bike_y - wheel_r), 2)

        # ── Frame ──
        frame_pts = [
            (x + 10, bike_y - wheel_r),          # rear axle
            (cx + 1, bike_y - 22),               # seat top
            (x + w - 12, bike_y - wheel_r),      # front axle
            (cx + 8, bike_y - 20),               # head tube bottom
            (cx + 6, bike_y - 28),               # head tube top
        ]
        pygame.draw.polygon(surface, EBIKE_FRAME, frame_pts)
        pygame.draw.polygon(surface, OUTLINE, frame_pts, 1)

        # Frame highlight
        pygame.draw.line(surface, EBIKE_FENDER,
                         (x + 12, bike_y - wheel_r - 1),
                         (cx + 5, bike_y - 24), 1)

        # ── Fenders ──
        for fwx in [x + 10, x + w - 12]:
            fender_rect = pygame.Rect(fwx - 6, bike_y - wheel_r - 3, 12, 4)
            pygame.draw.arc(surface, EBIKE_FENDER, fender_rect, math.pi, 2 * math.pi, 1)

        # ── Chain area ──
        chain_rect = pygame.Rect(cx - 4, bike_y - 10, 10, 6)
        pygame.draw.ellipse(surface, EBIKE_PEDAL, chain_rect)
        pygame.draw.ellipse(surface, OUTLINE, chain_rect, 1)

        # ── Handlebars ──
        hb_x = cx + 8
        hb_y = bike_y - 30
        pygame.draw.line(surface, EBIKE_HANDLE, (hb_x - 2, hb_y), (hb_x + 4, hb_y), 3)
        pygame.draw.circle(surface, (40, 40, 40), (hb_x - 3, hb_y), 2)
        pygame.draw.circle(surface, (40, 40, 40), (hb_x + 5, hb_y), 2)

        # ── Basket ──
        basket_rect = pygame.Rect(x + w - 8, bike_y - 26, 10, 8)
        draw_rounded_rect(surface, basket_rect, EBIKE_BASKET, 2, outline=1)

        # ── Seat ──
        seat_rect = pygame.Rect(cx - 4, bike_y - 26, 12, 5)
        draw_rounded_rect(surface, seat_rect, EBIKE_SEAT, 3, outline=1)

        # ── Brand logo dot (small circle on frame) ──
        logo_x = int(cx + 2)
        logo_y = int(bike_y - 18)
        pygame.draw.circle(surface, (255, 255, 255), (logo_x, logo_y), 2)
        pygame.draw.circle(surface, OUTLINE, (logo_x, logo_y), 2, 1)


# ═══════════════════════════════════════════════════════════════════
#  WEATHER OBSTACLES
# ═══════════════════════════════════════════════════════════════════

# ── Raindrop (雨滴 — 雨天低空障碍物，下蹲躲避) ──────────────────
class Raindrop(Obstacle):
    def __init__(self, x=0):
        h = random.randint(18, 28)
        super().__init__(x, OVERHEAD_BOTTOM - h - random.randint(2, 20), 8, h)
        self.overhead = True  # slide under to dodge

    def update(self, speed):
        self.x -= speed
        # raindrops drift downward slowly
        self.y += 0.8

    def is_offscreen(self):
        return self.x + self.w < -50 or self.y > OVERHEAD_BOTTOM

    def draw(self, surface, frame=0):
        x, y = self.x, self.y
        w, h = self.w, self.h

        # rain streak — teardrop shape
        # top point
        streak_pts = [
            (x + w // 2, y),           # top center
            (x + w, y + h - 6),        # bottom right
            (x + w // 2, y + h),       # bottom tip
            (x, y + h - 6),            # bottom left
        ]
        rain_alpha = int(160 + 40 * math.sin(frame * 0.12 + x * 0.1))
        rain_alpha = max(100, min(255, rain_alpha))
        rain_color = (*RAIN_COLOR[:3], rain_alpha)

        drop_surf = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        shifted_pts = [(px - x + 1, py - y + 1) for px, py in streak_pts]
        pygame.draw.polygon(drop_surf, rain_color, shifted_pts)
        # highlight streak
        hl_pts = [
            (w // 2 + 1, 3),
            (w - 1, h - 5),
            (w // 2 + 1, h - 2),
        ]
        if len(hl_pts) >= 3:
            pygame.draw.polygon(drop_surf, (200, 215, 235, min(255, rain_alpha + 30)), hl_pts)
        surface.blit(drop_surf, (x, y))


class SnowClump(Obstacle):
    def __init__(self, x=0):
        size = random.randint(16, 24)
        super().__init__(x, GROUND_Y - size, size, size)
        self.roll = random.random() * math.pi * 2

    def update(self, speed):
        self.x -= speed * 0.92
        self.roll += speed * 0.04

    def draw(self, surface, frame=0):
        cx = int(self.x + self.w / 2)
        cy = int(self.y + self.h / 2 + math.sin(self.roll) * 2)
        pygame.draw.ellipse(surface, SHADOW, (self.x - 3, GROUND_Y - 5, self.w + 7, 7))
        pygame.draw.circle(surface, (236, 246, 255), (cx, cy), self.w // 2)
        pygame.draw.circle(surface, OUTLINE, (cx, cy), self.w // 2, 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 4, cy - 4), max(3, self.w // 5))


def _star_points(cx, cy, r_outer, r_inner):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    return pts


def _draw_star(surface, cx, cy, r, color):
    pts = _star_points(cx, cy, r, r * 0.48)
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.polygon(surface, OUTLINE, pts, 1)


def _draw_kawaii_face(surface, cx, cy, scale=1.0, smile=True):
    eye_r = max(2, int(4 * scale))
    for ex in (cx - int(10 * scale), cx + int(10 * scale)):
        pygame.draw.circle(surface, (92, 46, 42), (int(ex), int(cy)), eye_r + 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(ex - 1 * scale), int(cy - 2 * scale)), max(1, eye_r // 2))
    pygame.draw.circle(surface, (255, 137, 128), (int(cx - 17 * scale), int(cy + 11 * scale)), max(3, int(5 * scale)))
    pygame.draw.circle(surface, (255, 137, 128), (int(cx + 17 * scale), int(cy + 11 * scale)), max(3, int(5 * scale)))
    if smile:
        mouth = pygame.Rect(int(cx - 8 * scale), int(cy + 5 * scale), int(16 * scale), int(12 * scale))
        pygame.draw.arc(surface, (92, 46, 42), mouth, 0, math.pi, max(2, int(2 * scale)))
        pygame.draw.ellipse(surface, (255, 105, 113), mouth.inflate(-6, -5))
    else:
        pygame.draw.circle(surface, (92, 46, 42), (int(cx), int(cy + 8 * scale)), max(2, int(3 * scale)))


class ImageJumpObstacle(Obstacle):
    image_name = ""
    draw_size = (70, 54)
    collision_size = (64, 44)
    bob_amount = 2

    def __init__(self, x=0):
        cw, ch = self.collision_size
        super().__init__(x, GROUND_Y - ch, cw, ch)
        self.seed = random.random() * math.pi * 2

    def draw(self, surface, frame=0):
        bob = math.sin(frame * 0.08 + self.seed) * self.bob_amount
        image = _load_obstacle_image(self.image_name, self.draw_size)
        draw_x = self.x + (self.w - self.draw_size[0]) / 2
        draw_y = GROUND_Y - self.draw_size[1] + bob
        pygame.draw.ellipse(surface, SHADOW, (self.x - 2, GROUND_Y - 6, self.w + 5, 9))
        if image:
            surface.blit(image, (int(draw_x), int(draw_y)))
        else:
            pygame.draw.rect(surface, (255, 190, 99), (self.x, self.y, self.w, self.h), border_radius=8)
            pygame.draw.rect(surface, OUTLINE, (self.x, self.y, self.w, self.h), 2, border_radius=8)


class BookImageObstacle(ImageJumpObstacle):
    image_name = "book.png"
    draw_size = (86, 66)
    collision_size = (68, 50)
    bob_amount = 3


class SlippersImageObstacle(ImageJumpObstacle):
    image_name = "slippers.png"
    draw_size = (88, 56)
    collision_size = (76, 38)
    bob_amount = 2


class TrashImageObstacle(ImageJumpObstacle):
    image_name = "trash-bin.png"
    draw_size = (56, 74)
    collision_size = (46, 60)
    bob_amount = 2


class BaoImageObstacle(ImageJumpObstacle):
    image_name = "bao.png"
    draw_size = (58, 46)
    collision_size = (50, 34)
    bob_amount = 4


class CuteLunchBagObstacle(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, GROUND_Y - 56, 48, 56)
        self.seed = random.random() * math.pi * 2

    def draw(self, surface, frame=0):
        sway = math.sin(frame * 0.08 + self.seed) * 3
        x, y = self.x + sway, self.y
        pygame.draw.ellipse(surface, SHADOW, (x + 3, GROUND_Y - 5, 42, 8))
        bag = pygame.Rect(int(x + 4), int(y + 10), 40, 45)
        pygame.draw.rect(surface, (255, 190, 99), bag, border_radius=10)
        pygame.draw.rect(surface, (119, 72, 56), bag, 3, border_radius=10)
        pygame.draw.arc(surface, (119, 72, 56), (x + 13, y - 1, 22, 20), math.pi, math.tau, 4)
        label = pygame.Rect(int(x + 12), int(y + 27), 24, 18)
        pygame.draw.rect(surface, (255, 244, 204), label, border_radius=6)
        pygame.draw.rect(surface, (119, 72, 56), label, 2, border_radius=6)
        pygame.draw.circle(surface, (255, 129, 132), (int(x + 20), int(y + 35)), 4)
        pygame.draw.circle(surface, (128, 229, 111), (int(x + 28), int(y + 35)), 4)
        _draw_star(surface, x + 36, y + 18, 5, (255, 226, 73))


class CuteWarningTapeObstacle(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 28, 96, 28)
        self.overhead = True
        self.seed = random.random() * math.pi * 2

    def draw(self, surface, frame=0):
        x, y = self.x, self.y + math.sin(frame * 0.07 + self.seed) * 2
        for post_x in (x + 6, x + 84):
            pygame.draw.rect(surface, (255, 192, 78), (post_x, y - 20, 9, GROUND_Y - y + 20), border_radius=4)
            pygame.draw.rect(surface, OUTLINE, (post_x, y - 20, 9, GROUND_Y - y + 20), 2, border_radius=4)
        tape = pygame.Rect(int(x + 3), int(y + 4), 90, 16)
        pygame.draw.rect(surface, (255, 221, 73), tape, border_radius=8)
        pygame.draw.rect(surface, OUTLINE, tape, 2, border_radius=8)
        for sx in range(int(x + 7), int(x + 91), 16):
            pygame.draw.polygon(surface, (255, 118, 92), [(sx, y + 4), (sx + 8, y + 4), (sx + 1, y + 20), (sx - 7, y + 20)])
        _draw_star(surface, x + 47, y - 2, 6, (83, 197, 255))


class CuteTreeBranchObstacle(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 34, 110, 34)
        self.overhead = True
        self.seed = random.random() * math.pi * 2

    def draw(self, surface, frame=0):
        sway = math.sin(frame * 0.05 + self.seed) * 6
        x, y = self.x, self.y
        branch = [(x, y + 12), (x + 45, y + 18 + sway), (x + 110, y + 8)]
        pygame.draw.lines(surface, (75, 45, 32), False, branch, 12)
        pygame.draw.lines(surface, (128, 78, 45), False, branch, 8)
        for i, (lx, ly, r) in enumerate([(20, 3, 17), (42, -8, 20), (66, 3, 18), (89, -5, 15)]):
            cy = y + ly + math.sin(frame * 0.06 + i + self.seed) * 3
            pygame.draw.circle(surface, (42, 112, 58), (int(x + lx), int(cy)), r)
            pygame.draw.circle(surface, (98, 190, 90), (int(x + lx - 4), int(cy - 3)), max(5, r // 2))
            pygame.draw.circle(surface, OUTLINE, (int(x + lx), int(cy)), r, 2)


class CuteBannerObstacle(Obstacle):
    def __init__(self, x=0):
        super().__init__(x, OVERHEAD_BOTTOM - 30, 118, 30)
        self.overhead = True
        self.seed = random.random() * math.pi * 2

    def draw(self, surface, frame=0):
        wave = math.sin(frame * 0.08 + self.seed) * 3
        x, y = self.x, self.y
        rect = pygame.Rect(int(x + 7), int(y + 4 + wave), 104, 22)
        pygame.draw.rect(surface, (255, 137, 166), rect, border_radius=11)
        pygame.draw.rect(surface, OUTLINE, rect, 2, border_radius=11)
        pygame.draw.line(surface, (255, 244, 204), (x + 18, y + 15 + wave), (x + 98, y + 15 - wave), 3)
        for sx, color in [(25, (255, 226, 73)), (52, (83, 197, 255)), (78, (128, 229, 111)), (101, (255, 226, 73))]:
            _draw_star(surface, x + sx, y + 15 + math.sin(frame * 0.1 + sx) * 3, 5, color)
        for px in (x + 8, x + 107):
            pygame.draw.rect(surface, (145, 98, 76), (px, y - 36, 6, 138), border_radius=3)


# ═══════════════════════════════════════════════════════════════════
#  OBSTACLE TYPE REGISTRY & FACTORY
# ═══════════════════════════════════════════════════════════════════
OBSTACLE_TYPES = [
    CuteLunchBagObstacle,       # 0
    CuteWarningTapeObstacle,    # 1
    CuteTreeBranchObstacle,     # 2
    CuteBannerObstacle,         # 3
]


def obstacle_factory(score, weather=None, mode=0):
    """Create an obstacle based on current score, weather, and game mode.

    Args:
        score: current game score (affects difficulty pool)
        weather: current weather string (affects raindrop spawning)
        mode: game mode — 0=普通早八(normal), 1=极限冲刺(extreme), 2=悠闲逛校园(relaxed)
    """
    # ── Weather-based obstacles ──
    if weather in (WEATHER_RAINY, WEATHER_STORMY) and random.random() < 0.18:
        return Raindrop(WIDTH + random.randint(0, 200))
    if weather == WEATHER_SNOWY and random.random() < 0.16:
        return SnowClump(WIDTH + random.randint(0, 180))

    # ── Obstacle pools based on game mode ──
    if mode == 1:
        pool = [0, 1, 1, 2, 2, 3, 3]
    elif mode == 2:
        pool = [0, 0, 1, 2]
    else:
        if score < 300:
            pool = [0, 0, 0, 1, 2]
        elif score < 800:
            pool = [0, 1, 2, 3]
        else:
            pool = [0, 1, 1, 2, 2, 3, 3]
    idx = random.choice(pool)
    return OBSTACLE_TYPES[idx](WIDTH + 40)
