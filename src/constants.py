BOARD_SIZE = 8

PLAYER_1 = "Player1"
PLAYER_2 = "Player2"

EMPTY = None

# Current / transitional prototype piece types
BASIC_PIECE = "Basic"
HUMAN_PIECE = "human"
MALE_PIECE = "male"
FEMALE_PIECE = "female"
ELEMENT_PIECE = "element"

# Elements
EARTH = "earth"
WATER = "water"
FIRE = "fire"
AIR = "air"

ELEMENTS = [EARTH, WATER, FIRE, AIR]

# Tile types
NEUTRAL_TILE = "neutral"
EARTH_TILE = "earth"
WATER_TILE = "water"
FIRE_TILE = "fire"
AIR_TILE = "air"

TILE_TYPES = [NEUTRAL_TILE, EARTH_TILE, WATER_TILE, FIRE_TILE, AIR_TILE]

# Symbols for current simplified prototype
PLAYER_1_SYMBOL = "A"
PLAYER_2_SYMBOL = "B"

# Multi-piece prototype symbols
PLAYER_1_MALE_SYMBOL = "M"
PLAYER_1_FEMALE_SYMBOL = "F"
PLAYER_1_ELEMENT_SYMBOL = "E"

PLAYER_2_MALE_SYMBOL = "m"
PLAYER_2_FEMALE_SYMBOL = "f"
PLAYER_2_ELEMENT_SYMBOL = "e"

# Rewards
WIN_REWARD = 10
ILLEGAL_MOVE_PENALTY = -5
NORMAL_MOVE_REWARD = 0