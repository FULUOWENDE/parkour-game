# 抢早八 · Campus Rush — Game Constants

from enum import IntEnum

# ── Window ───────────────────────────────────────────────────
WIDTH = 960
HEIGHT = 540
FPS = 60
TITLE = "早八跑酷"

# ── Layout ───────────────────────────────────────────────────
GROUND_Y = 448
GROUND_H = 90

# ── Physics ──────────────────────────────────────────────────
GRAVITY = 0.58
JUMP_VEL = -14.5
DB_JUMP_VEL = -13.0

# ── Speed ────────────────────────────────────────────────────
BASE_SPEED = 5.5
SPEED_CAP = 16.0
SPEED_RAMP = 360

# ── Player ───────────────────────────────────────────────────
PLAYER_W = 56
PLAYER_H = 82
PLAYER_SLIDE_H = 38
PLAYER_SLIDE_DURATION = 38
PLAYER_X = 110
PLAYER_MAX_JUMPS = 2
PLAYER_START_LIVES = 2

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
SAVE_FILE = "campus_rush_save.json"
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
WEATHER_SNOWY = "snowy"
WEATHER_STORMY = "stormy"
WEATHER_CLOUDY_SCORE = 320
WEATHER_RAINY_SCORE = 820
WEATHER_SNOWY_SCORE = 1450
WEATHER_STORMY_SCORE = 2150

SKY_SUNNY = (135, 206, 235)
SKY_CLOUDY = (150, 160, 175)
SKY_RAINY = (70, 80, 95)

RAIN_COLOR = (160, 190, 220, 180)
RAIN_OVERLAY_COLOR = (35, 40, 50, 115)
SNOW_COLOR = (245, 250, 255, 210)
SNOW_OVERLAY_COLOR = (220, 232, 245, 72)
STORM_OVERLAY_COLOR = (22, 27, 43, 145)

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
    WELCOME = 0         # 欢迎界面
    NICKNAME = 1        # 昵称窗口
    MAIN_MENU = 2       # 主菜单
    SELECT_CHAR = 3     # 角色选择界面
    SELECT_LEVEL = 4    # 限时关卡选择
    SHOP = 5            # 商店
    LEADERBOARD = 6     # 排行榜
    PROFILE = 7         # 个人主页
    GAME_RUN = 8        # 正常游戏跑酷
    GAME_OVER = 9       # 结算界面


# ═══════════════════════════════════════════════════════════════════
#  CHARACTER PRESETS
# ═══════════════════════════════════════════════════════════════════

CHAR_LIST = [
    {
        "id": "male",
        "name": "男大学生",
        "image": "male-student.png",
        "color_body": (95, 168, 211),
        "color_skin": (239, 178, 122),
        "color_jeans": (51, 78, 104),
        "color_bag": (244, 182, 74),
        "color_hair": (51, 37, 31),
        "color_shoe": (245, 240, 223),
        "jump_mul": 1.0,
        "slide_mul": 1.0,
        "speed_mul": 1.0,
        "desc": "均衡手感，适合标准早八冲刺。",
    },
    {
        "id": "female",
        "name": "女大学生",
        "image": "female-student.png",
        "color_body": (243, 127, 160),
        "color_skin": (242, 185, 138),
        "color_jeans": (101, 77, 139),
        "color_bag": (127, 207, 138),
        "color_hair": (49, 34, 60),
        "color_shoe": (47, 109, 178),
        "jump_mul": 1.04,
        "slide_mul": 1.04,
        "speed_mul": 1.0,
        "desc": "二段跳更轻盈，适合复杂路线。",
    },
]

# ═══════════════════════════════════════════════════════════════════
#  GAME MODES
# ═══════════════════════════════════════════════════════════════════

MODE_LIST = [
    {
        "id": "endless",
        "name": "无尽模式",
        "desc": "一直跑，越跑越快。",
        "detail": "速度曲线参考 Campus Rush，障碍会随着分数逐渐变密。",
        "image": "endless.jpg",
    },
    {
        "id": "timed",
        "name": "限时模式",
        "desc": "60 秒内到达终点。",
        "detail": "共 10 个关卡，长度和奖励参考课设版本。",
        "image": "timed.jpg",
    },
]

SHOP_ITEMS = [
    {
        "id": "umbrella",
        "name": "太阳伞",
        "image": "umbrella.png",
        "price": 80,
        "desc": "抵挡一次伤害，早八路上多一层体面。",
        "effect": "shield",
    },
    {
        "id": "coffee",
        "name": "提神咖啡",
        "image": "coffee.png",
        "price": 120,
        "desc": "短时间加速，困意先放一边。",
        "effect": "speed",
    },
    {
        "id": "notes",
        "name": "学霸笔记",
        "image": "notes.png",
        "price": 150,
        "desc": "收集附近金币，知识改变钱包。",
        "effect": "magnet",
    },
    {
        "id": "studentId",
        "name": "学生证",
        "image": "student-id.png",
        "price": 180,
        "desc": "增加一条额外生命，证明你还能抢救。",
        "effect": "life",
    },
    {
        "id": "alarm",
        "name": "闹钟",
        "image": "alarm.png",
        "price": 140,
        "desc": "暂停时间数秒，给灵魂一点缓冲。",
        "effect": "freeze",
    },
    {
        "id": "ebike",
        "name": "电动车",
        "image": "ebike.png",
        "price": 260,
        "desc": "短时间冲刺，并无视部分障碍。",
        "effect": "dash",
    },
]

LEVEL_LIST = [
    {
        "id": index + 1,
        "name": f"第{index + 1}关",
        "length": 700 + (index + 1) * 118 + index * index * 32,
        "reward": 35 + (index + 1) * 16,
    }
    for index in range(10)
]

CHALLENGE_LIMIT = 60
METER_PIXELS = 18

TEACHER_QUOTES = [
    "你又不上早八！",
    "早八对你来说是传说吗？",
    "你这学期签到率危险了。",
    "老师已经记住你了。",
    "你是不是又睡过头了？",
    "你的床封印了你吗？",
    "你和教室是不是异地恋？",
    "今天又准备补考吗？",
    "迟到大王就是你吧？",
    "早八：终究是错付了。",
]

NICKNAME_PREFIXES = [
    "晨跑", "困困", "闪电", "奶茶", "风一样", "早八", "不迟到", "冲刺", "元气", "铃声",
]
NICKNAME_NAMES = [
    "小王", "阿星", "同学", "学霸", "课代表", "干饭人", "小太阳", "追风者", "小橙", "小鹿",
]

# ═══════════════════════════════════════════════════════════════════
#  MENU / UI COLORS
# ═══════════════════════════════════════════════════════════════════

MENU_BG = (255, 242, 185)
MENU_BTN_NORMAL = (255, 181, 76)
MENU_BTN_HOVER = (255, 220, 91)
MENU_BTN_TEXT = (255, 255, 255)
MENU_BTN_DISABLED = (100, 100, 120)
MENU_TITLE_COLOR = (80, 50, 33)
MENU_ACCENT = (255, 96, 121)
MENU_SUBTLE = (92, 91, 77)
MENU_CARD_BG = (255, 255, 255, 25)
MENU_OVERLAY = (0, 0, 0, 140)
MENU_DANGER = (220, 60, 60)
