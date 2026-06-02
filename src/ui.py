import math
import os

import pygame

from src.constants import (
    DEAD,
    HEIGHT,
    HIGHSCORE_FILE,
    HUD_BG,
    PLAYER_MAX_JUMPS,
    PLAYING,
    SHIELD_DURATION,
    SPEED_CAP,
    SPEED_SLOW_DURATION,
    START,
    TEXT_ACCENT,
    TEXT_LIGHT,
    TEXT_RED,
    TEXT_SHIELD,
    TEXT_SLOW,
    TITLE,
    WIDTH,
)


_FONT_REGULAR = os.path.join(os.path.dirname(__file__), "resources", "fonts", "NotoSansSC-Regular.ttf")
_FONT_BOLD = os.path.join(os.path.dirname(__file__), "resources", "fonts", "NotoSansSC-Bold.ttf")
_FONT_CACHE = {}


def _get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        path = _FONT_BOLD if bold else _FONT_REGULAR
        try:
            _FONT_CACHE[key] = pygame.font.Font(path, size)
        except Exception:
            _FONT_CACHE[key] = pygame.font.Font(None, size)
    return _FONT_CACHE[key]


class UI:
    def __init__(self):
        self.font_sm = _get_font(14)
        self.font_md = _get_font(18)
        self.font_lg = _get_font(24)
        self.font_xl = _get_font(40, bold=True)
        self.font_title = _get_font(56, bold=True)
        self.high_score = self._load_high_score()
        # pre-rendered surfaces for start/game-over screens
        self._start_prompt_surf = None
        self._restart_prompt_surf = None

    def _load_high_score(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, "r") as f:
                    return int(f.read().strip())
        except (ValueError, OSError):
            pass
        return 0

    def save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except OSError:
            pass

    def check_high_score(self, score):
        s = int(score)
        if s > self.high_score:
            self.high_score = s
            return True
        return False

    # ── HUD ────────────────────────────────────────────────────────
    def draw_hud(self, surface, score, speed, player):
        # Score background
        hud_w = 200
        hud_h = 56
        # add extra height for status indicators when effects are active
        extra_h = 0
        if player.shield_timer > 0:
            extra_h += 18
        if player.slow_timer > 0:
            extra_h += 18
        hud_bg = pygame.Surface((hud_w, hud_h + extra_h), pygame.SRCALPHA)
        pygame.draw.rect(hud_bg, HUD_BG, hud_bg.get_rect(), border_radius=6)
        surface.blit(hud_bg, (12, 10))

        # Score text
        score_text = self.font_md.render(f"分数  {int(score):06d}", True, TEXT_LIGHT)
        surface.blit(score_text, (22, 14))

        # High score
        best_text = self.font_sm.render(f"最高  {self.high_score:06d}", True, (200, 200, 200))
        surface.blit(best_text, (22, 38))

        # Status indicators
        status_y = 70
        if player.shield_timer > 0:
            secs = player.shield_timer / 60.0
            shield_label = self.font_sm.render(f"🛡 护盾 {secs:.1f}s", True, TEXT_SHIELD)
            shield_bg = pygame.Surface((shield_label.get_width() + 12, 16), pygame.SRCALPHA)
            pygame.draw.rect(shield_bg, HUD_BG, shield_bg.get_rect(), border_radius=4)
            surface.blit(shield_bg, (12, status_y))
            surface.blit(shield_label, (18, status_y + 1))
            status_y += 18
        if player.slow_timer > 0:
            secs = player.slow_timer / 60.0
            slow_label = self.font_sm.render(f"❄ 减速 {secs:.1f}s", True, TEXT_SLOW)
            slow_bg = pygame.Surface((slow_label.get_width() + 12, 16), pygame.SRCALPHA)
            pygame.draw.rect(slow_bg, HUD_BG, slow_bg.get_rect(), border_radius=4)
            surface.blit(slow_bg, (12, status_y))
            surface.blit(slow_label, (18, status_y + 1))

        # Speed bar background
        bar_x = WIDTH - 136
        bar_y = 14
        bar_w = 120
        bar_h = 8
        bar_bg = pygame.Surface((bar_w + 8, 42), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, HUD_BG, bar_bg.get_rect(), border_radius=6)
        surface.blit(bar_bg, (bar_x - 4, bar_y - 10))

        # Speed label
        speed_level = int((speed - 5.5) / 0.5) + 1
        spd_text = self.font_sm.render(f"速度 Lv{speed_level}", True, (200, 200, 200))
        surface.blit(spd_text, (bar_x - 4, bar_y - 8))

        # Speed bar fill
        max_spd = SPEED_CAP - 5.5
        cur_spd = speed - 5.5
        pct = min(cur_spd / max_spd, 1.0)
        bar_bg_rect = pygame.Rect(bar_x, bar_y + 10, bar_w, bar_h)
        pygame.draw.rect(surface, (80, 80, 80), bar_bg_rect, border_radius=4)

        if pct < 0.5:
            bar_color = (60, 180, 100)
        elif pct < 0.8:
            bar_color = (255, 200, 50)
        else:
            bar_color = (255, 60, 60)

        if pct > 0:
            fill_rect = pygame.Rect(bar_x, bar_y + 10, int(bar_w * pct), bar_h)
            pygame.draw.rect(surface, bar_color, fill_rect, border_radius=4)

        # Jump dots
        for i in range(PLAYER_MAX_JUMPS):
            dot_cx = WIDTH - 24 - i * 20
            dot_cy = 52
            used = i < player.jumps
            if used:
                pygame.draw.circle(surface, (80, 80, 80), (dot_cx, dot_cy), 6)
            else:
                pygame.draw.circle(surface, (255, 200, 50), (dot_cx, dot_cy), 6)
                pygame.draw.circle(surface, (40, 40, 40), (dot_cx, dot_cy), 6, 1)

        jump_label = self.font_sm.render("跳跃", True, (200, 200, 200))
        surface.blit(jump_label, (WIDTH - 60, 56))

    # ── Start Screen ───────────────────────────────────────────────
    def draw_start_screen(self, surface, frame):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        cy = HEIGHT // 2

        # Title
        title = self.font_title.render("赶 早 八", True, TEXT_LIGHT)
        tw, th = title.get_size()
        surface.blit(title, (WIDTH // 2 - tw // 2, cy - 110))

        # Subtitle
        sub = self.font_lg.render("Campus Rush", True, TEXT_ACCENT)
        sw, sh = sub.get_size()
        surface.blit(sub, (WIDTH // 2 - sw // 2, cy - 5))

        # Controls
        ctrl1 = self.font_md.render("空格/↑/W — 跳跃（可二段跳）", True, (220, 220, 220))
        ctrl2 = self.font_md.render("↓/S — 下蹲（躲避上方障碍物）", True, (220, 220, 220))
        ctrl3 = self.font_sm.render("鼠标: 上半屏跳跃 / 下半屏下蹲", True, (180, 180, 180))
        cw1, ch1 = ctrl1.get_size()
        cw2, ch2 = ctrl2.get_size()
        cw3, ch3 = ctrl3.get_size()
        surface.blit(ctrl1, (WIDTH // 2 - cw1 // 2, cy + 35))
        surface.blit(ctrl2, (WIDTH // 2 - cw2 // 2, cy + 68))
        surface.blit(ctrl3, (WIDTH // 2 - cw3 // 2, cy + 98))

        # Pulsing prompt (pre-render text, apply alpha per-frame)
        if self._start_prompt_surf is None:
            prompt = self.font_lg.render("按空格键 或 点击开始", True, TEXT_ACCENT)
            self._start_prompt_surf = pygame.Surface(prompt.get_size(), pygame.SRCALPHA)
            self._start_prompt_surf.blit(prompt, (0, 0))
        pulse = 0.6 + 0.4 * math.sin(frame * 0.06)
        prompt_copy = self._start_prompt_surf.copy()
        prompt_copy.set_alpha(int(pulse * 255))
        surface.blit(prompt_copy, (WIDTH // 2 - prompt_copy.get_width() // 2, cy + 140))

        if self.high_score > 0:
            hs_text = self.font_sm.render(f"历史最高分：{self.high_score}", True, (200, 200, 200))
            hsw, hsh = hs_text.get_size()
            surface.blit(hs_text, (WIDTH // 2 - hsw // 2, cy + 182))

    # ── Game Over Screen ───────────────────────────────────────────
    def draw_game_over_screen(self, surface, frame, score, new_record):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 10, 10, 160))
        surface.blit(overlay, (0, 0))

        cy = HEIGHT // 2

        # Game Over
        go_text = self.font_title.render("GAME OVER", True, TEXT_RED)
        gw, gh = go_text.get_size()
        surface.blit(go_text, (WIDTH // 2 - gw // 2, cy - 105))

        # Score
        score_text = self.font_xl.render(f"得分：{int(score)}", True, TEXT_LIGHT)
        sw, sh = score_text.get_size()
        surface.blit(score_text, (WIDTH // 2 - sw // 2, cy + 0))

        # New record or best
        if new_record:
            rec_text = self.font_lg.render("★  新纪录  ★", True, TEXT_ACCENT)
            rw, rh = rec_text.get_size()
            surface.blit(rec_text, (WIDTH // 2 - rw // 2, cy + 62))
        else:
            best_text = self.font_md.render(f"最高分：{self.high_score}", True, (200, 200, 200))
            bw, bh = best_text.get_size()
            surface.blit(best_text, (WIDTH // 2 - bw // 2, cy + 62))

        # Pulsing restart (pre-render text, apply alpha per-frame)
        if self._restart_prompt_surf is None:
            restart = self.font_lg.render("按空格键重新开始", True, TEXT_LIGHT)
            self._restart_prompt_surf = pygame.Surface(restart.get_size(), pygame.SRCALPHA)
            self._restart_prompt_surf.blit(restart, (0, 0))
        pulse = 0.6 + 0.4 * math.sin(frame * 0.06)
        restart_copy = self._restart_prompt_surf.copy()
        restart_copy.set_alpha(int(pulse * 255))
        rsw, rsh = restart_copy.get_size()
        surface.blit(restart_copy, (WIDTH // 2 - rsw // 2, cy + 110))
