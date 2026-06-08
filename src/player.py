import math

import pygame

from src.constants import (
    CHAR_LIST,
    DB_JUMP_VEL,
    EBIKE_BASKET,
    EBIKE_DURATION,
    EBIKE_FENDER,
    EBIKE_FRAME,
    EBIKE_HANDLE,
    EBIKE_HUB,
    EBIKE_PEDAL,
    EBIKE_SEAT,
    EBIKE_TIRE_COLOR,
    GRAVITY,
    GROUND_Y,
    JUMP_VEL,
    OUTLINE,
    PLAYER_BAG,
    PLAYER_BODY,
    PLAYER_HAIR,
    PLAYER_H,
    PLAYER_JEANS,
    PLAYER_MAX_JUMPS,
    PLAYER_SHOE,
    PLAYER_SKIN,
    PLAYER_SLIDE_DURATION,
    PLAYER_SLIDE_H,
    PLAYER_W,
    PLAYER_X,
)
from src.utils import draw_circle_outlined, draw_rounded_rect, spawn_burst


class Player:
    def __init__(self, char_config=None):
        self.x = PLAYER_X
        self.w = PLAYER_W
        self.h = PLAYER_H
        self.y = GROUND_Y - self.h
        self.vy = 0
        self.jumps = 0
        self.max_jumps = PLAYER_MAX_JUMPS
        self.sliding = False
        self.slide_timer = 0
        self.leg_phase = 0
        self.trail = []
        self.dead = False
        self._land_squash = 0  # squash frames remaining
        # item effects
        self.shield_timer = 0   # frames of shield remaining (absorbs 1 hit)
        self.slow_timer = 0     # frames of slow effect remaining
        self.ebike_timer = 0    # frames of shared e-bike ride remaining
        # pre-allocated surfaces for per-frame use
        self._trail_surf_cache = {}
        self._ring_surf = None
        # apply character config
        self._apply_char_config(char_config)

    def _apply_char_config(self, config):
        """Apply character-specific colors, jump/slide/speed modifiers."""
        if config is None:
            config = CHAR_LIST[0]  # default to first character
        self.char_config = config
        # Colors
        self.body_color = config.get("color_body", PLAYER_BODY)
        self.skin_color = config.get("color_skin", PLAYER_SKIN)
        self.jeans_color = config.get("color_jeans", PLAYER_JEANS)
        self.bag_color = config.get("color_bag", PLAYER_BAG)
        self.hair_color = config.get("color_hair", PLAYER_HAIR)
        self.shoe_color = config.get("color_shoe", PLAYER_SHOE)
        # Attribute multipliers
        self.jump_mul = config.get("jump_mul", 1.0)
        self.slide_mul = config.get("slide_mul", 1.0)
        self.speed_mul = config.get("speed_mul", 1.0)

    @property
    def slide_h(self):
        return PLAYER_SLIDE_H if self.sliding else self.h

    @property
    def effective_collision_h(self):
        """Collision height adjusted by character slide_mul.

        Larger slide_mul = smaller collision area = more forgiving when sliding.
        """
        base = self.slide_h - 8
        return max(4, base / self.slide_mul)

    @property
    def top(self):
        return self.y

    @property
    def bot(self):
        return self.y + self.slide_h

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.slide_h / 2

    def jump(self, particles):
        if self.jumps < self.max_jumps:
            base_vel = JUMP_VEL if self.jumps == 0 else DB_JUMP_VEL
            self.vy = base_vel * self.jump_mul
            self.jumps += 1
            particles.extend(
                spawn_burst(self.cx, self.bot, 10, [(255, 255, 255), (255, 200, 50)])
            )

    def slide(self):
        if not self.sliding and self.bot >= GROUND_Y:
            self.sliding = True
            self.slide_timer = PLAYER_SLIDE_DURATION
            self.y = GROUND_Y - self.slide_h

    def update(self, speed, base_speed):
        # trail
        self.trail.append({"x": self.cx, "y": self.cy, "a": 1.0})
        if len(self.trail) > 9:
            self.trail.pop(0)
        for t in self.trail:
            t["a"] -= 0.11

        # squash recovery
        if self._land_squash > 0:
            self._land_squash -= 1

        # slide countdown
        if self.sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.sliding = False

        # item effect countdowns
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.slow_timer > 0:
            self.slow_timer -= 1
        if self.ebike_timer > 0:
            self.ebike_timer -= 1

        # gravity
        self.vy += GRAVITY
        self.y += self.vy

        # ground clamp
        ground_top = GROUND_Y - self.slide_h
        if self.y >= ground_top:
            was_airborne = self.y - self.vy < ground_top and self.vy > 3
            self.y = ground_top
            self.vy = 0
            self.jumps = 0
            if was_airborne:
                self._land_squash = 4

        # leg animation
        if self.jumps == 0 and not self.sliding:
            self.leg_phase += 0.22 * (speed / base_speed)

    def draw(self, surface, frame=0):
        # trail
        for t in self.trail:
            if t["a"] <= 0:
                continue
            alpha = int(max(0, t["a"]) * 100)
            tw = int(self.w * 0.4)
            th = int(self.slide_h * 0.25)
            key = (tw, th)
            if key not in self._trail_surf_cache:
                s = pygame.Surface(key, pygame.SRCALPHA)
                pygame.draw.ellipse(s, (255, 200, 100, 255), s.get_rect())
                self._trail_surf_cache[key] = s
            trail_s = self._trail_surf_cache[key].copy()
            trail_s.set_alpha(alpha)
            surface.blit(trail_s, (t["x"] - tw / 2, t["y"] - th / 2))

        x, y = self.x, self.y
        w, h = self.w, self.slide_h
        cx = self.cx

        # squash effect
        scale_y = 1.0
        if self._land_squash > 0:
            scale_y = 0.85
        scale_x = 1.0
        if self._land_squash > 0:
            scale_x = 1.08

        if self.ebike_timer > 0 and self.jumps == 0 and not self.sliding:
            self._draw_ebike(surface, x, y, w, h, cx)
        elif self.sliding:
            self._draw_sliding(surface, x, y, w)
        else:
            self._draw_running(surface, x, y, w, h, cx, scale_x, scale_y)

        # double-jump ring
        if self.jumps == 1:
            self._draw_jump_ring(surface, w, h)

        # shield glow
        if self.shield_timer > 0:
            self._draw_shield_glow(surface, frame)

    def _draw_jump_ring(self, surface, w, h):
        """Draw the double-jump indicator ring (cached)."""
        if self._ring_surf is None:
            self._ring_surf = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
        else:
            self._ring_surf.fill((0, 0, 0, 0))
        for i in range(16):
            ang = i * math.pi * 2 / 16
            if i % 2 == 0:
                start_a = ang
                end_a = ang + math.pi * 2 / 16 * 0.8
                pts = []
                for a_step in range(5):
                    a = start_a + (end_a - start_a) * a_step / 4
                    px_val = w + math.cos(a) * w * 0.78
                    py_val = h + math.sin(a) * h * 0.78
                    pts.append((px_val, py_val))
                if len(pts) >= 2:
                    pygame.draw.lines(self._ring_surf, (255, 200, 50, 120), False, pts, 2)
        surface.blit(self._ring_surf, (self.cx - w, self.cy - h))

    def _draw_shield_glow(self, surface, frame):
        """Draw golden shield glow around player."""
        pulse = 0.7 + 0.3 * math.sin(frame * 0.15)
        alpha = int(pulse * 140)
        radius = int(max(self.w, self.slide_h) * 1.1)
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # outer glow ring
        for r_offset in range(3):
            a = alpha // (r_offset + 2)
            pygame.draw.circle(
                glow,
                (255, 215, 0, max(0, a)),
                (radius, radius),
                radius - r_offset * 2,
                width=2,
            )
        surface.blit(glow, (self.cx - radius, self.cy - radius))

    def _draw_ebike(self, surface, x, y, w, h, cx):
        """Draw the player riding a shared e-bike."""
        foot_y = GROUND_Y
        bike_y = foot_y

        # ── Bike shadow ──
        shadow_rect = pygame.Rect(x - 4, bike_y - 2, w + 30, 6)
        pygame.draw.ellipse(surface, (0, 0, 0, 40), shadow_rect)

        # ── Wheels ──
        wheel_radius = 12
        front_wx = int(cx + 16)
        rear_wx = int(cx - 14)
        wheel_cy = bike_y - wheel_radius

        # Pedaling rotation
        pedal_angle = self.leg_phase * 1.8  # faster rotation for riding

        for wx in [rear_wx, front_wx]:
            # Tire
            pygame.draw.circle(surface, OUTLINE, (wx, wheel_cy), wheel_radius, 2)
            pygame.draw.circle(surface, EBIKE_TIRE_COLOR, (wx, wheel_cy), wheel_radius - 1)
            # Hub
            pygame.draw.circle(surface, EBIKE_HUB, (wx, wheel_cy), 4)
            pygame.draw.circle(surface, OUTLINE, (wx, wheel_cy), 4, 1)
            # Spokes
            for ang in range(0, 360, 60):
                rad = math.radians(ang + pedal_angle * 30)
                sp_x = wx + math.cos(rad) * (wheel_radius - 3)
                sp_y = wheel_cy + math.sin(rad) * (wheel_radius - 3)
                pygame.draw.line(surface, (140, 140, 150), (wx, wheel_cy), (int(sp_x), int(sp_y)), 1)

        # ── Bike frame (blue shared-bike style) ──
        # Main frame: diamond shape
        frame_pts = [
            (rear_wx, wheel_cy),               # rear axle
            (cx + 2, wheel_cy - 14),           # seat post top
            (front_wx, wheel_cy),              # front axle
            (cx + 10, wheel_cy - 16),          # head tube bottom
            (cx + 8, wheel_cy - 28),           # head tube top
            (cx - 2, wheel_cy - 14),           # seat post bottom
        ]
        pygame.draw.polygon(surface, EBIKE_FRAME, frame_pts)
        pygame.draw.polygon(surface, OUTLINE, frame_pts, 1)

        # Crossbar highlight
        pygame.draw.line(surface, EBIKE_FENDER, (rear_wx + 2, wheel_cy - 2), (cx + 6, wheel_cy - 24), 2)

        # ── Fenders ──
        for fwx, fw_dir in [(rear_wx, -1), (front_wx, 1)]:
            fender_rect = pygame.Rect(fwx - 9, wheel_cy - wheel_radius - 2, 18, 6)
            pygame.draw.arc(surface, EBIKE_FENDER, fender_rect, math.pi, 2 * math.pi, 2)

        # ── Chain / pedal area ──
        chain_rect = pygame.Rect(cx - 6, wheel_cy - 6, 12, 8)
        pygame.draw.ellipse(surface, EBIKE_PEDAL, chain_rect)
        pygame.draw.ellipse(surface, OUTLINE, chain_rect, 1)

        # ── Handlebars ──
        hb_x = cx + 10
        hb_y = wheel_cy - 28
        pygame.draw.line(surface, EBIKE_HANDLE, (hb_x - 2, hb_y), (hb_x + 4, hb_y), 4)
        # Grips
        pygame.draw.circle(surface, (40, 40, 40), (hb_x - 4, hb_y), 2)
        pygame.draw.circle(surface, (40, 40, 40), (hb_x + 6, hb_y), 2)

        # ── Basket (front) ──
        basket_rect = pygame.Rect(front_wx + 4, wheel_cy - 20, 10, 10)
        draw_rounded_rect(surface, basket_rect, EBIKE_BASKET, 2, outline=1)
        # Basket grid lines
        for gx in range(basket_rect.x + 3, basket_rect.x + 9, 3):
            pygame.draw.line(surface, (140, 140, 150), (gx, basket_rect.y), (gx, basket_rect.y + 10), 1)

        # ── Seat ──
        seat_rect = pygame.Rect(cx - 5, wheel_cy - 20, 14, 6)
        draw_rounded_rect(surface, seat_rect, EBIKE_SEAT, 3, outline=1)

        # ── Player riding (seated, upper body only) ──
        seat_top = wheel_cy - 20
        body_h = h - 22  # shorter body when seated

        # Player body (seated, slight forward lean)
        body_rect = pygame.Rect(x + 3, seat_top - body_h + 8, w - 6, body_h)
        draw_rounded_rect(surface, body_rect, self.body_color, 6, outline=0)

        # Arms reaching to handlebars
        for ax_sign, ax_base in [(-1, 0), (1, 0)]:
            arm_start_x = cx + ax_sign * 2
            arm_start_y = seat_top - body_h + 14
            arm_end_x = hb_x + ax_sign * 3
            arm_end_y = hb_y + 2
            pygame.draw.line(surface, OUTLINE, (arm_start_x, arm_start_y), (arm_end_x, arm_end_y), 4)
            pygame.draw.line(surface, self.body_color, (arm_start_x, arm_start_y), (arm_end_x, arm_end_y), 2)

        # Head
        head_cx = cx + 2
        head_cy = seat_top - body_h + 2
        hair_rect = pygame.Rect(head_cx - 9, head_cy - 12, 18, 13)
        draw_rounded_rect(surface, hair_rect, self.hair_color, 4, outline=0)
        draw_circle_outlined(surface, (head_cx, head_cy), 10, self.skin_color, outline=0)
        # Eye looking forward
        eye_white = pygame.Rect(head_cx + 3, head_cy - 3, 6, 6)
        pygame.draw.ellipse(surface, (255, 255, 255), eye_white)
        pygame.draw.ellipse(surface, OUTLINE, eye_white, 1)
        pygame.draw.circle(surface, (20, 20, 20), (head_cx + 6, head_cy - 1), 2)

        # Speed lines / wind effect while riding
        if self.ebike_timer > 0:
            for si in range(3):
                lx = x - 8 - si * 6
                ly = int(head_cy - 4 + math.sin(self.leg_phase * 2 + si) * 3)
                alpha = int(120 + 60 * math.sin(self.leg_phase * 3 + si))
                wind = pygame.Surface((10, 1), pygame.SRCALPHA)
                wind.fill((255, 255, 255, alpha))
                surface.blit(wind, (lx, ly))

    def _draw_running(self, surface, x, y, w, h, cx, scale_x, scale_y):
        leg_swing = math.sin(self.leg_phase) * 14
        foot_y = y + h + 2

        # shadow
        shadow_rect = pygame.Rect(cx - w * 0.3, GROUND_Y - 2, w * 0.6, 5)
        pygame.draw.ellipse(surface, (0, 0, 0, 40), shadow_rect)

        # legs (jeans) — draw through to feet
        left_foot_x = cx - 5 + leg_swing
        right_foot_x = cx + 5 - leg_swing
        # back leg
        pygame.draw.line(surface, OUTLINE, (cx - 5, foot_y - 18), (left_foot_x, foot_y + 16), 7)
        pygame.draw.line(surface, self.jeans_color, (cx - 5, foot_y - 18), (left_foot_x, foot_y + 16), 5)
        # shoes
        pygame.draw.ellipse(surface, OUTLINE, (left_foot_x - 6, foot_y + 12, 12, 8))
        pygame.draw.ellipse(surface, self.shoe_color, (left_foot_x - 5, foot_y + 13, 10, 6))
        # front leg
        pygame.draw.line(surface, OUTLINE, (cx + 5, foot_y - 18), (right_foot_x, foot_y + 16), 7)
        pygame.draw.line(surface, self.jeans_color, (cx + 5, foot_y - 18), (right_foot_x, foot_y + 16), 5)
        pygame.draw.ellipse(surface, OUTLINE, (right_foot_x - 6, foot_y + 12, 12, 8))
        pygame.draw.ellipse(surface, self.shoe_color, (right_foot_x - 5, foot_y + 13, 10, 6))

        # backpack (behind body)
        bag_rect = pygame.Rect(x + w - 4, y + 18, 10, h - 30)
        draw_rounded_rect(surface, bag_rect, self.bag_color, 3)

        # body (jacket)
        body_rect = pygame.Rect(x + 3, y + 20, w - 6, h - 34)
        draw_rounded_rect(surface, body_rect, self.body_color, 7)

        # arms
        arm_phase = self.leg_phase + math.pi
        arm_swing = math.cos(arm_phase) * 9
        # back arm
        pygame.draw.line(surface, OUTLINE, (cx - 2, y + 28), (cx - 2 + arm_swing, y + 45), 6)
        pygame.draw.line(surface, self.body_color, (cx - 2, y + 28), (cx - 2 + arm_swing, y + 45), 4)
        # front arm
        front_swing = math.cos(arm_phase + math.pi) * 9
        pygame.draw.line(surface, OUTLINE, (cx + 2, y + 28), (cx + 2 + front_swing, y + 45), 6)
        pygame.draw.line(surface, self.body_color, (cx + 2, y + 28), (cx + 2 + front_swing, y + 45), 4)

        # head
        head_cx = int(cx)
        head_cy = int(y + 13)
        # hair (behind head)
        hair_rect = pygame.Rect(head_cx - 10, head_cy - 16, 20, 16)
        draw_rounded_rect(surface, hair_rect, self.hair_color, 5)
        # head
        draw_circle_outlined(surface, (head_cx, head_cy), 12, self.skin_color)
        # eye
        eye_white = pygame.Rect(head_cx + 4, head_cy - 4, 8, 8)
        pygame.draw.ellipse(surface, (255, 255, 255), eye_white)
        pygame.draw.ellipse(surface, OUTLINE, eye_white, 1)
        pygame.draw.circle(surface, (20, 20, 20), (head_cx + 8, head_cy - 1), 3)

    def _draw_sliding(self, surface, x, y, w):
        # shadow
        shadow_rect = pygame.Rect(x + 2, GROUND_Y - 2, w, 5)
        pygame.draw.ellipse(surface, (0, 0, 0, 40), shadow_rect)

        # body horizontal
        body_rect = pygame.Rect(x + 6, y + 12, w - 12, 14)
        draw_rounded_rect(surface, body_rect, self.body_color, 6)
        # backpack
        bag_rect = pygame.Rect(x + w - 6, y + 8, 8, 20)
        draw_rounded_rect(surface, bag_rect, self.bag_color, 3)
        # head at front (right side)
        head_cx = int(x + w - 10)
        head_cy = int(y + 8)
        draw_circle_outlined(surface, (head_cx, head_cy), 9, self.skin_color)
        # eye
        eye_white = pygame.Rect(head_cx + 3, head_cy - 3, 6, 6)
        pygame.draw.ellipse(surface, (255, 255, 255), eye_white)
        pygame.draw.ellipse(surface, OUTLINE, eye_white, 1)
        pygame.draw.circle(surface, (20, 20, 20), (head_cx + 5, head_cy - 1), 2)
        # hair
        hair_rect = pygame.Rect(head_cx - 8, head_cy - 12, 16, 12)
        draw_rounded_rect(surface, hair_rect, self.hair_color, 4)
        # legs extended left
        pygame.draw.line(surface, OUTLINE, (x + 4, y + 18), (x - 4, y + 22), 6)
        pygame.draw.line(surface, self.jeans_color, (x + 4, y + 18), (x - 4, y + 22), 4)
