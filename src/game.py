import math
import random

import pygame

from src.background import Background
from src.constants import (
    BASE_SPAWN_GAP,
    BASE_SPEED,
    DEAD,
    FPS,
    HEIGHT,
    MIN_SPAWN_GAP,
    PLAYING,
    SCORE_RATE,
    SPAWN_GAP_DECAY,
    SPEED_CAP,
    SPEED_RAMP,
    SPEED_SLOW_FACTOR,
    START,
    WEATHER_CLOUDY,
    WEATHER_CLOUDY_SCORE,
    WEATHER_RAINY,
    WEATHER_RAINY_SCORE,
    WEATHER_SUNNY,
    WIDTH,
)
from src.obstacles import obstacle_factory
from src.player import Player
from src.ui import UI
from src.utils import check_collision, draw_particles, spawn_burst, update_particles


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.state = START
        self.score = 0
        self.speed = BASE_SPEED
        self.frame = 0
        self.ground_offset = 0
        self.spawn_timer = 0
        self.speed_multiplier = 1.0  # modified by SpeedBun item
        self.weather = WEATHER_SUNNY

        self.background = Background()
        self.player = Player()
        self.ui = UI()
        self.obstacles = []
        self.particles = []

        self.running = True

    @property
    def effective_speed(self):
        return self.speed * self.speed_multiplier

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.state == PLAYING:
                        self.player.jump(self.particles)
                    else:
                        self.start_game()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.state == PLAYING:
                        self.player.slide()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state != PLAYING:
                    self.start_game()
                else:
                    if event.pos[1] < HEIGHT * 0.55:
                        self.player.jump(self.particles)
                    else:
                        self.player.slide()

        return self.running

    def start_game(self):
        self.state = PLAYING
        self.score = 0
        self.speed = BASE_SPEED
        self.frame = 0
        self.ground_offset = 0
        self.spawn_timer = 0
        self.speed_multiplier = 1.0
        self.weather = WEATHER_SUNNY
        self.obstacles = []
        self.particles = []
        self.player = Player()

    def kill_player(self):
        self.state = DEAD
        self.particles.extend(
            spawn_burst(
                self.player.cx, self.player.cy, 28,
                [(255, 60, 60), (255, 140, 30), (255, 255, 255), (255, 200, 50), (255, 182, 182)],
            )
        )
        self.ui.check_high_score(self.score)

    def update(self):
        if self.state != PLAYING:
            return

        self.frame += 1
        self.score += self.effective_speed * SCORE_RATE

        # speed ramp
        self.speed = min(BASE_SPEED + math.floor(self.score / SPEED_RAMP) * 0.5, SPEED_CAP)

        # reset speed multiplier when slow timer expires
        if self.player.slow_timer <= 0 and self.speed_multiplier < 1.0:
            self.speed_multiplier = 1.0

        self.ground_offset += self.effective_speed

        # weather transition
        if self.score < WEATHER_CLOUDY_SCORE:
            self.weather = WEATHER_SUNNY
        elif self.score < WEATHER_RAINY_SCORE:
            self.weather = WEATHER_CLOUDY
        else:
            self.weather = WEATHER_RAINY

        # spawn obstacles
        self.spawn_timer += 1
        spawn_gap = max(MIN_SPAWN_GAP, BASE_SPAWN_GAP - math.floor(self.score / SPAWN_GAP_DECAY) * 5)
        # slightly faster spawn when rainy for raindrops
        if self.weather == WEATHER_RAINY:
            spawn_gap = max(MIN_SPAWN_GAP - 8, spawn_gap - 5)
        if self.spawn_timer >= spawn_gap + random.random() * 28:
            self.obstacles.append(obstacle_factory(self.score, self.weather))
            self.spawn_timer = 0

        # update obstacles
        for o in self.obstacles:
            o.update(self.effective_speed)
        self.obstacles = [o for o in self.obstacles if not o.is_offscreen()]

        # update player
        self.player.update(self.effective_speed, BASE_SPEED)

        # collision detection
        for o in self.obstacles:
            if check_collision(self.player, o):
                if o.is_item:
                    # pickup item — apply its effect
                    o.apply_effect(self)
                    o.scored = True  # mark for removal
                elif self.player.shield_timer > 0:
                    # shield absorbs hit — consume shield, remove obstacle
                    self.player.shield_timer = 0
                    self.particles.extend(
                        spawn_burst(o.x + o.w // 2, o.y + o.h // 2, 12,
                                    [(255, 215, 0), (255, 255, 200), (255, 180, 0)])
                    )
                    o.scored = True  # mark obstacle for removal
                else:
                    self.kill_player()
                    return

        # remove scored obstacles (items and shield-destroyed obstacles)
        self.obstacles = [o for o in self.obstacles if not o.scored]

        # particles
        self.particles = update_particles(self.particles)

    def draw(self):
        # sky color based on weather
        self.background.draw(self.screen, self.ground_offset, self.weather, self.frame)

        # obstacles
        for o in self.obstacles:
            o.draw(self.screen, self.frame)

        # player
        if self.state != DEAD:
            self.player.draw(self.screen, self.frame)

        # particles
        draw_particles(self.screen, self.particles)

        # UI overlays
        if self.state == PLAYING:
            self.ui.draw_hud(self.screen, self.score, self.speed * self.speed_multiplier, self.player)
        elif self.state == START:
            self.ui.draw_start_screen(self.screen, self.frame)
        elif self.state == DEAD:
            new_record = self.ui.high_score == int(self.score) and int(self.score) > 0
            self.ui.draw_game_over_screen(self.screen, self.frame, self.score, new_record)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.running = self.handle_events()
            if not self.running:
                break
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def cleanup(self):
        self.ui.save_high_score()
