# 抢早八 · Campus Rush — Game Constants

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
ITEM_SPAWN_CHANCE = 0.06        # base 6% chance per obstacle spawn
ITEM_SPAWN_CHANCE_MAX = 0.12    # 12% max at high score
SHIELD_DURATION = 300           # 5 sec at 60 FPS (absorbs 1 hit)
SPEED_SLOW_FACTOR = 0.55        # reduce map speed to 55%
SPEED_SLOW_DURATION = 180       # 3 sec at 60 FPS

# ── Weather ────────────────────────────────────────────────────
WEATHER_SUNNY = "sunny"
WEATHER_CLOUDY = "cloudy"
WEATHER_RAINY = "rainy"
WEATHER_CLOUDY_SCORE = 800
WEATHER_RAINY_SCORE = 2000

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
