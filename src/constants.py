# 抢早八 · Campus Rush — Game Constants

from enum import IntEnum

# ── Window ───────────────────────────────────────────────────
WIDTH = 960
HEIGHT = 540
FPS = 60
TITLE = "赶早八 · Campus Rush"

# ── Layout ───────────────────────────────────────────────────
GROUND_Y = 450
GROUND_H = 90

# ── Physics ──────────────────────────────────────────────────
GRAVITY = 0.58
JUMP_VEL = -14.5
DB_JUMP_VEL = -13.0

# ── Speed ────────────────────────────────────────────────────
BASE_SPEED = 5.5
SPEED_CAP = 16.0
SPEED_RAMP = 400

# ── Player ───────────────────────────────────────────────────
PLAYER_W = 38
PLAYER_H = 62
PLAYER_SLIDE_H = 30
PLAYER_SLIDE_DURATION = 38
PLAYER_X = 110
PLAYER_MAX_JUMPS = 2

# ── Spawn ────────────────────────────────────────────────────
BASE_SPAWN_GAP = 95
MIN_SPAWN_GAP = 52
SPAWN_GAP_DECAY = 350
SCORE_RATE = 0.048

# ── Game States ──────────────────────────────────────────────
START = "start"
PLAYING = "playing"
DEAD = "dead"

# ── High Score ───────────────────────────────────────────────
HIGHSCORE_FILE = "highscore.txt"

# ── Color Palette ────────────────────────────────────────────
OUTLINE = (40, 40, 40)

GROUND_LIGHT = (200, 190, 175)
GROUND_DARK = (170, 160, 145)

PLAYER_BODY = (220, 60, 60)
PLAYER_SKIN = (255, 220, 180)
PLAYER_JEANS = (50, 80, 160)
PLAYER_BAG = (30, 40, 80)
PLAYER_HAIR = (30, 25, 20)
PLAYER_SHOE = (50, 50, 50)

TRASH_CAN = (100, 130, 150)
TRASH_LID = (70, 90, 110)
SIGN_POLE = (140, 140, 150)
SIGN_BOARD = (80, 160, 120)
CONE_ORANGE = (255, 140, 30)
CONE_WHITE = (240, 240, 240)
TAPE_YELLOW = (255, 210, 0)
CART_RED = (200, 50, 50)
CART_SILVER = (180, 190, 200)
BUMP_YELLOW = (255, 220, 50)
BUMP_BLACK = (40, 40, 40)
BIKE_GREEN = (60, 180, 100)
BIKE_TIRE = (50, 50, 50)
BIKE_RIDER = (240, 180, 60)

# ── Overhead Obstacles (slide-under) ───────────────────────────
# TreeBranch
TREE_TRUNK = (101, 67, 33)
TREE_TRUNK_LIGHT = (130, 90, 45)
TREE_TRUNK_DARK = (65, 40, 18)
TREE_LEAF = (34, 139, 34)
TREE_LEAF_LIGHT = (80, 190, 60)
TREE_LEAF_DARK = (15, 90, 20)
TREE_LEAF_MID = (50, 155, 45)

# CampusBanner
BANNER_RED = (195, 25, 30)
BANNER_RED_LIGHT = (225, 55, 55)
BANNER_RED_DARK = (150, 15, 18)
BANNER_TEXT = (255, 255, 220)
BANNER_POLE = (130, 135, 145)
BANNER_POLE_HL = (175, 180, 190)

# BarrierGate
BARRIER_RED = (215, 35, 35)
BARRIER_POST = (110, 115, 125)
BARRIER_POST_HL = (160, 165, 175)
BARRIER_COUNTER = (60, 60, 70)

# ── Improved Shading ───────────────────────────────────────────
SHADOW = (0, 0, 0, 50)
CONE_HIGHLIGHT = (255, 175, 80)
CONE_SHADOW = (200, 100, 15)
TRASH_HIGHLIGHT = (145, 170, 190)
TRASH_SHADOW = (55, 75, 90)
CART_HIGHLIGHT = (235, 85, 85)
CART_WHEEL = (50, 50, 50)
SIGN_TEXT = (255, 255, 255)
SIGN_ARROW = (255, 255, 200)

# Overhead obstacle collision constant
OVERHEAD_BOTTOM = GROUND_Y - 42  # between standing top (388) and sliding top (420)

# ── Item / Power-up ────────────────────────────────────────────
ITEM_SPAWN_CHANCE = 0.12        # base 12% chance per obstacle spawn
ITEM_SPAWN_CHANCE_MAX = 0.20    # 20% max at high score
SHIELD_DURATION = 300           # 5 sec at 60 FPS (absorbs 1 hit)
SPEED_SLOW_FACTOR = 0.55        # reduce map speed to 55%
SPEED_SLOW_DURATION = 240       # 4 sec at 60 FPS
EBIKE_SPEED_FACTOR = 1.55       # shared e-bike speed multiplier
EBIKE_DURATION = 240            # 4 sec at 60 FPS

# ── Weather ────────────────────────────────────────────────────
WEATHER_SUNNY = "sunny"
WEATHER_CLOUDY = "cloudy"
WEATHER_RAINY = "rainy"
WEATHER_CLOUDY_SCORE = 400      # ~20s in: cloudy
WEATHER_RAINY_SCORE = 1200      # ~45s in: rainy

SKY_SUNNY = (135, 206, 235)
SKY_CLOUDY = (150, 160, 175)
SKY_RAINY = (70, 80, 95)

RAIN_COLOR = (160, 190, 220, 180)
RAIN_OVERLAY_COLOR = (35, 40, 50, 115)

# ── HUD / UI Colors ────────────────────────────────────────────
HUD_BG = (0, 0, 0, 140)
TEXT_LIGHT = (240, 240, 240)
TEXT_ACCENT = (255, 200, 50)
TEXT_RED = (255, 60, 60)
TEXT_SHIELD = (255, 215, 0)
TEXT_SLOW = (100, 200, 255)
TEXT_EBIKE = (255, 180, 30)

# ── Shared E-Bike Colors ──────────────────────────────────────
EBIKE_FRAME = (40, 140, 220)    # blue frame (like HelloBike/Hellobike)
EBIKE_FENDER = (30, 110, 190)
EBIKE_TIRE_COLOR = (35, 35, 35)
EBIKE_HUB = (200, 200, 210)
EBIKE_BASKET = (180, 180, 190)
EBIKE_SEAT = (30, 30, 35)
EBIKE_HANDLE = (160, 165, 175)
EBIKE_PEDAL = (120, 120, 130)

# ═══════════════════════════════════════════════════════════════════
#  GAME STATE MACHINE
# ═══════════════════════════════════════════════════════════════════


class GameState(IntEnum):
    MAIN_MENU = 0       # 主菜单
    SELECT_CHAR = 1     # 角色选择界面
    SELECT_MODE = 2     # 游戏模式选择
    GAME_RUN = 3        # 正常游戏跑酷
    GAME_OVER = 4       # 死亡结算界面


# ═══════════════════════════════════════════════════════════════════
#  CHARACTER PRESETS
# ═══════════════════════════════════════════════════════════════════

CHAR_LIST = [
    {
        "name": "普通学生",
        "color_body": (220, 60, 60),
        "color_skin": (255, 220, 180),
        "color_jeans": (50, 80, 160),
        "color_bag": (30, 40, 80),
        "color_hair": (30, 25, 20),
        "color_shoe": (50, 50, 50),
        "jump_mul": 1.0,
        "slide_mul": 1.0,
        "speed_mul": 1.0,
        "desc": "均衡属性，标准开局",
    },
    {
        "name": "体育生",
        "color_body": (80, 160, 60),
        "color_skin": (255, 210, 160),
        "color_jeans": (40, 60, 120),
        "color_bag": (20, 30, 60),
        "color_hair": (20, 18, 15),
        "color_shoe": (220, 180, 30),
        "jump_mul": 1.18,
        "slide_mul": 0.92,
        "speed_mul": 0.90,
        "desc": "跳跃更高，移速略慢",
    },
    {
        "name": "熬夜学霸",
        "color_body": (120, 90, 160),
        "color_skin": (240, 225, 195),
        "color_jeans": (60, 60, 80),
        "color_bag": (40, 30, 50),
        "color_hair": (35, 30, 28),
        "color_shoe": (60, 60, 60),
        "jump_mul": 0.92,
        "slide_mul": 1.25,
        "speed_mul": 1.0,
        "desc": "下蹲判定范围更大，容错高",
    },
    {
        "name": "健身学长",
        "color_body": (190, 70, 70),
        "color_skin": (255, 200, 150),
        "color_jeans": (30, 30, 40),
        "color_bag": (50, 30, 20),
        "color_hair": (25, 22, 18),
        "color_shoe": (40, 40, 40),
        "jump_mul": 1.05,
        "slide_mul": 0.85,
        "speed_mul": 1.12,
        "desc": "速度更快，障碍刷新变密",
    },
]

# ═══════════════════════════════════════════════════════════════════
#  GAME MODES
# ═══════════════════════════════════════════════════════════════════

MODE_LIST = [
    {
        "name": "普通早八",
        "desc": "原版难度曲线，标准体验",
        "detail": "随分数提升切换障碍池，正常生成间隔",
    },
    {
        "name": "极限冲刺",
        "desc": "全程高分难度，快速刷分",
        "detail": "固定高难度障碍池，生成间距缩短20%",
    },
    {
        "name": "悠闲逛校园",
        "desc": "障碍间距大，休闲闯关",
        "detail": "简单障碍池永久生效，禁用大部分高空障碍",
    },
]

# ═══════════════════════════════════════════════════════════════════
#  MENU / UI COLORS
# ═══════════════════════════════════════════════════════════════════

MENU_BG = (50, 120, 180)
MENU_BTN_NORMAL = (80, 160, 210)
MENU_BTN_HOVER = (140, 210, 245)
MENU_BTN_TEXT = (255, 255, 255)
MENU_BTN_DISABLED = (100, 100, 120)
MENU_TITLE_COLOR = (255, 255, 255)
MENU_ACCENT = (255, 200, 50)
MENU_SUBTLE = (200, 200, 210)
MENU_CARD_BG = (255, 255, 255, 25)
MENU_OVERLAY = (0, 0, 0, 140)
MENU_DANGER = (220, 60, 60)
