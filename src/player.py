import math
import os

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


def _pt(point):
    return int(point[0]), int(point[1])


def _shade(color, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in color)


class Player:
    def __init__(self, char_config=None, lives=3):
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
        self.lives = lives
        self._land_squash = 0  # squash frames remaining
        # item effects
        self.shield_timer = 0   # frames of shield remaining (absorbs 1 hit)
        self.slow_timer = 0     # frames of slow effect remaining
        self.ebike_timer = 0    # frames of shared e-bike ride remaining
        self.coffee_timer = 0
        self.magnet_timer = 0
        self.dash_timer = 0
        self.invulnerable_timer = 0
        # pre-allocated surfaces for per-frame use
        self._trail_surf_cache = {}
        self._ring_surf = None
        self._sprite_cache = {}
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
        self.is_female = config.get("id") == "female"
        self.image_name = None
        self.sprite = None

    def _load_sprite(self, image_name):
        if not image_name:
            return None
        if image_name in self._sprite_cache:
            return self._sprite_cache[image_name]
        path = os.path.join(os.path.dirname(__file__), "resources", "characters", image_name)
        try:
            sprite = pygame.image.load(path).convert_alpha()
        except Exception:
            sprite = None
        self._sprite_cache[image_name] = sprite
        return sprite

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
        if self.coffee_timer > 0:
            self.coffee_timer -= 1
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

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

        if self.invulnerable_timer > 0 and frame % 8 < 4:
            return

        if self.ebike_timer > 0 and self.jumps == 0 and not self.sliding:
            self._draw_ebike(surface, x, y, w, h, cx)
        elif self.sliding:
            self._draw_sliding(surface, x, y, w, frame)
        else:
            self._draw_running(surface, x, y, w, h, cx, scale_x, scale_y, frame)

        # double-jump ring
        if self.jumps == 1:
            self._draw_jump_ring(surface, w, h)

        # shield glow
        if self.shield_timer > 0:
            self._draw_shield_glow(surface, frame)

    def _draw_sprite(self, surface, frame, sliding=False):
        if self.sprite is None:
            return False

        target_h = self.slide_h + (24 if not sliding else 18)
        target_w = int(target_h * self.sprite.get_width() / max(1, self.sprite.get_height()))
        sprite = pygame.transform.smoothscale(self.sprite, (target_w, target_h))

        if sliding:
            sprite = pygame.transform.rotate(sprite, -18)
            x = self.x - 18
            y = GROUND_Y - sprite.get_height() + 10
        else:
            bob = math.sin(self.leg_phase * 0.65) * 3 if self.jumps == 0 else 0
            x = self.x - 24
            y = self.y - 17 + bob

        if self.dash_timer > 0 or self.coffee_timer > 0:
            tint = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            tint.fill((255, 218, 80, 64))
            sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        surface.blit(sprite, (int(x), int(y)))
        return True

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

    def _draw_running(self, surface, x, y, w, h, cx, scale_x, scale_y, frame):
        phase = self.leg_phase
        stride = math.sin(phase)
        counter = math.cos(phase)
        airborne = self.jumps > 0
        bob = 0 if airborne else math.sin(phase * 2) * 2
        body_shift = math.sin(phase) * 1.5 if not airborne else 0
        foot_y = y + h + 1
        hip_y = y + h - 28 + bob
        shoulder_y = y + 30 + bob
        torso_h = 39 * scale_y
        torso_w = 28 * scale_x

        shadow_w = int((w * 0.72) * (0.78 if airborne else 1))
        shadow_rect = pygame.Rect(int(cx - shadow_w / 2), GROUND_Y - 3, shadow_w, 7)
        pygame.draw.ellipse(surface, (0, 0, 0, 42), shadow_rect)

        if self.dash_timer > 0 or self.coffee_timer > 0:
            aura = pygame.Surface((98, 118), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (255, 228, 70, 46), aura.get_rect())
            surface.blit(aura, (int(cx - 55), int(y - 20)))

        def line(color, start, end, width):
            pygame.draw.line(surface, OUTLINE, _pt(start), _pt(end), width + 3)
            pygame.draw.line(surface, color, _pt(start), _pt(end), width)

        def shoe(center, direction):
            sx, sy = center
            rect = pygame.Rect(int(sx - 13), int(sy - 5), 25, 10)
            pygame.draw.ellipse(surface, OUTLINE, rect)
            pygame.draw.ellipse(surface, self.shoe_color, rect.inflate(-3, -3))
            tip = (int(sx + direction * 10), int(sy - 1))
            pygame.draw.circle(surface, (255, 255, 255), tip, 2)

        leg_specs = [
            (-1, stride, 0.82, self.jeans_color),
            (1, -stride, 1.0, _shade(self.jeans_color, 1.08)),
        ]
        leg_specs.sort(key=lambda spec: spec[2])
        for side, swing, _, color in leg_specs:
            thigh_start = (cx + body_shift + side * 7, hip_y)
            knee = (cx + body_shift + side * 9 + swing * 9, hip_y + 18 + abs(swing) * 2)
            foot = (cx + body_shift + side * 10 + swing * 19, foot_y - max(0, swing) * 4)
            line(color, thigh_start, knee, 7)
            line(_shade(color, 1.13), knee, foot, 6)
            shoe(foot, 1)

        bag_rect = pygame.Rect(int(cx + 10), int(shoulder_y + 6), 18, 37)
        pygame.draw.rect(surface, OUTLINE, bag_rect.inflate(5, 5), border_radius=7)
        pygame.draw.rect(surface, self.bag_color, bag_rect, border_radius=6)
        pygame.draw.rect(surface, _shade(self.bag_color, 1.24), (bag_rect.x + 3, bag_rect.y + 4, bag_rect.w - 6, 6), border_radius=3)

        back_hand = (cx - 18 + counter * 13, shoulder_y + 35 - stride * 4)
        line(self.skin_color, (cx - 6, shoulder_y + 11), back_hand, 6)
        pygame.draw.circle(surface, self.skin_color, _pt(back_hand), 4)

        torso = pygame.Rect(int(cx - torso_w / 2 + body_shift), int(shoulder_y), int(torso_w), int(torso_h))
        pygame.draw.rect(surface, OUTLINE, torso.inflate(7, 7), border_radius=11)
        pygame.draw.rect(surface, self.body_color, torso, border_radius=9)
        pygame.draw.polygon(
            surface,
            (255, 248, 225),
            [
                (torso.centerx - 9, torso.y + 6),
                (torso.centerx, torso.y + 17),
                (torso.centerx + 9, torso.y + 6),
            ],
        )
        stripe = pygame.Rect(torso.x + 6, torso.y + 24, torso.w - 12, 6)
        pygame.draw.rect(surface, _shade(self.body_color, 1.25), stripe, border_radius=3)
        pygame.draw.line(surface, _shade(self.bag_color, 0.78), (torso.right - 4, torso.y + 7), (torso.right + 5, torso.y + 35), 3)

        front_hand = (cx + 17 - counter * 15, shoulder_y + 35 + stride * 4)
        line(_shade(self.skin_color, 1.03), (cx + 7, shoulder_y + 12), front_hand, 6)
        pygame.draw.circle(surface, self.skin_color, _pt(front_hand), 4)

        neck = pygame.Rect(int(cx - 4), int(shoulder_y - 2), 8, 8)
        pygame.draw.rect(surface, self.skin_color, neck, border_radius=3)

        head_c = (int(cx + 3 + body_shift), int(y + 16 + bob))
        if self.is_female:
            pony_c = (head_c[0] - 15 + int(math.sin(phase + frame * 0.02) * 4), head_c[1] - 2)
            pygame.draw.ellipse(surface, OUTLINE, (pony_c[0] - 16, pony_c[1] - 12, 24, 24))
            pygame.draw.ellipse(surface, self.hair_color, (pony_c[0] - 14, pony_c[1] - 10, 21, 21))

        pygame.draw.circle(surface, OUTLINE, head_c, 16)
        pygame.draw.circle(surface, self.skin_color, head_c, 13)
        hair_cap = pygame.Rect(head_c[0] - 13, head_c[1] - 17, 27, 18)
        pygame.draw.ellipse(surface, self.hair_color, hair_cap)
        pygame.draw.arc(surface, _shade(self.hair_color, 1.25), hair_cap.inflate(-5, -4), math.pi * 1.02, math.pi * 1.86, 2)
        if self.is_female:
            pygame.draw.circle(surface, (255, 112, 150), (head_c[0] - 9, head_c[1] - 14), 4)
        else:
            pygame.draw.polygon(
                surface,
                self.hair_color,
                [(head_c[0] - 11, head_c[1] - 5), (head_c[0] - 1, head_c[1] - 17), (head_c[0] + 7, head_c[1] - 4)],
            )

        eye_rect = pygame.Rect(head_c[0] + 4, head_c[1] - 4, 7, 7)
        pygame.draw.ellipse(surface, (255, 255, 255), eye_rect)
        pygame.draw.ellipse(surface, OUTLINE, eye_rect, 1)
        pygame.draw.circle(surface, (24, 24, 24), (head_c[0] + 8, head_c[1] - 1), 2)
        pygame.draw.circle(surface, (255, 148, 142), (head_c[0] + 5, head_c[1] + 5), 3)
        pygame.draw.arc(surface, (150, 70, 55), (head_c[0] + 2, head_c[1] + 4, 9, 7), 0, math.pi, 2)

    def _draw_sliding(self, surface, x, y, w, frame):
        slide_phase = math.sin(frame * 0.16)
        shadow_rect = pygame.Rect(int(x + 1), GROUND_Y - 3, int(w + 12), 7)
        pygame.draw.ellipse(surface, (0, 0, 0, 42), shadow_rect)

        body = pygame.Rect(int(x + 8), int(y + 12), int(w - 4), 17)
        pygame.draw.rect(surface, OUTLINE, body.inflate(6, 6), border_radius=9)
        pygame.draw.rect(surface, self.body_color, body, border_radius=8)
        pygame.draw.rect(surface, _shade(self.body_color, 1.23), (body.x + 8, body.y + 4, body.w - 20, 4), border_radius=2)

        bag = pygame.Rect(int(x + 2), int(y + 7), 17, 20)
        pygame.draw.rect(surface, OUTLINE, bag.inflate(4, 4), border_radius=6)
        pygame.draw.rect(surface, self.bag_color, bag, border_radius=5)

        hip = (x + 12, y + 25)
        knee = (x - 2, y + 29 + slide_phase * 2)
        foot = (x - 15, y + 31)
        pygame.draw.line(surface, OUTLINE, _pt(hip), _pt(knee), 8)
        pygame.draw.line(surface, self.jeans_color, _pt(hip), _pt(knee), 5)
        pygame.draw.line(surface, OUTLINE, _pt(knee), _pt(foot), 8)
        pygame.draw.line(surface, _shade(self.jeans_color, 1.12), _pt(knee), _pt(foot), 5)
        pygame.draw.ellipse(surface, OUTLINE, (int(foot[0] - 8), int(foot[1] - 4), 18, 8))
        pygame.draw.ellipse(surface, self.shoe_color, (int(foot[0] - 6), int(foot[1] - 3), 15, 6))

        arm_start = (x + w - 13, y + 19)
        arm_end = (x + w + 8, y + 23 + slide_phase * 2)
        pygame.draw.line(surface, OUTLINE, _pt(arm_start), _pt(arm_end), 7)
        pygame.draw.line(surface, self.skin_color, _pt(arm_start), _pt(arm_end), 4)
        pygame.draw.circle(surface, self.skin_color, _pt(arm_end), 4)

        head_c = (int(x + w - 1), int(y + 10))
        if self.is_female:
            pygame.draw.ellipse(surface, OUTLINE, (head_c[0] - 24, head_c[1] - 10, 22, 18))
            pygame.draw.ellipse(surface, self.hair_color, (head_c[0] - 22, head_c[1] - 8, 20, 16))
        pygame.draw.circle(surface, OUTLINE, head_c, 12)
        pygame.draw.circle(surface, self.skin_color, head_c, 10)
        pygame.draw.ellipse(surface, self.hair_color, (head_c[0] - 10, head_c[1] - 14, 22, 13))
        eye_white = pygame.Rect(head_c[0] + 3, head_c[1] - 4, 6, 6)
        pygame.draw.ellipse(surface, (255, 255, 255), eye_white)
        pygame.draw.ellipse(surface, OUTLINE, eye_white, 1)
        pygame.draw.circle(surface, (20, 20, 20), (head_c[0] + 6, head_c[1] - 1), 2)
        pygame.draw.arc(surface, (150, 70, 55), (head_c[0] + 1, head_c[1] + 3, 8, 6), 0, math.pi, 2)
