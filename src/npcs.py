"""Decorative campus ambience.

These objects are visual only. They fly in the sky or hover far from the main
running lane, so players will not mistake them for obstacles.
"""

import math
import random

import pygame

from src.constants import HEIGHT, OUTLINE, WIDTH


class Ambient:
    def __init__(self, x, y, w, h, speed_ratio=0.45):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed_ratio = speed_ratio
        self.seed = random.random() * math.pi * 2

    def update(self, map_speed):
        self.x -= map_speed * self.speed_ratio

    def is_offscreen(self):
        return self.x + self.w < -100

    def draw(self, surface, frame):
        raise NotImplementedError


class FlyingBird(Ambient):
    def __init__(self, x):
        y = random.randint(64, 190)
        super().__init__(x, y, 34, 18, speed_ratio=random.uniform(0.18, 0.34))
        self.color = random.choice([(48, 66, 90), (72, 82, 102), (36, 49, 70)])
        self.scale = random.uniform(0.8, 1.25)

    def draw(self, surface, frame):
        flap = math.sin(frame * 0.18 + self.seed)
        x = int(self.x)
        y = int(self.y + math.sin(frame * 0.025 + self.seed) * 7)
        body = (x + int(14 * self.scale), y + int(7 * self.scale))
        wing_span = int((13 + flap * 5) * self.scale)
        wing_lift = int((5 + abs(flap) * 8) * self.scale)

        pygame.draw.ellipse(surface, self.color, (x + 8, y + 4, int(16 * self.scale), int(9 * self.scale)))
        pygame.draw.line(surface, OUTLINE, body, (body[0] - wing_span, body[1] - wing_lift), 3)
        pygame.draw.line(surface, self.color, body, (body[0] - wing_span, body[1] - wing_lift), 2)
        pygame.draw.line(surface, OUTLINE, body, (body[0] + wing_span, body[1] - wing_lift), 3)
        pygame.draw.line(surface, self.color, body, (body[0] + wing_span, body[1] - wing_lift), 2)
        pygame.draw.polygon(surface, (242, 180, 69), [(x + 24, y + 7), (x + 31, y + 5), (x + 25, y + 10)])


class PaperPlane(Ambient):
    def __init__(self, x):
        y = random.randint(95, 245)
        super().__init__(x, y, 38, 22, speed_ratio=random.uniform(0.25, 0.42))
        self.tint = random.choice([(255, 255, 255), (245, 252, 255), (255, 249, 231)])

    def update(self, map_speed):
        self.x -= map_speed * self.speed_ratio
        self.y += math.sin(self.x * 0.012 + self.seed) * 0.18

    def draw(self, surface, frame):
        x = int(self.x)
        y = int(self.y + math.sin(frame * 0.04 + self.seed) * 5)
        points = [(x, y + 10), (x + 38, y), (x + 26, y + 19)]
        fold = [(x + 13, y + 10), (x + 38, y), (x + 21, y + 13)]
        pygame.draw.polygon(surface, OUTLINE, points, width=2)
        pygame.draw.polygon(surface, self.tint, points)
        pygame.draw.polygon(surface, (214, 232, 245), fold)
        pygame.draw.line(surface, (150, 174, 190), (x + 13, y + 10), (x + 26, y + 19), 1)


class Butterfly(Ambient):
    def __init__(self, x):
        y = random.randint(250, min(345, HEIGHT - 150))
        super().__init__(x, y, 26, 22, speed_ratio=random.uniform(0.12, 0.24))
        self.left = random.choice([(255, 112, 150), (255, 194, 78), (128, 229, 111)])
        self.right = random.choice([(83, 197, 255), (255, 218, 91), (176, 132, 255)])

    def update(self, map_speed):
        self.x -= map_speed * self.speed_ratio
        self.y += math.sin(self.x * 0.02 + self.seed) * 0.45

    def draw(self, surface, frame):
        flap = abs(math.sin(frame * 0.22 + self.seed))
        x = int(self.x)
        y = int(self.y)
        wing_h = int(7 + flap * 8)
        pygame.draw.ellipse(surface, OUTLINE, (x, y - wing_h, 12, wing_h * 2), 1)
        pygame.draw.ellipse(surface, OUTLINE, (x + 12, y - wing_h, 12, wing_h * 2), 1)
        pygame.draw.ellipse(surface, self.left, (x + 1, y - wing_h + 1, 10, wing_h * 2 - 2))
        pygame.draw.ellipse(surface, self.right, (x + 13, y - wing_h + 1, 10, wing_h * 2 - 2))
        pygame.draw.line(surface, (58, 45, 40), (x + 12, y - 8), (x + 12, y + 8), 2)


AMBIENT_TYPES = [FlyingBird, FlyingBird, PaperPlane, Butterfly]


def npc_factory():
    ambient_class = random.choice(AMBIENT_TYPES)
    spawn_x = WIDTH + random.randint(30, 340)
    return ambient_class(spawn_x)
