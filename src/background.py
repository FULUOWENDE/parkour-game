import os
import math
import random

import pygame

from src.constants import (
    GROUND_DARK,
    GROUND_H,
    GROUND_LIGHT,
    GROUND_Y,
    HEIGHT,
    OUTLINE,
    RAIN_COLOR,
    RAIN_OVERLAY_COLOR,
    SNOW_COLOR,
    SNOW_OVERLAY_COLOR,
    STORM_OVERLAY_COLOR,
    WEATHER_CLOUDY,
    WEATHER_RAINY,
    WEATHER_SNOWY,
    WEATHER_STORMY,
    WEATHER_SUNNY,
    WIDTH,
)

TAU = 6.283185307179586


class Background:
    def __init__(self):
        self.images = self._load_backgrounds()
        self.sequence = [0, self._random_next_index(0)]
        self.offset = 0.0
        self._last_ground_offset = 0.0
        self._ground_surf = self._build_ground()
        self._cloud_overlay = self._build_cloud_overlay()
        self._dark_cloud_overlay = self._build_dark_cloud_overlay()
        self._rain_streaks = self._build_rain_streaks()
        self._snowflakes = self._build_snowflakes()
        self._rain_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._rain_overlay.fill(RAIN_OVERLAY_COLOR)
        self._snow_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._snow_overlay.fill(SNOW_OVERLAY_COLOR)
        self._storm_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._storm_overlay.fill(STORM_OVERLAY_COLOR)

    def _load_backgrounds(self):
        base = os.path.join(os.path.dirname(__file__), "resources")
        paths = [
            os.path.join(base, "江西师大背景图.jpg"),
            os.path.join(base, "backgrounds", "campus-gate.png"),
            os.path.join(base, "backgrounds", "campus-square.png"),
            os.path.join(base, "backgrounds", "library-sun.png"),
            os.path.join(base, "backgrounds", "library-snow.png"),
        ]
        images = []
        for path in paths:
            if not os.path.exists(path):
                continue
            raw = pygame.image.load(path).convert()
            images.append(self._fit_background(raw))
        if not images:
            fallback = pygame.Surface((WIDTH, HEIGHT))
            fallback.fill((135, 206, 235))
            images.append(fallback)
        return images

    def _fit_background(self, image):
        iw, ih = image.get_size()
        scale = max(WIDTH / iw, HEIGHT / ih)
        scaled = pygame.transform.smoothscale(image, (int(iw * scale), int(ih * scale)))
        crop = pygame.Surface((WIDTH, HEIGHT))
        x = (WIDTH - scaled.get_width()) // 2
        y = (HEIGHT - scaled.get_height()) // 2
        crop.blit(scaled, (x, y))
        return crop

    def _random_next_index(self, current):
        if len(self.images) <= 1:
            return 0
        choices = [i for i in range(len(self.images)) if i != current]
        return random.choice(choices)

    def _advance_sequence(self):
        self.sequence.pop(0)
        self.sequence.append(self._random_next_index(self.sequence[-1]))

    def _build_ground(self):
        surf = pygame.Surface((WIDTH, GROUND_H))
        for y in range(GROUND_H):
            t = y / GROUND_H
            r = int(GROUND_LIGHT[0] + (GROUND_DARK[0] - GROUND_LIGHT[0]) * t)
            g = int(GROUND_LIGHT[1] + (GROUND_DARK[1] - GROUND_LIGHT[1]) * t)
            b = int(GROUND_LIGHT[2] + (GROUND_DARK[2] - GROUND_LIGHT[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        return surf

    def _build_cloud_overlay(self):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for _ in range(24):
            cx = random.randint(0, WIDTH)
            cy = random.randint(18, 185)
            radius = random.randint(44, 118)
            alpha = random.randint(42, 78)
            for r_offset in range(random.randint(3, 6)):
                ox = cx + random.randint(-30, 30)
                oy = cy + random.randint(-10, 10)
                rr = radius - r_offset * 15
                if rr > 0:
                    pygame.draw.circle(surf, (112, 122, 142, alpha), (ox, oy), rr)
        return surf

    def _build_dark_cloud_overlay(self):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for _ in range(32):
            cx = random.randint(-70, WIDTH + 70)
            cy = random.randint(8, 178)
            radius = random.randint(58, 140)
            alpha = random.randint(72, 118)
            for r_offset in range(random.randint(4, 8)):
                ox = cx + random.randint(-46, 46)
                oy = cy + random.randint(-16, 16)
                rr = radius - r_offset * 16
                if rr > 0:
                    pygame.draw.circle(surf, (50, 58, 78, alpha), (ox, oy), rr)
        return surf

    def _build_rain_streaks(self):
        surf = pygame.Surface((WIDTH, HEIGHT + 60), pygame.SRCALPHA)
        for _ in range(170):
            rx = random.randint(0, WIDTH)
            ry = random.randint(0, HEIGHT + 60)
            length = random.randint(11, 24)
            alpha = random.randint(75, 165)
            color = (*RAIN_COLOR[:3], alpha)
            pygame.draw.line(surf, color, (rx - random.randint(2, 5), ry - length), (rx, ry), 1)
        return surf

    def _build_snowflakes(self):
        flakes = []
        for _ in range(135):
            flakes.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT + 80),
                "r": random.randint(2, 5),
                "speed": random.uniform(0.7, 1.8),
                "drift": random.uniform(0.6, 2.2),
                "phase": random.random() * TAU,
            })
        return flakes

    def draw(self, surface, ground_offset, weather=WEATHER_SUNNY, frame=0):
        delta = ground_offset - self._last_ground_offset
        self._last_ground_offset = ground_offset
        self.offset += max(0, delta) * 0.32
        while self.offset >= WIDTH:
            self.offset -= WIDTH
            self._advance_sequence()

        x0 = -int(self.offset)
        surface.blit(self.images[self.sequence[0]], (x0, 0))
        surface.blit(self.images[self.sequence[1]], (x0 + WIDTH, 0))

        if weather == WEATHER_CLOUDY:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((36, 42, 58, 76))
            surface.blit(dim, (0, 0))
            surface.blit(self._cloud_overlay, (0, 0))
        elif weather in (WEATHER_RAINY, WEATHER_STORMY):
            if weather == WEATHER_STORMY:
                surface.blit(self._storm_overlay, (0, 0))
                surface.blit(self._dark_cloud_overlay, (0, 0))
                self._draw_lightning(surface, frame)
            else:
                surface.blit(self._rain_overlay, (0, 0))
                surface.blit(self._dark_cloud_overlay, (0, 0))
            rain_offset = (frame * 3) % (HEIGHT + 60)
            surface.blit(self._rain_streaks, (0, rain_offset - HEIGHT - 60))
            surface.blit(self._rain_streaks, (0, rain_offset))
        elif weather == WEATHER_SNOWY:
            surface.blit(self._snow_overlay, (0, 0))
            surface.blit(self._cloud_overlay, (0, 0))
            self._draw_snow(surface, frame)

        surface.blit(self._ground_surf, (0, GROUND_Y))
        pygame.draw.line(surface, OUTLINE, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

        dash_w = 40
        gap_w = 20
        dash_y = GROUND_Y + 30
        total_w = dash_w + gap_w
        start_x = -(ground_offset % total_w)
        x = start_x
        while x < WIDTH + total_w:
            if x + dash_w > 0 and x < WIDTH:
                dash_rect = pygame.Rect(max(x, 0), dash_y, min(x + dash_w, WIDTH) - max(x, 0), 4)
                pygame.draw.rect(surface, (220, 220, 200), dash_rect)
            x += total_w

    def _draw_snow(self, surface, frame):
        for flake in self._snowflakes:
            x = (flake["x"] + math.sin(frame * 0.018 + flake["phase"]) * flake["drift"] * 12) % WIDTH
            y = (flake["y"] + frame * flake["speed"]) % (HEIGHT + 80) - 40
            color = (*SNOW_COLOR[:3], max(90, min(230, int(SNOW_COLOR[3] - flake["r"] * 8))))
            pygame.draw.circle(surface, color, (int(x), int(y)), flake["r"])

    def _draw_lightning(self, surface, frame):
        if frame % 170 not in (0, 1, 2, 3, 4):
            return
        flash_alpha = 120 if frame % 170 < 2 else 62
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash.fill((210, 226, 255, flash_alpha))
        surface.blit(flash, (0, 0))
        start_x = 620 + int(math.sin(frame * 0.31) * 180)
        points = [(start_x, 18)]
        x, y = start_x, 18
        for _ in range(6):
            x += random.randint(-34, 28)
            y += random.randint(25, 52)
            points.append((x, y))
        pygame.draw.lines(surface, (255, 247, 160), False, points, 7)
        pygame.draw.lines(surface, (255, 255, 255), False, points, 3)
