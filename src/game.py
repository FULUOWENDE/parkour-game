import json
import math
import os
import random

import pygame

from src.background import Background
from src.constants import (
    BASE_SPAWN_GAP,
    BASE_SPEED,
    CHALLENGE_LIMIT,
    CHAR_LIST,
    DEAD,
    EBIKE_SPEED_FACTOR,
    HEIGHT,
    LEVEL_LIST,
    METER_PIXELS,
    MIN_SPAWN_GAP,
    PLAYING,
    PLAYER_START_LIVES,
    SAVE_FILE,
    SCORE_RATE,
    SHOP_ITEMS,
    SPAWN_GAP_DECAY,
    SPEED_CAP,
    SPEED_RAMP,
    SPEED_SLOW_FACTOR,
    START,
    TEACHER_QUOTES,
    WEATHER_CLOUDY,
    WEATHER_CLOUDY_SCORE,
    WEATHER_RAINY,
    WEATHER_RAINY_SCORE,
    WEATHER_SNOWY,
    WEATHER_SNOWY_SCORE,
    WEATHER_STORMY,
    WEATHER_STORMY_SCORE,
    WEATHER_SUNNY,
    WIDTH,
)
from src.npcs import npc_factory
from src.obstacles import obstacle_factory
from src.player import Player
from src.ui import UI
from src.utils import check_collision, draw_particles, spawn_burst, update_particles


DEFAULT_SAVE = {
    "nickname": "",
    "coins": 120,
    "best_distance": 0,
    "unlocked_level": 1,
    "selected_char": 0,
    "inventory": {},
    "distance_rankings": [],
    "wealth_rankings": [],
}


class Game:
    def __init__(self, screen, sound_manager=None):
        self.screen = screen
        self.sound = sound_manager
        self.background = Background()
        self.ui = UI()
        self.save_data = self._load_save()

        self.state = START
        self.mode = "endless"
        self.level_idx = None
        self.char_idx = self.save_data.get("selected_char", 0)
        self.char_idx = max(0, min(self.char_idx, len(CHAR_LIST) - 1))
        self.player = Player(CHAR_LIST[self.char_idx])

        self.score = 0
        self.distance_m = 0
        self.elapsed = 0
        self.session_coins = 0
        self.reward_coins = 0
        self.speed = BASE_SPEED
        self.target_speed = BASE_SPEED
        self.speed_multiplier = 1.0
        self.frame = 0
        self.ground_offset = 0
        self.spawn_timer = 0
        self.coin_timer = 0
        self.weather = WEATHER_SUNNY
        self.weather_flash = 0
        self.freeze_timer = 0
        self.hit_stop_timer = 0
        self.result = {}
        self.is_finished = False
        self.last_run = {"mode": "endless", "level_idx": None}

        self.obstacles = []
        self.coins = []
        self.npcs = []
        self.particles = []

    def _load_save(self):
        data = DEFAULT_SAVE.copy()
        data["inventory"] = {}
        data["distance_rankings"] = []
        data["wealth_rankings"] = []
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                data.update(raw)
                data["inventory"] = dict(raw.get("inventory", {}))
                data["distance_rankings"] = list(raw.get("distance_rankings", []))
                data["wealth_rankings"] = list(raw.get("wealth_rankings", []))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass
        return data

    def save(self):
        self.save_data["selected_char"] = self.char_idx
        self._record_wealth()
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.save_data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass
        self.ui.high_score = max(self.ui.high_score, int(self.save_data.get("best_distance", 0)))
        self.ui.save_high_score()

    def set_nickname(self, nickname):
        nickname = (nickname or "").strip()
        self.save_data["nickname"] = nickname[:12] if nickname else "早八同学"
        self.save()

    @property
    def nickname(self):
        return self.save_data.get("nickname") or "早八同学"

    def distance_rankings(self):
        rows = list(self.save_data.get("distance_rankings", []))
        rows.sort(key=lambda row: row.get("distance", 0), reverse=True)
        return rows[:100]

    def wealth_rankings(self):
        self._record_wealth(save_now=False)
        rows = list(self.save_data.get("wealth_rankings", []))
        rows.sort(key=lambda row: row.get("coins", 0), reverse=True)
        return rows[:100]

    def buy_item(self, item_idx):
        if item_idx < 0 or item_idx >= len(SHOP_ITEMS):
            return False, "没有这个道具"
        item = SHOP_ITEMS[item_idx]
        coins = int(self.save_data.get("coins", 0))
        if coins < item["price"]:
            return False, "金币不够"
        self.save_data["coins"] = coins - item["price"]
        inventory = self.save_data.setdefault("inventory", {})
        inventory[item["id"]] = inventory.get(item["id"], 0) + 1
        self.save()
        return True, f"已购买 {item['name']}"

    def start_game(self, char_idx=0, mode="endless", level_idx=None, immediate=False):
        self.char_idx = max(0, min(char_idx, len(CHAR_LIST) - 1))
        self.save_data["selected_char"] = self.char_idx
        self.mode = mode
        self.level_idx = level_idx
        self.last_run = {"mode": mode, "level_idx": level_idx}
        char_config = CHAR_LIST[self.char_idx]

        self.state = PLAYING if immediate else START
        self.score = 0
        self.distance_m = 0
        self.elapsed = 0
        self.session_coins = 0
        self.reward_coins = 0
        self.speed = BASE_SPEED + (level_idx or 0) * 0.25 if mode == "timed" else BASE_SPEED
        self.target_speed = self.speed
        self.speed_multiplier = 1.0
        self.frame = 0
        self.ground_offset = 0
        self.spawn_timer = 0
        self.coin_timer = 0
        self.weather = WEATHER_SUNNY
        self.weather_flash = 0
        self.freeze_timer = 0
        self.hit_stop_timer = 0
        self.result = {}
        self.is_finished = False

        self.obstacles = []
        self.coins = []
        self.npcs = []
        self.particles = []
        self.player = Player(char_config, lives=PLAYER_START_LIVES)

    def replay_last(self):
        self.start_game(self.char_idx, self.last_run["mode"], self.last_run["level_idx"], immediate=True)

    @property
    def effective_speed(self):
        boost = self.speed_multiplier
        if self.player.ebike_timer > 0:
            boost *= EBIKE_SPEED_FACTOR
        if self.player.dash_timer > 0:
            boost *= 1.65
        if self.hit_stop_timer > 0 or self.freeze_timer > 0:
            return 0
        return self.speed * boost * self.player.speed_mul

    @property
    def current_level(self):
        if self.mode != "timed" or self.level_idx is None:
            return None
        if 0 <= self.level_idx < len(LEVEL_LIST):
            return LEVEL_LIST[self.level_idx]
        return None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.state == START:
                    self._begin_play()
                elif self.state == PLAYING:
                    self.player.jump(self.particles)
                    if self.sound:
                        self.sound.play_jump()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.state == PLAYING:
                    self.player.slide()
                    if self.sound:
                        self.sound.play_slide()
            elif pygame.K_1 <= event.key <= pygame.K_6:
                self.use_item(event.key - pygame.K_1)

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

    def use_item(self, item_idx):
        if item_idx < 0 or item_idx >= len(SHOP_ITEMS) or self.state != PLAYING:
            return False
        item = SHOP_ITEMS[item_idx]
        inventory = self.save_data.setdefault("inventory", {})
        if inventory.get(item["id"], 0) <= 0:
            return False
        inventory[item["id"]] -= 1
        if inventory[item["id"]] <= 0:
            inventory.pop(item["id"], None)

        effect = item["effect"]
        if effect == "shield":
            self.player.shield_timer = max(self.player.shield_timer, 60 * 8)
        elif effect == "speed":
            self.player.coffee_timer = max(self.player.coffee_timer, 60 * 5)
            self.speed_multiplier = max(self.speed_multiplier, 1.32)
        elif effect == "magnet":
            self.player.magnet_timer = max(self.player.magnet_timer, 60 * 8)
        elif effect == "life":
            self.player.lives += 1
        elif effect == "freeze":
            self.freeze_timer = max(self.freeze_timer, 60 * 3)
        elif effect == "dash":
            self.player.dash_timer = max(self.player.dash_timer, 60 * 4)
            self.player.ebike_timer = max(self.player.ebike_timer, 60 * 4)

        self.save()
        if self.sound:
            self.sound.play_item(item["id"])
        self.particles.extend(spawn_burst(self.player.cx, self.player.cy, 18, [(255, 255, 255), (255, 220, 80), (128, 229, 111)]))
        return True

    def _begin_play(self):
        self.state = PLAYING

    def update(self):
        if self.state != PLAYING or self.is_finished:
            return

        self.frame += 1
        self.particles = update_particles(self.particles)
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
        if self.hit_stop_timer > 0:
            self.hit_stop_timer -= 1

        time_frozen = self.freeze_timer > 0
        movement_frozen = self.freeze_timer > 0 or self.hit_stop_timer > 0

        if self.mode == "timed" and not time_frozen:
            self.elapsed += 1 / 60
            self._check_finish_conditions()
            if self.is_finished:
                self.player.update(0, BASE_SPEED)
                return

        if not movement_frozen:
            if self.mode != "timed":
                self.elapsed += 1 / 60
            self.distance_m += self.effective_speed / METER_PIXELS
            self.score = self.distance_m
            self.ground_offset += self.effective_speed
            self._update_speed()
            self._update_weather()
            self._spawn_world()
            self._update_entities()
            self._handle_collisions()
            self._check_finish_conditions()

        self.player.update(self.effective_speed if not movement_frozen else 0, BASE_SPEED)

    def _update_speed(self):
        if self.mode == "timed":
            level_no = (self.level_idx or 0) + 1
            difficulty = (level_no - 1) / 9
            base = BASE_SPEED + level_no * 0.48 + difficulty * 0.65
            progress = 0
            if self.current_level:
                progress = self.distance_m / max(1, self.current_level["length"])
            self.target_speed = min(
                base + self.distance_m * (0.011 + difficulty * 0.004) + level_no * 0.13 + progress * (1.0 + level_no * 0.12),
                SPEED_CAP + 4.5,
            )
            self.speed += (self.target_speed - self.speed) * (0.045 + difficulty * 0.012)
        else:
            self.speed = min(BASE_SPEED + math.floor(self.score / SPEED_RAMP) * 0.5, SPEED_CAP)

        if self.player.coffee_timer <= 0 and self.speed_multiplier > 1.0 and self.player.dash_timer <= 0:
            self.speed_multiplier = 1.0
        if self.player.slow_timer <= 0 and self.speed_multiplier < 1.0:
            self.speed_multiplier = 1.0

    def _update_weather(self):
        prev = self.weather
        if self.mode == "timed":
            self.weather = WEATHER_SUNNY
        elif self.score < WEATHER_CLOUDY_SCORE:
            self.weather = WEATHER_SUNNY
        elif self.score < WEATHER_RAINY_SCORE:
            self.weather = WEATHER_CLOUDY
        elif self.score < WEATHER_SNOWY_SCORE:
            self.weather = WEATHER_RAINY
        elif self.score < WEATHER_STORMY_SCORE:
            self.weather = WEATHER_SNOWY
        else:
            self.weather = WEATHER_STORMY

        if self.weather != prev:
            self.weather_flash = 105
            if self.sound:
                if self.weather in (WEATHER_RAINY, WEATHER_STORMY):
                    self.sound.play_rain_start()
                    self.sound.switch_bgm("tension")
                else:
                    self.sound.switch_bgm("early")

    def _spawn_world(self):
        self.spawn_timer += 1
        self.coin_timer += 1

        if self.mode == "timed":
            level_no = (self.level_idx or 0) + 1
            difficulty = (level_no - 1) / 9
            progress = 0
            if self.current_level:
                progress = self.distance_m / max(1, self.current_level["length"])
            spawn_gap = max(
                18,
                BASE_SPAWN_GAP - level_no * 8 - int(difficulty * 20) - int(self.distance_m / 64) * 4 - int(progress * (16 + level_no)),
            )
            mode_for_obstacles = 0 if level_no < 3 and progress < 0.38 else 1
        else:
            spawn_gap = max(MIN_SPAWN_GAP, BASE_SPAWN_GAP - math.floor(self.score / SPAWN_GAP_DECAY) * 5)
            mode_for_obstacles = 0
            if self.weather in (WEATHER_RAINY, WEATHER_SNOWY, WEATHER_STORMY):
                spawn_gap = max(MIN_SPAWN_GAP - 8, spawn_gap - 5)
            if self.weather == WEATHER_STORMY:
                spawn_gap = max(MIN_SPAWN_GAP - 12, spawn_gap - 4)

        if self.spawn_timer >= spawn_gap + random.random() * 28:
            self.obstacles.append(obstacle_factory(self.score, self.weather, mode_for_obstacles))
            self.spawn_timer = 0

        if self.coin_timer >= 44 + random.random() * 32:
            self.coins.append(Coin(WIDTH + 40, random.choice([300, 330, 360, 390])))
            self.coin_timer = 0

        if random.random() < 0.006:
            self.npcs.append(npc_factory())

    def _update_entities(self):
        for coin in self.coins:
            coin.update(self.effective_speed, self.player)
        self.coins = [coin for coin in self.coins if not coin.is_offscreen() and not coin.collected]

        for obstacle in self.obstacles:
            obstacle.update(self.effective_speed)
        self.obstacles = [obstacle for obstacle in self.obstacles if not obstacle.is_offscreen() and not obstacle.scored]

        for npc in self.npcs:
            npc.update(self.effective_speed)
        self.npcs = [npc for npc in self.npcs if not npc.is_offscreen()]

    def _handle_collisions(self):
        for coin in self.coins:
            if coin.collides_with(self.player):
                coin.collected = True
                self.session_coins += 1
                self.particles.extend(spawn_burst(coin.x, coin.y, 8, [(255, 217, 80), (255, 255, 180)]))

        for obstacle in self.obstacles:
            if not check_collision(self.player, obstacle):
                continue
            if obstacle.is_item:
                obstacle.apply_effect(self)
                obstacle.scored = True
                if self.sound:
                    self.sound.play_item(type(obstacle).__name__)
                self.particles.extend(spawn_burst(obstacle.x + obstacle.w // 2, obstacle.y + obstacle.h // 2, 14, [(255, 255, 255), (255, 215, 0)]))
                continue
            if self.player.dash_timer > 0:
                obstacle.scored = True
                self.particles.extend(spawn_burst(obstacle.x + obstacle.w // 2, obstacle.y + obstacle.h // 2, 12, [(255, 220, 80), (255, 140, 40)]))
                continue
            if self.player.shield_timer > 0:
                self.player.shield_timer = 0
                obstacle.scored = True
                self.particles.extend(spawn_burst(obstacle.x + obstacle.w // 2, obstacle.y + obstacle.h // 2, 12, [(255, 215, 0), (255, 255, 200)]))
                continue
            if self.player.invulnerable_timer > 0:
                continue

            obstacle.scored = True
            self.player.invulnerable_timer = 80
            self.particles.extend(spawn_burst(self.player.cx, self.player.cy, 22, [(255, 60, 60), (255, 140, 30), (255, 255, 255)]))
            if self.mode == "timed":
                self.hit_stop_timer = 120
                continue

            self.player.lives -= 1
            if self.player.lives <= 0:
                self.finish_run(False)
                return

    def _check_finish_conditions(self):
        if self.mode == "timed":
            level = self.current_level
            if level and self.distance_m >= level["length"]:
                self.finish_run(True)
            elif self.elapsed >= CHALLENGE_LIMIT:
                self.finish_run(False)

    def finish_run(self, success):
        if self.is_finished:
            return
        self.is_finished = True
        self.state = DEAD
        level = self.current_level
        reward = 0
        quote = "校旗就在眼前，今天没有迟到。" if success else random.choice(TEACHER_QUOTES)

        if self.mode == "timed" and success and level:
            reward = level["reward"]
            self.save_data["unlocked_level"] = max(self.save_data.get("unlocked_level", 1), min(level["id"] + 1, len(LEVEL_LIST)))
        elif self.mode == "endless":
            self.save_data["best_distance"] = max(float(self.save_data.get("best_distance", 0)), self.distance_m)
            self.ui.check_high_score(self.distance_m)
            self._record_endless_run()

        self.reward_coins = reward
        self.save_data["coins"] = int(self.save_data.get("coins", 0)) + self.session_coins + reward
        self.result = {
            "success": success,
            "quote": quote,
            "distance": self.distance_m,
            "coins": self.session_coins + reward,
            "time": self.elapsed,
            "mode": self.mode,
        }
        self.save()
        if self.sound and not success:
            self.sound.play_death()

    def _record_endless_run(self):
        rows = list(self.save_data.get("distance_rankings", []))
        rows.append({
            "name": self.nickname,
            "distance": int(self.distance_m),
            "coins": int(self.session_coins),
        })
        rows.sort(key=lambda row: row.get("distance", 0), reverse=True)
        self.save_data["distance_rankings"] = rows[:100]

    def _record_wealth(self, save_now=False):
        rows = [
            row for row in self.save_data.get("wealth_rankings", [])
            if row.get("name") != self.nickname
        ]
        rows.append({
            "name": self.nickname,
            "coins": int(self.save_data.get("coins", 0)),
        })
        rows.sort(key=lambda row: row.get("coins", 0), reverse=True)
        self.save_data["wealth_rankings"] = rows[:100]
        if save_now:
            self.save()

    def draw_scene(self):
        self.background.draw(self.screen, self.ground_offset, self.weather, self.frame)

        for npc in self.npcs:
            npc.draw(self.screen, self.frame)
        for coin in self.coins:
            coin.draw(self.screen, self.frame)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen, self.frame)

        if self.state != DEAD:
            self.player.draw(self.screen, self.frame)

        if self.mode == "timed" and self.current_level:
            self._draw_finish_line()

        draw_particles(self.screen, self.particles)
        self._draw_weather_flash()

    def _draw_finish_line(self):
        level = self.current_level
        if not level:
            return
        finish_x = self.player.x + (level["length"] - self.distance_m) * METER_PIXELS
        if -120 < finish_x < WIDTH + 160:
            pole_x = int(finish_x)
            pygame.draw.rect(self.screen, (80, 50, 33), (pole_x, 220, 8, 228))
            pygame.draw.rect(self.screen, (239, 77, 77), (pole_x + 8, 224, 110, 48))
            pygame.draw.rect(self.screen, (255, 230, 110), (pole_x + 22, 238, 72, 10))
            pygame.draw.rect(self.screen, (255, 250, 225), (pole_x + 22, 254, 54, 8))
            font = self.ui.font_md
            label = font.render("教学楼", True, (80, 50, 33))
            self.screen.blit(label, (pole_x + 18, 180))

    def _draw_weather_flash(self):
        if self.weather_flash <= 0:
            return
        self.weather_flash -= 1
        alpha = int(min(95, self.weather_flash * 1.5))
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        label = ""
        color = (255, 255, 255)
        if self.weather == WEATHER_CLOUDY:
            flash.fill((44, 50, 68, alpha))
            label = "阴天来了"
            color = (255, 218, 91)
        elif self.weather == WEATHER_RAINY:
            flash.fill((42, 63, 92, alpha))
            label = "下雨了"
            color = (83, 197, 255)
        elif self.weather == WEATHER_SNOWY:
            flash.fill((210, 232, 250, alpha))
            label = "下雪了"
            color = (255, 255, 255)
        elif self.weather == WEATHER_STORMY:
            flash.fill((26, 28, 48, alpha))
            label = "打雷了"
            color = (255, 231, 98)
        self.screen.blit(flash, (0, 0))
        text = self.ui.font_title.render(label, True, color)
        shadow = self.ui.font_title.render(label, True, (80, 50, 33))
        center = (WIDTH // 2, HEIGHT // 2 - 54)
        self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 4)))
        self.screen.blit(text, text.get_rect(center=center))

    def draw_overlay(self):
        if self.state == PLAYING:
            self.ui.draw_hud(self.screen, self)
        elif self.state == START:
            self.ui.draw_start_screen(self.screen, self.frame, self.mode, self.current_level)

    @property
    def is_game_over(self):
        return self.state == DEAD

    def cleanup(self):
        self.save()


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 11
        self.collected = False
        self.seed = random.random() * math.pi * 2

    def update(self, speed, player):
        if player.magnet_timer > 0:
            dx = player.cx - self.x
            dy = player.cy - self.y
            dist = max(1, math.hypot(dx, dy))
            if dist < 160:
                self.x += dx / dist * 8
                self.y += dy / dist * 8
                return
        self.x -= speed

    def is_offscreen(self):
        return self.x < -40

    def collides_with(self, player):
        return abs(player.cx - self.x) < player.w and abs(player.cy - self.y) < player.slide_h

    def draw(self, surface, frame):
        pulse = 0.75 + 0.25 * math.sin(frame * 0.12 + self.seed)
        w = max(6, int(self.r * 2 * pulse))
        rect = pygame.Rect(int(self.x - w // 2), int(self.y - self.r), w, self.r * 2)
        pygame.draw.ellipse(surface, (255, 217, 80), rect)
        pygame.draw.ellipse(surface, (80, 50, 33), rect, width=2)
        inner = rect.inflate(-6, -6)
        if inner.w > 0 and inner.h > 0:
            pygame.draw.ellipse(surface, (255, 245, 160), inner)
