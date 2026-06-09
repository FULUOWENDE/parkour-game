import os
import math

import pygame

from src.constants import (
    CHALLENGE_LIMIT,
    HEIGHT,
    HUD_BG,
    PLAYER_MAX_JUMPS,
    SHOP_ITEMS,
    SPEED_CAP,
    TEXT_ACCENT,
    TEXT_EBIKE,
    TEXT_LIGHT,
    TEXT_SHIELD,
    TEXT_SLOW,
    WIDTH,
)

FONT_REGULAR = os.path.join(os.path.dirname(__file__), "resources", "fonts", "NotoSansSC-Regular.ttf")
FONT_BOLD = os.path.join(os.path.dirname(__file__), "resources", "fonts", "NotoSansSC-Bold.ttf")
_FONT_CACHE = {}


def _get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        path = FONT_BOLD if bold else FONT_REGULAR
        try:
            _FONT_CACHE[key] = pygame.font.Font(path, size)
        except Exception:
            _FONT_CACHE[key] = pygame.font.Font(None, size)
    return _FONT_CACHE[key]


class UI:
    def __init__(self):
        self.font_sm = _get_font(14)
        self.font_md = _get_font(18, bold=True)
        self.font_lg = _get_font(26, bold=True)
        self.font_xl = _get_font(42, bold=True)
        self.font_title = _get_font(58, bold=True)
        self.high_score = 0
        self._item_images = {}

    def save_high_score(self):
        pass

    def check_high_score(self, score):
        s = int(score)
        if s > self.high_score:
            self.high_score = s
            return True
        return False

    def draw_hud(self, surface, game):
        player = game.player
        panel = pygame.Surface((WIDTH, 76), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 0))
        pygame.draw.rect(panel, HUD_BG, (12, 10, 540, 56), border_radius=8)
        pygame.draw.rect(panel, HUD_BG, (WIDTH - 268, 10, 256, 56), border_radius=8)
        surface.blit(panel, (0, 0))

        mode_name = "无尽" if game.mode == "endless" else f"限时 {game.level_idx + 1}/10"
        time_value = game.elapsed if game.mode == "endless" else max(0, CHALLENGE_LIMIT - game.elapsed)
        left_text = f"{mode_name}  距离 {int(game.distance_m)}m  金币 {game.session_coins}  时间 {int(time_value)}s"
        surface.blit(self.font_md.render(left_text, True, TEXT_LIGHT), (26, 22))

        lives = str(max(0, player.lives))
        best = int(game.save_data.get("best_distance", 0))
        right_text = f"生命 {lives}   最高 {best}m"
        surface.blit(self.font_md.render(right_text, True, TEXT_LIGHT), (WIDTH - 252, 22))

        speed_pct = min(max((game.speed - 5.5) / (SPEED_CAP - 5.5), 0), 1)
        bar = pygame.Rect(WIDTH - 252, 48, 220, 7)
        pygame.draw.rect(surface, (85, 85, 85), bar, border_radius=4)
        fill = pygame.Rect(bar.x, bar.y, int(bar.w * speed_pct), bar.h)
        pygame.draw.rect(surface, (255, 200, 50) if speed_pct < 0.75 else (255, 88, 80), fill, border_radius=4)

        for i in range(PLAYER_MAX_JUMPS):
            dot_x = 34 + i * 20
            color = (255, 200, 50) if i >= player.jumps else (100, 100, 100)
            pygame.draw.circle(surface, color, (dot_x, 60), 6)
            pygame.draw.circle(surface, (40, 40, 40), (dot_x, 60), 6, width=1)

        self._draw_effects(surface, game)
        self._draw_inventory(surface, game)

    def _draw_effects(self, surface, game):
        player = game.player
        x, y = 18, 82
        effects = []
        if player.shield_timer > 0:
            effects.append((f"护盾 {player.shield_timer / 60:.1f}s", TEXT_SHIELD))
        if player.coffee_timer > 0:
            effects.append((f"提神 {player.coffee_timer / 60:.1f}s", TEXT_ACCENT))
        if player.magnet_timer > 0:
            effects.append((f"笔记吸附 {player.magnet_timer / 60:.1f}s", (128, 229, 111)))
        if player.dash_timer > 0:
            effects.append((f"电动车 {player.dash_timer / 60:.1f}s", TEXT_EBIKE))
        if game.freeze_timer > 0:
            effects.append((f"暂停时间 {game.freeze_timer / 60:.1f}s", TEXT_SLOW))
        if game.hit_stop_timer > 0:
            effects.append((f"停顿 {game.hit_stop_timer / 60:.1f}s", (255, 110, 90)))

        for text, color in effects:
            label = self.font_sm.render(text, True, color)
            rect = pygame.Rect(x, y, label.get_width() + 16, 24)
            pygame.draw.rect(surface, HUD_BG, rect, border_radius=6)
            surface.blit(label, (x + 8, y + 4))
            x += rect.w + 8

    def _draw_inventory(self, surface, game):
        inventory = game.save_data.get("inventory", {})
        x = 18
        y = HEIGHT - 58
        for i, item in enumerate(SHOP_ITEMS):
            count = inventory.get(item["id"], 0)
            rect = pygame.Rect(x + i * 72, y, 64, 42)
            pygame.draw.rect(surface, (40, 35, 42, 190), rect, border_radius=7)
            pygame.draw.rect(surface, (255, 255, 255, 80), rect, width=1, border_radius=7)
            key = self.font_sm.render(str(i + 1), True, TEXT_LIGHT)
            surface.blit(key, (rect.x + 5, rect.y + 4))
            label = self.font_sm.render(f"x{count}", True, TEXT_LIGHT if count else (140, 140, 140))
            surface.blit(label, (rect.x + 32, rect.y + 20))
            icon = self._load_item_image(item["image"], (28, 28))
            if icon:
                if count <= 0:
                    icon = icon.copy()
                    icon.set_alpha(80)
                surface.blit(icon, (rect.x + 20, rect.y + 5))

    def _load_item_image(self, image_name, size):
        key = (image_name, size)
        if key in self._item_images:
            return self._item_images[key]
        path = os.path.join(os.path.dirname(__file__), "resources", "items", image_name)
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, size)
        except Exception:
            img = None
        self._item_images[key] = img
        return img

    def draw_start_screen(self, surface, frame, mode, level):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((35, 25, 20, 118))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 130, 500, 260)
        pygame.draw.rect(surface, (80, 50, 33), panel, border_radius=18)
        pygame.draw.rect(surface, (255, 247, 222), panel.inflate(-8, -8), border_radius=14)

        title = "无尽模式" if mode == "endless" else f"限时模式 第{level['id']}关"
        detail = "越跑越快，看看你能撑多远。" if mode == "endless" else f"{level['length']}m / 60秒，奖励 {level['reward']} 金币"
        surface.blit(self.font_xl.render(title, True, (255, 96, 121)), (panel.x + 98, panel.y + 42))
        surface.blit(self.font_md.render(detail, True, (80, 50, 33)), (panel.x + 72, panel.y + 105))
        surface.blit(self.font_sm.render("Space / ↑ / W 跳跃与二段跳    ↓ / S 下滑    1-6 使用道具", True, (96, 86, 70)), (panel.x + 53, panel.y + 150))
        prompt = self.font_lg.render("按空格或点击开始", True, (65, 126, 217))
        prompt.set_alpha(int(160 + 80 * abs(math.sin(frame * 0.06))))
        surface.blit(prompt, prompt.get_rect(center=(panel.centerx, panel.y + 205)))
