import math
import os
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
    SKY_CLOUDY,
    SKY_RAINY,
    SKY_SUNNY,
    WEATHER_CLOUDY,
    WEATHER_RAINY,
    WEATHER_SUNNY,
    
    WIDTH,
)


class Background:
    def __init__(self):
        bg_path = os.path.join(os.path.dirname(__file__), "resources", "江西师大背景图.jpg")
        self._bg_image = pygame.image.load(bg_path).convert()
        self._bg_image = pygame.transform.scale(self._bg_image, (WIDTH, HEIGHT))
        self._ground_surf = self._build_ground()
        # pre-render cloud overlay for cloudy weather
        self._cloud_overlay = self._build_cloud_overlay()
        # pre-render rain streak surface
        self._rain_streaks = self._build_rain_streaks()
        # pre-render rain overlay (dark tint)
        self._rain_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._rain_overlay.fill(RAIN_OVERLAY_COLOR)

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
        """Pre-render a cloudy fog overlay."""
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # scattered cloud patches
        for _ in range(18):
            cx = random.randint(0, WIDTH)
            cy = random.randint(20, 200)
            radius = random.randint(40, 100)
            alpha = random.randint(15, 35)
            for r_offset in range(random.randint(3, 6)):
                ox = cx + random.randint(-30, 30)
                oy = cy + random.randint(-10, 10)
                or_r = radius - r_offset * 15
                if or_r > 0:
                    pygame.draw.circle(surf, (180, 185, 195, alpha), (ox, oy), or_r)
        return surf

    def _build_rain_streaks(self):
        """Pre-render rain streak lines for scrolling."""
        surf = pygame.Surface((WIDTH, HEIGHT + 60), pygame.SRCALPHA)
        for _ in range(120):
            rx = random.randint(0, WIDTH)
            ry = random.randint(0, HEIGHT + 60)
            length = random.randint(8, 18)
            alpha = random.randint(60, 140)
            sx = rx - random.randint(2, 5)
            ex = rx
            sy = ry - length
            ey = ry
            color = (*RAIN_COLOR[:3], alpha)
            pygame.draw.line(surf, color, (sx, sy), (ex, ey), 1)
        return surf

    def draw(self, surface, ground_offset, weather=WEATHER_SUNNY, frame=0):
        # ── Sky ──
        if weather == WEATHER_SUNNY:
            surface.fill(SKY_SUNNY)
            surface.blit(self._bg_image, (0, 0))
        elif weather == WEATHER_CLOUDY:
            surface.fill(SKY_CLOUDY)
            surface.blit(self._bg_image, (0, 0))
            # semi-transparent cloud fog
            surface.blit(self._cloud_overlay, (0, 0))
        elif weather == WEATHER_RAINY:
            surface.fill(SKY_RAINY)
            surface.blit(self._bg_image, (0, 0))
            # darken
            surface.blit(self._rain_overlay, (0, 0))
            # scrolling rain streaks
            rain_offset = (frame * 3) % (HEIGHT + 60)
            surface.blit(self._rain_streaks, (0, rain_offset - HEIGHT - 60))
            surface.blit(self._rain_streaks, (0, rain_offset))

        # ── Ground ──
        surface.blit(self._ground_surf, (0, GROUND_Y))
        pygame.draw.line(surface, OUTLINE, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

        # scrolling road dashes
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
