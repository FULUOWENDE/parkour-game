import math
import random

import pygame

from src.background import Background
from src.constants import (
    BASE_SPAWN_GAP,
    BASE_SPEED,
    CHAR_LIST,
    DEAD,
    EBIKE_SPEED_FACTOR,
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
from src.npcs import npc_factory
from src.ui import UI
from src.utils import check_collision, draw_particles, spawn_burst, update_particles


class Game:
    def __init__(self, screen, sound_manager=None):
        self.screen = screen
        self.sound = sound_manager  # SoundManager instance (can be None)
        self.state = START
        self.score = 0
        self.speed = BASE_SPEED
        self.frame = 0
        self.ground_offset = 0
        self.spawn_timer = 0
        self.speed_multiplier = 1.0  # modified by SpeedBun item
        self.weather = WEATHER_SUNNY
        self._weather_flash = 0      # frames remaining for weather transition flash

        self.background = Background()
        self.player = Player()
        self.ui = UI()
        self.obstacles = []
        self.particles = []
        self.npcs = []

        # Character & mode selection
        self.char_idx = 0
        self.mode = 0
        self._char_speed_mul = 1.0
        self._mode_spawn_gap_mul = 1.0

    @property
    def effective_speed(self):
        boost = self.speed_multiplier
        if self.player.ebike_timer > 0:
            boost *= EBIKE_SPEED_FACTOR
        return self.speed * boost * self._char_speed_mul

    def handle_event(self, event):
        """Handle a single pygame event. Returns False if the app should quit."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.state == PLAYING:
                    self.player.jump(self.particles)
                    if self.sound:
                        self.sound.play_jump()
                elif self.state == START:
                    self._begin_play()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.state == PLAYING:
                    self.player.slide()
                    if self.sound:
                        self.sound.play_slide()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == START:
                self._begin_play()
            elif self.state == PLAYING:
                if event.pos[1] < HEIGHT * 0.55:
                    self.player.jump(self.particles)
                    if self.sound:
                        self.sound.play_jump()
                else:
                    self.player.slide()
                    if self.sound:
                        self.sound.play_slide()

        return True

    def start_game(self, char_idx=0, mode=0, immediate=False):
        """Reset and start/restart the game.

        Args:
            char_idx: index into CHAR_LIST for character selection
            mode: 0=普通早八, 1=极限冲刺, 2=悠闲逛校园
            immediate: if True, jump straight to PLAYING; else show START screen
        """
        self.char_idx = char_idx
        self.mode = mode

        # Apply character config
        char_config = CHAR_LIST[char_idx] if char_idx < len(CHAR_LIST) else CHAR_LIST[0]
        self._char_speed_mul = char_config.get("speed_mul", 1.0)

        # Apply mode-based spawn gap modifier
        if mode == 1:
            self._mode_spawn_gap_mul = 0.8   # 极限冲刺: 20% shorter gaps
        elif mode == 2:
            self._mode_spawn_gap_mul = 1.5   # 悠闲逛校园: 50% longer gaps
        else:
            self._mode_spawn_gap_mul = 1.0

        self.state = PLAYING if immediate else START
        self.score = 0
        self.speed = BASE_SPEED
        self.frame = 0
        self.ground_offset = 0
        self.spawn_timer = 0
        self.speed_multiplier = 1.0
        self.weather = WEATHER_SUNNY
        self._weather_flash = 0
        self.obstacles = []
        self.particles = []
        self.npcs = []
        self.player = Player(char_config)

    def _begin_play(self):
        """Transition from START to PLAYING (called on first jump/click)."""
        self.state = PLAYING

    def kill_player(self):
        self.state = DEAD
        self.particles.extend(
            spawn_burst(
                self.player.cx, self.player.cy, 28,
                [(255, 60, 60), (255, 140, 30), (255, 255, 255), (255, 200, 50), (255, 182, 182)],
            )
        )
        self.ui.check_high_score(self.score)
        if self.sound:
            self.sound.play_death()

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

        # weather transition (with flash notification on change)
        prev_weather = self.weather
        if self.score < WEATHER_CLOUDY_SCORE:
            self.weather = WEATHER_SUNNY
        elif self.score < WEATHER_RAINY_SCORE:
            self.weather = WEATHER_CLOUDY
        else:
            self.weather = WEATHER_RAINY
        if self.weather != prev_weather:
            self._weather_flash = 60  # 1 sec flash notification
            if self.sound:
                if self.weather == WEATHER_RAINY:
                    self.sound.play_rain_start()
                    self.sound.switch_bgm("tension")
                elif self.weather == WEATHER_CLOUDY:
                    self.sound.switch_bgm("early")

        # spawn obstacles
        self.spawn_timer += 1
        spawn_gap = max(MIN_SPAWN_GAP, BASE_SPAWN_GAP - math.floor(self.score / SPAWN_GAP_DECAY) * 5)
        # apply mode-based spawn gap multiplier
        spawn_gap = int(spawn_gap * self._mode_spawn_gap_mul)
        spawn_gap = max(MIN_SPAWN_GAP, spawn_gap)
        # slightly faster spawn when rainy for raindrops
        if self.weather == WEATHER_RAINY:
            spawn_gap = max(MIN_SPAWN_GAP - 8, spawn_gap - 5)
        if self.spawn_timer >= spawn_gap + random.random() * 28:
            self.obstacles.append(obstacle_factory(self.score, self.weather, self.mode))
            self.spawn_timer = 0

        # spawn NPCs (decorative pedestrians, less frequent than obstacles)
        if random.random() < 0.008:  # ~0.5 NPC per second at 60fps
            self.npcs.append(npc_factory())

        # update obstacles
        for o in self.obstacles:
            o.update(self.effective_speed)
        self.obstacles = [o for o in self.obstacles if not o.is_offscreen()]

        # update NPCs
        for n in self.npcs:
            n.update(self.effective_speed)
        self.npcs = [n for n in self.npcs if not n.is_offscreen()]

        # update player
        self.player.update(self.effective_speed, BASE_SPEED)

        # collision detection
        for o in self.obstacles:
            if check_collision(self.player, o):
                if o.is_item:
                    # pickup item — apply its effect + particle burst
                    o.apply_effect(self)
                    o.scored = True  # mark for removal
                    if self.sound:
                        self.sound.play_item(type(o).__name__)
                    self.particles.extend(
                        spawn_burst(o.x + o.w // 2, o.y + o.h // 2, 15,
                                    [(255, 255, 255), (255, 255, 200), (255, 200, 50),
                                     (255, 215, 0), (255, 240, 150)])
                    )
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

    def draw_scene(self):
        """Draw the game world: background, obstacles, player, particles, weather fx."""
        # sky color based on weather
        self.background.draw(self.screen, self.ground_offset, self.weather, self.frame)

        # NPC pedestrians (behind obstacles, decorative only)
        for n in self.npcs:
            n.draw(self.screen, self.frame)

        # obstacles
        for o in self.obstacles:
            o.draw(self.screen, self.frame)

        # player
        if self.state != DEAD:
            self.player.draw(self.screen, self.frame)

        # particles
        draw_particles(self.screen, self.particles)

        # weather transition flash
        if self._weather_flash > 0:
            self._weather_flash -= 1
            alpha = int(min(80, self._weather_flash * 1.5))
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            if self.weather == WEATHER_CLOUDY:
                flash.fill((180, 185, 195, alpha))
            elif self.weather == WEATHER_RAINY:
                flash.fill((100, 120, 150, alpha))
            self.screen.blit(flash, (0, 0))
            # weather label
            label = None
            if self.weather == WEATHER_CLOUDY:
                label = self.ui.font_md.render("☁ 阴天来了...", True, (220, 220, 230))
            elif self.weather == WEATHER_RAINY:
                label = self.ui.font_md.render("🌧 下雨了！下蹲躲避雨滴", True, (180, 200, 230))
            if label:
                lw = label.get_width()
                self.screen.blit(label, (WIDTH // 2 - lw // 2, HEIGHT // 2 - 40))

    def draw_overlay(self):
        """Draw UI overlays: HUD, start screen, or game-over screen."""
        if self.state == PLAYING:
            self.ui.draw_hud(self.screen, self.score, self.speed * self.speed_multiplier, self.player, self.weather)
        elif self.state == START:
            self.ui.draw_start_screen(self.screen, self.frame)
        elif self.state == DEAD:
            new_record = self.ui.high_score == int(self.score) and int(self.score) > 0
            self.ui.draw_game_over_screen(self.screen, self.frame, self.score, new_record)

    def draw(self):
        """Draw everything: scene + overlays + flip. Kept for backward compat."""
        self.draw_scene()
        self.draw_overlay()
        pygame.display.flip()

    @property
    def is_game_over(self):
        """External check: has the game ended (player died)?"""
        return self.state == DEAD

    @property
    def is_new_record(self):
        """Check if current score is a new high score."""
        return self.ui.high_score == int(self.score) and int(self.score) > 0

    def cleanup(self):
        self.ui.save_high_score()
