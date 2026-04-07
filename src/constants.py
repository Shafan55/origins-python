# =========================================
# Board configuration
# =========================================
BOARD_SIZE = 8


# =========================================
# Players
# =========================================
PLAYER_1 = "Player1"
PLAYER_2 = "Player2"


# =========================================
# Piece types
# =========================================
MALE_PIECE = "male"
FEMALE_PIECE = "female"
ELEMENT_PIECE = "element"


# =========================================
# Elements
# =========================================
EARTH = "earth"
WATER = "water"
FIRE = "fire"
AIR = "air"

ELEMENTS = [EARTH, WATER, FIRE, AIR]


# =========================================
# Tile types
# =========================================
NEUTRAL_TILE = "neutral"
EARTH_TILE = "earth"
WATER_TILE = "water"
FIRE_TILE = "fire"
AIR_TILE = "air"

TILE_TYPES = [
    NEUTRAL_TILE,
    EARTH_TILE,
    WATER_TILE,
    FIRE_TILE,
    AIR_TILE,
]


# =========================================
# Display symbols
# =========================================
PLAYER_1_MALE_SYMBOL = "M"
PLAYER_1_FEMALE_SYMBOL = "F"
PLAYER_1_ELEMENT_SYMBOL = "E"

PLAYER_2_MALE_SYMBOL = "m"
PLAYER_2_FEMALE_SYMBOL = "f"
PLAYER_2_ELEMENT_SYMBOL = "e"


# =========================================
# Rewards
# =========================================
WIN_REWARD = 10
NORMAL_MOVE_REWARD = 0
ILLEGAL_MOVE_PENALTY = -5


# =========================================
# RL / environment defaults
# =========================================
PROTOTYPE_BOARD_SIZE = 4
FULL_GAME_BOARD_SIZE = 8
PROTOTYPE_MAX_STEPS = 40
FULL_GAME_MAX_STEPS = 100