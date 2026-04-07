BOARD_SIZE = 8

PLAYER_1 = "Player1"
PLAYER_2 = "Player2"

EMPTY = None

# Current prototype piece type
BASIC_PIECE = "Basic"

# Future Origins piece types
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

# Symbols for current prototype
PLAYER_1_SYMBOL = "A"
PLAYER_2_SYMBOL = "B"

# Future symbols (for later use)
PLAYER_1_MALE_SYMBOL = "M"
PLAYER_1_FEMALE_SYMBOL = "F"
PLAYER_1_EARTH_SYMBOL = "E"
PLAYER_1_WATER_SYMBOL = "W"
PLAYER_1_FIRE_SYMBOL = "R"
PLAYER_1_AIR_SYMBOL = "I"

PLAYER_2_MALE_SYMBOL = "m"
PLAYER_2_FEMALE_SYMBOL = "f"
PLAYER_2_EARTH_SYMBOL = "e"
PLAYER_2_WATER_SYMBOL = "w"
PLAYER_2_FIRE_SYMBOL = "r"
PLAYER_2_AIR_SYMBOL = "i"

# Rewards
WIN_REWARD = 10
ILLEGAL_MOVE_PENALTY = -5
NORMAL_MOVE_REWARD = 0