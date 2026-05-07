import math
import random

import pygame

from src.constants import OUTLINE, OVERHEAD_BOTTOM


def draw_rounded_rect(surface, rect, color, radius, outline=2, outline_color=OUTLINE):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if outline > 0:
        pygame.draw.rect(surface, outline_color, rect, width=outline, border_radius=radius)


def draw_circle_outlined(surface, center, radius, fill_color, outline=2, outline_color=OUTLINE):
    pygame.draw.circle(surface, fill_color, center, radius)
    if outline > 0:
        pygame.draw.circle(surface, outline_color, center, radius, width=outline)


def draw_ellipse_outlined(surface, rect, fill_color, outline=2, outline_color=OUTLINE):
    pygame.draw.ellipse(surface, fill_color, rect)
    if outline > 0:
        pygame.draw.ellipse(surface, outline_color, rect, width=outline)


def draw_line_outlined(surface, color, start, end, width, outline_color=OUTLINE):
    pygame.draw.line(surface, outline_color, start, end, width + 2)
    pygame.draw.line(surface, color, start, end, width)


def draw_polygon_outlined(surface, color, points, outline=2, outline_color=OUTLINE):
    pygame.draw.polygon(surface, color, points)
    if outline > 0:
        pygame.draw.polygon(surface, outline_color, points, width=outline)


def check_collision(player, obstacle):
    px = player.x + 7
    py = player.y + 6
    pw = player.w - 14
    ph = player.slide_h - 8
    if obstacle.overhead:
        obs_top = 0
        obs_bottom = OVERHEAD_BOTTOM
    else:
        obs_top = obstacle.y
        obs_bottom = obstacle.y + obstacle.h
    return (
        px < obstacle.x + obstacle.w
        and px + pw > obstacle.x
        and py < obs_bottom
        and py + ph > obs_top
    )


class Particle:
    def __init__(self, x, y, vx, vy, life, decay, radius, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.decay = decay
        self.radius = radius
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.life -= self.decay

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surface):
        if not self.alive:
            return
        alpha = int(max(0, self.life * 255))
        color = (*self.color, alpha) if len(self.color) == 3 else self.color
        temp = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, color, (self.radius, self.radius), self.radius)
        surface.blit(temp, (self.x - self.radius, self.y - self.radius))


def spawn_burst(x, y, count, colors):
    particles = []
    for _ in range(count):
        angle = random.random() * math.pi * 2
        spd = 2 + random.random() * 5
        particles.append(
            Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * spd,
                vy=math.sin(angle) * spd - 1,
                life=1,
                decay=0.035 + random.random() * 0.04,
                radius=2.5 + random.random() * 4,
                color=random.choice(colors),
            )
        )
    return particles


def update_particles(particles):
    remaining = []
    for p in particles:
        p.update()
        if p.alive:
            remaining.append(p)
    return remaining


def draw_particles(surface, particles):
    for p in particles:
        p.draw(surface)
