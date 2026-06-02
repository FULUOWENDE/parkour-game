"""NPC pedestrians — pure visual decoration (no collision).

Types:
  - RushingStudent  : 狂奔赶课同学 (fast, leaning forward, backpack bouncing)
  - StrollingTeacher: 慢悠悠散步老师 (slow, upright, dignified)
  - CampusCouple    : 牵手情侣 (two figures side-by-side, holding hands)
  - CleaningLady    : 扫地保洁阿姨 (with broom, apron, slow)

All NPCs walk on the ground plane and scroll left with the map.
"""

import math
import random

import pygame

from src.constants import GROUND_Y, OUTLINE, WIDTH
from src.utils import draw_circle_outlined, draw_rounded_rect

# ── NPC palette ───────────────────────────────────────────────────
# Rushing student
STUDENT_BODY = (70, 130, 220)        # blue jacket
STUDENT_SKIN = (255, 220, 180)
STUDENT_HAIR = (25, 20, 18)
STUDENT_JEANS = (40, 60, 140)
STUDENT_BAG = (200, 60, 40)          # red backpack
STUDENT_SHOE = (40, 40, 40)

# Strolling teacher
TEACHER_BODY = (140, 110, 80)        # brown blazer
TEACHER_SKIN = (255, 215, 170)
TEACHER_HAIR = (80, 80, 80)          # grey hair
TEACHER_PANTS = (50, 50, 60)         # dark trousers
TEACHER_SHOE = (30, 30, 30)
TEACHER_MUG = (220, 220, 240)        # coffee mug

# Couple
COUPLE_LEFT_BODY = (220, 130, 150)   # pink/red jacket
COUPLE_RIGHT_BODY = (80, 140, 200)   # blue jacket
COUPLE_SKIN = (255, 218, 175)
COUPLE_HAIR_DARK = (25, 20, 20)
COUPLE_HAIR_LONG = (50, 30, 25)      # long dark hair
COUPLE_JEANS = (55, 65, 130)
COUPLE_SHOE = (45, 45, 45)

# Cleaning lady
CLEANER_BODY = (180, 160, 130)       # beige uniform
CLEANER_SKIN = (255, 210, 165)
CLEANER_HAIR = (40, 35, 30)
CLEANER_APRON = (100, 160, 100)      # green apron
CLEANER_PANTS = (60, 60, 70)
CLEANER_SHOE = (35, 35, 35)
CLEANER_BROOM_STICK = (180, 150, 110)
CLEANER_BROOM_HEAD = (140, 100, 50)


# ═══════════════════════════════════════════════════════════════════
#  BASE NPC
# ═══════════════════════════════════════════════════════════════════

class NPC:
    """Base class for all decorative pedestrians."""

    def __init__(self, x, y, w, h, speed_ratio=1.0):
        self.x = x
        self.y = y          # top of figure
        self.w = w
        self.h = h
        self.speed_ratio = speed_ratio  # 1.0 = match map speed; <1 = slower
        self._sway_offset = random.random() * math.pi * 2  # random phase

    def update(self, map_speed):
        self.x -= map_speed * self.speed_ratio

    def is_offscreen(self):
        return self.x + self.w < -80

    @property
    def ground_y(self):
        """Bottom of NPC = ground line."""
        return GROUND_Y

    def draw(self, surface, frame):
        raise NotImplementedError


# ═══════════════════════════════════════════════════════════════════
#  狂奔赶课同学
# ═══════════════════════════════════════════════════════════════════

class RushingStudent(NPC):
    """Student sprinting to class — leaning forward, backpack bouncing."""

    def __init__(self, x):
        w, h = 28, 50
        super().__init__(x, GROUND_Y - h, w, h, speed_ratio=0.82)
        # Random book color under arm
        self._book_color = random.choice([
            (180, 50, 50), (50, 100, 180), (50, 150, 80), (200, 140, 40)
        ])

    def draw(self, surface, frame):
        x, y = self.x, self.y
        w, h = self.w, self.h
        cx = x + w // 2

        # Running bob — more intense sprint motion
        bounce = math.sin(frame * 0.25 + self._sway_offset) * 3
        lean = 3  # lean forward (drawn as body offset)

        foot_y = self.ground_y

        # Shadow
        shadow_rect = pygame.Rect(x + 2, foot_y - 2, w - 4, 4)
        pygame.draw.ellipse(surface, (0, 0, 0, 30), shadow_rect)

        # Sprinting legs — wider stride
        sprint_phase = frame * 0.3 + self._sway_offset
        leg_swing = math.sin(sprint_phase) * 10
        # Back leg
        lfx = cx - 4 + leg_swing
        rfx = cx + 4 - leg_swing

        # Back leg (dark)
        pygame.draw.line(surface, OUTLINE,
                         (cx - 3, foot_y - 16), (lfx, foot_y + 2), 5)
        pygame.draw.line(surface, STUDENT_JEANS,
                         (cx - 3, foot_y - 16), (lfx, foot_y + 2), 3)
        # Front leg
        pygame.draw.line(surface, OUTLINE,
                         (cx + 3, foot_y - 16), (rfx, foot_y + 2), 5)
        pygame.draw.line(surface, STUDENT_JEANS,
                         (cx + 3, foot_y - 16), (rfx, foot_y + 2), 3)
        # Shoes
        for shx in [lfx, rfx]:
            pygame.draw.ellipse(surface, OUTLINE, (shx - 4, foot_y, 8, 5))
            pygame.draw.ellipse(surface, STUDENT_SHOE, (shx - 3, foot_y + 1, 6, 3))

        # Backpack (bouncing more vigorously)
        bag_bob = bounce * 1.3
        bag_rect = pygame.Rect(x + w - 5, y + int(12 + bag_bob), 8, h - 24)
        draw_rounded_rect(surface, bag_rect, STUDENT_BAG, 2, outline=0)

        # Body (leaning forward)
        body_rect = pygame.Rect(x + 3 + lean, y + int(14 + bounce), w - 8, h - 26)
        draw_rounded_rect(surface, body_rect, STUDENT_BODY, 5, outline=0)

        # Pumping arms
        arm_swing = math.cos(sprint_phase) * 8
        # Back arm
        pygame.draw.line(surface, OUTLINE,
                         (cx - 2 + lean, int(y + 20 + bounce)),
                         (cx - 2 + arm_swing + lean, int(y + 32 + bounce)), 4)
        pygame.draw.line(surface, STUDENT_BODY,
                         (cx - 2 + lean, int(y + 20 + bounce)),
                         (cx - 2 + arm_swing + lean, int(y + 32 + bounce)), 2)
        # Front arm
        pygame.draw.line(surface, OUTLINE,
                         (cx + 2 + lean, int(y + 20 + bounce)),
                         (cx + 2 - arm_swing + lean, int(y + 32 + bounce)), 4)
        pygame.draw.line(surface, STUDENT_BODY,
                         (cx + 2 + lean, int(y + 20 + bounce)),
                         (cx + 2 - arm_swing + lean, int(y + 32 + bounce)), 2)

        # Book under front arm
        book_x = int(cx + 4 - arm_swing + lean)
        book_y = int(y + 28 + bounce)
        book_rect = pygame.Rect(book_x - 5, book_y - 2, 7, 10)
        pygame.draw.rect(surface, self._book_color, book_rect, border_radius=1)
        pygame.draw.rect(surface, OUTLINE, book_rect, width=1, border_radius=1)

        # Head
        head_cx = int(cx + lean)
        head_cy = int(y + 8 + bounce)
        # Hair
        hair_rect = pygame.Rect(head_cx - 8, head_cy - 11, 16, 12)
        draw_rounded_rect(surface, hair_rect, STUDENT_HAIR, 4, outline=0)
        # Face
        draw_circle_outlined(surface, (head_cx, head_cy), 9, STUDENT_SKIN, outline=0)
        # Sweat drops (running hard!)
        if int(frame * 0.15 + self._sway_offset) % 3 == 0:
            for sx, sy in [(head_cx + 7, head_cy - 3), (head_cx + 9, head_cy + 2)]:
                pygame.draw.circle(surface, (150, 210, 255),
                                   (sx, sy), 2)


# ═══════════════════════════════════════════════════════════════════
#  慢悠悠散步老师
# ═══════════════════════════════════════════════════════════════════

class StrollingTeacher(NPC):
    """Teacher taking a leisurely stroll — slow, dignified gait."""

    def __init__(self, x):
        w, h = 30, 54
        super().__init__(x, GROUND_Y - h, w, h, speed_ratio=0.38)
        self._has_glasses = random.random() < 0.6
        self._has_mug = random.random() < 0.5

    def draw(self, surface, frame):
        x, y = self.x, self.y
        w, h = self.w, self.h
        cx = x + w // 2
        foot_y = self.ground_y

        # Gentle walking bob
        bounce = math.sin(frame * 0.10 + self._sway_offset) * 1.5

        # Shadow
        shadow_rect = pygame.Rect(x + 3, foot_y - 2, w - 6, 4)
        pygame.draw.ellipse(surface, (0, 0, 0, 25), shadow_rect)

        # Slow walking legs — narrow stride
        walk_phase = frame * 0.10 + self._sway_offset
        leg_swing = math.sin(walk_phase) * 5
        lfx = cx - 3 + leg_swing
        rfx = cx + 3 - leg_swing

        for leg_x, lx_off in [(lfx, -3), (rfx, 3)]:
            pygame.draw.line(surface, OUTLINE,
                             (cx + lx_off, foot_y - 18), (leg_x, foot_y + 2), 5)
            pygame.draw.line(surface, TEACHER_PANTS,
                             (cx + lx_off, foot_y - 18), (leg_x, foot_y + 2), 3)
            # Shoes
            pygame.draw.ellipse(surface, OUTLINE, (leg_x - 4, foot_y, 8, 5))
            pygame.draw.ellipse(surface, TEACHER_SHOE, (leg_x - 3, foot_y + 1, 6, 3))

        # Body (blazer — upright posture, no lean)
        body_rect = pygame.Rect(x + 3, int(y + 16 + bounce), w - 6, h - 28)
        draw_rounded_rect(surface, body_rect, TEACHER_BODY, 5, outline=0)

        # Blazer lapels (subtle V-neck detail)
        lapel_pts = [
            (cx, int(y + 30 + bounce)),
            (cx - 4, int(y + 20 + bounce)),
            (cx + 4, int(y + 20 + bounce)),
        ]
        pygame.draw.polygon(surface, (255, 255, 240), lapel_pts)

        # Arms — gentle swing
        arm_swing = math.cos(walk_phase) * 4
        for ax_sign in [-1, 1]:
            ax = cx + ax_sign * 3
            pygame.draw.line(surface, OUTLINE,
                             (ax, int(y + 22 + bounce)),
                             (ax + arm_swing * ax_sign, int(y + 34 + bounce)), 4)
            pygame.draw.line(surface, TEACHER_BODY,
                             (ax, int(y + 22 + bounce)),
                             (ax + arm_swing * ax_sign, int(y + 34 + bounce)), 2)

        # Coffee mug in one hand
        if self._has_mug:
            mug_x = int(cx + 4 + arm_swing)
            mug_y = int(y + 32 + bounce)
            mug_rect = pygame.Rect(mug_x - 3, mug_y - 4, 6, 8)
            pygame.draw.rect(surface, TEACHER_MUG, mug_rect, border_radius=2)
            pygame.draw.rect(surface, OUTLINE, mug_rect, width=1, border_radius=2)
            # Steam
            for sx, sy, sr in [(mug_x - 2, mug_y - 7, 2), (mug_x + 2, mug_y - 9, 1)]:
                alpha = int(80 + 60 * math.sin(frame * 0.14 + sx))
                steam_s = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(steam_s, (255, 255, 255, alpha), (3, 3), sr)
                surface.blit(steam_s, (sx - 3, sy - 3))

        # Head
        head_cx = cx
        head_cy = int(y + 9 + bounce)
        # Hair (grey, receding hairline — higher forehead)
        hair_rect = pygame.Rect(head_cx - 9, head_cy - 10, 18, 12)
        draw_rounded_rect(surface, hair_rect, TEACHER_HAIR, 4, outline=0)
        # Bald top highlight
        pygame.draw.ellipse(surface, TEACHER_SKIN, (head_cx - 6, head_cy - 12, 12, 6))

        # Face
        draw_circle_outlined(surface, (head_cx, head_cy), 10, TEACHER_SKIN, outline=0)

        # Glasses
        if self._has_glasses:
            # Wireframe glasses
            glass_color = (60, 60, 60)
            pygame.draw.circle(surface, glass_color, (head_cx + 3, head_cy - 1), 5, width=1)
            pygame.draw.circle(surface, glass_color, (head_cx - 3, head_cy - 1), 5, width=1)
            pygame.draw.line(surface, glass_color,
                             (head_cx - 8, head_cy - 1), (head_cx + 8, head_cy - 1), 1)

        # Gentle smile
        smile_arc = pygame.Rect(head_cx - 3, head_cy + 1, 6, 3)
        pygame.draw.arc(surface, (60, 40, 30), smile_arc, 0.2, math.pi - 0.2, 1)


# ═══════════════════════════════════════════════════════════════════
#  牵手情侣
# ═══════════════════════════════════════════════════════════════════

class CampusCouple(NPC):
    """A couple walking hand-in-hand across campus."""

    def __init__(self, x):
        w, h = 58, 50  # wider to fit two people
        super().__init__(x, GROUND_Y - h, w, h, speed_ratio=0.42)
        # Random heart above sometimes
        self._show_heart = random.random() < 0.4

    def draw(self, surface, frame):
        x, y = self.x, self.y
        w, h = self.w, self.h
        foot_y = self.ground_y

        # Gentle couple bounce (synchronised)
        bounce = math.sin(frame * 0.09 + self._sway_offset) * 1.5

        # Shadow (wide, covers both)
        shadow_rect = pygame.Rect(x + 4, foot_y - 2, w - 8, 5)
        pygame.draw.ellipse(surface, (0, 0, 0, 25), shadow_rect)

        walk_phase = frame * 0.09 + self._sway_offset
        leg_swing = math.sin(walk_phase) * 4

        # ── Left person (girl — pink jacket, long hair, skirt) ──
        l_cx = x + 14

        # Legs
        lfx = l_cx - 2 + leg_swing
        rfx = l_cx + 2 - leg_swing
        for leg_x in [lfx, rfx]:
            pygame.draw.line(surface, OUTLINE,
                             (l_cx, foot_y - 16), (leg_x, foot_y + 2), 4)
            pygame.draw.line(surface, COUPLE_JEANS,
                             (l_cx, foot_y - 16), (leg_x, foot_y + 2), 2)
            pygame.draw.ellipse(surface, OUTLINE, (leg_x - 3, foot_y, 6, 4))
            pygame.draw.ellipse(surface, COUPLE_SHOE, (leg_x - 2, foot_y + 1, 4, 3))

        # Body (pink)
        l_body = pygame.Rect(l_cx - 7, int(y + 14 + bounce), 14, h - 26)
        draw_rounded_rect(surface, l_body, COUPLE_LEFT_BODY, 4, outline=0)

        # Skirt (slightly flared below)
        skirt_pts = [
            (l_cx - 8, int(y + h - 16)),
            (l_cx + 8, int(y + h - 16)),
            (l_cx + 10, int(y + h - 6)),
            (l_cx - 10, int(y + h - 6)),
        ]
        pygame.draw.polygon(surface, (180, 100, 130), skirt_pts)
        pygame.draw.polygon(surface, OUTLINE, skirt_pts, 1)

        # Head
        l_head = (l_cx, int(y + 7 + bounce))
        # Long hair behind
        long_hair = pygame.Rect(l_cx - 10, int(y + 1 + bounce), 20, 18)
        draw_rounded_rect(surface, long_hair, COUPLE_HAIR_LONG, 5, outline=0)
        draw_circle_outlined(surface, l_head, 8, COUPLE_SKIN, outline=0)

        # ── Right person (boy — blue jacket, dark hair) ──
        r_cx = x + 44

        # Legs
        lfx_r = r_cx - 2 + leg_swing
        rfx_r = r_cx + 2 - leg_swing
        for leg_x in [lfx_r, rfx_r]:
            pygame.draw.line(surface, OUTLINE,
                             (r_cx, foot_y - 16), (leg_x, foot_y + 2), 4)
            pygame.draw.line(surface, COUPLE_JEANS,
                             (r_cx, foot_y - 16), (leg_x, foot_y + 2), 2)
            pygame.draw.ellipse(surface, OUTLINE, (leg_x - 3, foot_y, 6, 4))
            pygame.draw.ellipse(surface, COUPLE_SHOE, (leg_x - 2, foot_y + 1, 4, 3))

        # Body (blue)
        r_body = pygame.Rect(r_cx - 7, int(y + 14 + bounce), 14, h - 26)
        draw_rounded_rect(surface, r_body, COUPLE_RIGHT_BODY, 4, outline=0)

        # Head
        r_head = (r_cx, int(y + 7 + bounce))
        hair_rect = pygame.Rect(r_cx - 9, int(y + 1 + bounce), 18, 11)
        draw_rounded_rect(surface, hair_rect, COUPLE_HAIR_DARK, 4, outline=0)
        draw_circle_outlined(surface, r_head, 8, COUPLE_SKIN, outline=0)

        # ── Joined hands (between them) ──
        hand_y = int(y + 24 + bounce)
        # Left person's right arm extending right
        pygame.draw.line(surface, COUPLE_LEFT_BODY,
                         (l_cx + 6, hand_y - 2), (l_cx + 14, hand_y), 2)
        # Right person's left arm extending left
        pygame.draw.line(surface, COUPLE_RIGHT_BODY,
                         (r_cx - 6, hand_y - 2), (r_cx - 14, hand_y), 2)
        # Joined hands (small circle in middle)
        join_x = (l_cx + r_cx) // 2
        pygame.draw.circle(surface, COUPLE_SKIN, (join_x, hand_y), 3)
        pygame.draw.circle(surface, OUTLINE, (join_x, hand_y), 3, width=1)

        # ── Floating heart ──
        if self._show_heart:
            heart_x = join_x
            heart_y = int(y - 4 + bounce + math.sin(frame * 0.055) * 4)
            heart_alpha = int(140 + 60 * math.sin(frame * 0.07))
            heart_alpha = max(80, min(255, heart_alpha))
            _draw_tiny_heart(surface, heart_x, heart_y, heart_alpha)


def _draw_tiny_heart(surface, cx, cy, alpha):
    """Draw a tiny pixel heart (4x4 approximation)."""
    heart_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
    color = (255, 80, 120, alpha)
    # Two dots on top row
    heart_surf.set_at((3, 1), color)
    heart_surf.set_at((6, 1), color)
    # Middle rows
    for px in range(2, 8):
        heart_surf.set_at((px, 2), color)
    for px in range(2, 8):
        heart_surf.set_at((px, 3), color)
    for px in range(2, 8):
        heart_surf.set_at((px, 4), color)
    # Bottom rows (taper to point)
    for px in range(3, 7):
        heart_surf.set_at((px, 5), color)
    for px in range(4, 6):
        heart_surf.set_at((px, 6), color)
    heart_surf.set_at((5, 7), color)
    surface.blit(heart_surf, (cx - 5, cy - 5))


# ═══════════════════════════════════════════════════════════════════
#  扫地保洁阿姨
# ═══════════════════════════════════════════════════════════════════

class CleaningLady(NPC):
    """Campus cleaning auntie with a broom, sweeping slowly."""

    def __init__(self, x):
        w, h = 32, 48
        super().__init__(x, GROUND_Y - h, w, h, speed_ratio=0.28)
        self._broom_phase = random.random() * math.pi * 2

    def draw(self, surface, frame):
        x, y = self.x, self.y
        w, h = self.w, self.h
        cx = x + w // 2
        foot_y = self.ground_y

        # Slow, steady pace — minimal bounce
        bounce = math.sin(frame * 0.07 + self._sway_offset) * 1

        # Shadow
        shadow_rect = pygame.Rect(x + 3, foot_y - 2, w - 6, 4)
        pygame.draw.ellipse(surface, (0, 0, 0, 22), shadow_rect)

        # Slow walking legs
        walk_phase = frame * 0.07 + self._sway_offset
        leg_swing = math.sin(walk_phase) * 4
        lfx = cx - 3 + leg_swing
        rfx = cx + 3 - leg_swing

        for leg_x, lx_off in [(lfx, -3), (rfx, 3)]:
            pygame.draw.line(surface, OUTLINE,
                             (cx + lx_off, foot_y - 16), (leg_x, foot_y + 2), 4)
            pygame.draw.line(surface, CLEANER_PANTS,
                             (cx + lx_off, foot_y - 16), (leg_x, foot_y + 2), 2)
            pygame.draw.ellipse(surface, OUTLINE, (leg_x - 3, foot_y, 6, 4))
            pygame.draw.ellipse(surface, CLEANER_SHOE, (leg_x - 2, foot_y + 1, 4, 3))

        # Body (uniform)
        body_rect = pygame.Rect(x + 3, int(y + 12 + bounce), w - 6, h - 24)
        draw_rounded_rect(surface, body_rect, CLEANER_BODY, 4, outline=0)

        # Apron overlay
        apron_rect = pygame.Rect(x + 5, int(y + 16 + bounce), w - 10, h - 30)
        draw_rounded_rect(surface, apron_rect, CLEANER_APRON, 2, outline=0)
        # Apron strings (horizontal line)
        apron_tie_y = int(y + 18 + bounce)
        pygame.draw.line(surface, (80, 140, 80), (x + 4, apron_tie_y), (x + w - 4, apron_tie_y), 1)

        # Arms — gentle sweeping motion
        arm_swing = math.cos(walk_phase) * 3
        # Left arm (holding broom)
        pygame.draw.line(surface, OUTLINE,
                         (cx - 4, int(y + 18 + bounce)),
                         (cx - 8 + arm_swing, int(y + 30 + bounce)), 4)
        pygame.draw.line(surface, CLEANER_BODY,
                         (cx - 4, int(y + 18 + bounce)),
                         (cx - 8 + arm_swing, int(y + 30 + bounce)), 2)
        # Right arm
        pygame.draw.line(surface, OUTLINE,
                         (cx + 4, int(y + 18 + bounce)),
                         (cx + 8 - arm_swing, int(y + 28 + bounce)), 4)
        pygame.draw.line(surface, CLEANER_BODY,
                         (cx + 4, int(y + 18 + bounce)),
                         (cx + 8 - arm_swing, int(y + 28 + bounce)), 2)

        # Broom (held in left hand, sweeping ground)
        broom_angle = math.sin(frame * 0.09 + self._broom_phase) * 0.15
        broom_top_x = cx - 8 + arm_swing
        broom_top_y = int(y + 30 + bounce)
        broom_bot_x = broom_top_x + int(math.sin(broom_angle) * 40)
        broom_bot_y = foot_y + 4

        # Broom stick
        pygame.draw.line(surface, CLEANER_BROOM_STICK,
                         (broom_top_x, broom_top_y),
                         (broom_bot_x + 10, broom_bot_y - 20), 2)
        # Broom head (bristles at ground)
        broom_head_pts = [
            (broom_bot_x - 6, broom_bot_y - 6),
            (broom_bot_x + 10, broom_bot_y - 8),
            (broom_bot_x + 12, broom_bot_y - 2),
            (broom_bot_x - 4, broom_bot_y),
        ]
        pygame.draw.polygon(surface, CLEANER_BROOM_HEAD, broom_head_pts)
        pygame.draw.polygon(surface, OUTLINE, broom_head_pts, 1)

        # Dust particles near broom head
        if int(frame * 0.2) % 3 == 0:
            for dx, dy in [(3, -8), (8, -10), (12, -5)]:
                dust_a = random.randint(30, 80)
                dust = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(dust, (180, 170, 150, dust_a), (2, 2), 1)
                surface.blit(dust, (broom_bot_x + dx, broom_bot_y + dy))

        # Head
        head_cx = cx
        head_cy = int(y + 6 + bounce)
        # Hair (tied back/up bun)
        hair_rect = pygame.Rect(head_cx - 8, head_cy - 12, 16, 14)
        draw_rounded_rect(surface, hair_rect, CLEANER_HAIR, 5, outline=0)
        # Hair bun on top
        pygame.draw.circle(surface, CLEANER_HAIR, (head_cx, head_cy - 12), 4)
        draw_circle_outlined(surface, (head_cx, head_cy), 9, CLEANER_SKIN, outline=0)

        # Kind smile
        smile_rect = pygame.Rect(head_cx - 3, head_cy + 2, 6, 3)
        pygame.draw.arc(surface, (60, 35, 25), smile_rect, 0.2, math.pi - 0.2, 1)


# ═══════════════════════════════════════════════════════════════════
#  NPC TYPE REGISTRY & FACTORY
# ═══════════════════════════════════════════════════════════════════

NPC_TYPES = [
    RushingStudent,     # 0: 狂奔赶课同学
    StrollingTeacher,   # 1: 慢悠悠散步老师
    CampusCouple,       # 2: 牵手情侣
    CleaningLady,       # 3: 扫地保洁阿姨
]

# Weights for random selection (student most common)
NPC_WEIGHTS = [0.35, 0.22, 0.18, 0.25]


def npc_factory():
    """Create a random NPC at the right edge of the screen.

    Returns:
        An NPC instance positioned off the right edge, ready to scroll in.
    """
    npc_class = random.choices(NPC_TYPES, weights=NPC_WEIGHTS, k=1)[0]
    # Spawn off-screen to the right with some random stagger
    spawn_x = WIDTH + random.randint(20, 300)
    return npc_class(spawn_x)
