from src.game import Game
from src.environment import OriginsEnv
from src.constants import (
    PLAYER_1,
    PLAYER_2,
    NORMAL_MOVE_REWARD,
    ILLEGAL_MOVE_PENALTY,
    WIN_REWARD,
    MALE_PIECE,
    FEMALE_PIECE,
    ELEMENT_PIECE,
    NEUTRAL_TILE,
    EARTH_TILE,
    WATER_TILE,
    FIRE_TILE,
    AIR_TILE,
    EARTH,
    WATER,
    PLAYER_1_MALE_SYMBOL,
    PLAYER_1_FEMALE_SYMBOL,
    PLAYER_1_ELEMENT_SYMBOL,
    PLAYER_2_ELEMENT_SYMBOL,
)
from src.pieces import Piece




def test_game_starts_with_player_1():
    game = Game(board_size=8)
    assert game.current_player == PLAYER_1


def test_initial_piece_positions_8x8():
    game = Game(board_size=8)
    player_1_count = 0
    player_2_count = 0

    for row in range(game.board.size):
        for col in range(game.board.size):
            piece = game.board.get_piece(row, col)
            if piece is None:
                continue
            if piece.owner == PLAYER_1:
                player_1_count += 1
            elif piece.owner == PLAYER_2:
                player_2_count += 1

    assert player_1_count == 10
    assert player_2_count == 10


def test_board_has_tiles_8x8():
    game = Game(board_size=8)
    for row in range(game.board.size):
        for col in range(game.board.size):
            tile = game.board.get_tile(row, col)
            assert tile is not None


def test_4x4_board_has_tiles():
    """4x4 board must have tiles so human pieces can move."""
    game = Game(board_size=4)
    has_element_tile = False
    for row in range(game.board.size):
        for col in range(game.board.size):
            tile = game.board.get_tile(row, col)
            assert tile is not None
            if tile != NEUTRAL_TILE:
                has_element_tile = True
    assert has_element_tile, "4x4 board should have at least one element tile"


def test_legal_moves_exist_for_player_1_on_8x8():
    game = Game(board_size=8)
    legal_moves = game.get_legal_moves()
    assert len(legal_moves) > 0


def test_legal_moves_exist_for_player_1_on_4x4():
    game = Game(board_size=4)
    legal_moves = game.get_legal_moves()
    assert len(legal_moves) > 0




def test_4x4_environment_reset_returns_valid_state():
    env = OriginsEnv(board_size=4)
    state = env.reset()
    assert isinstance(state, tuple)
    assert len(state) == 17  


def test_8x8_environment_reset_returns_valid_state():
    env = OriginsEnv(board_size=8, include_tile_state=True)
    state = env.reset()
    assert isinstance(state, tuple)
    
    assert len(state) == 129


def test_4x4_environment_returns_valid_actions():
    env = OriginsEnv(board_size=4)
    env.reset()
    actions = env.get_valid_actions()
    assert isinstance(actions, list)
    assert len(actions) > 0
    assert all(len(action) == 4 for action in actions)


def test_4x4_environment_step_returns_correct_format():
    env = OriginsEnv(board_size=4)
    env.reset()
    actions = env.get_valid_actions()

    next_state, reward, done, info = env.step(actions[0])

    assert isinstance(next_state, tuple)
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert isinstance(info, dict)
    assert "success"        in info
    assert "current_player" in info
    assert "winner"         in info
    assert "steps"          in info




def test_illegal_move_fails():
    game = Game(board_size=4)
    moved, reward = game.make_move(0, 0, 3, 3)
    assert moved is False
    assert reward == ILLEGAL_MOVE_PENALTY
    assert game.current_player == PLAYER_1


def test_human_cannot_move_within_starting_row():
    """Human pieces cannot move horizontally within their starting row."""
    game = Game(board_size=8)
    
    moved, reward = game.make_move(0, 0, 0, 1)
    assert moved is False
    assert reward == ILLEGAL_MOVE_PENALTY


def test_human_cannot_move_backward():
    """Human pieces cannot move backward toward their starting row."""
    game = Game(board_size=8)
    game.board.reset()
    game.setup_tiles()

    male = Piece(MALE_PIECE, PLAYER_1, PLAYER_1_MALE_SYMBOL)
    game.board.place_piece(3, 3, male)
    game.board.set_tile(2, 3, EARTH_TILE)

    moved, reward = game.make_move(3, 3, 2, 3)
    assert moved is False
    assert reward == ILLEGAL_MOVE_PENALTY


def test_human_cannot_return_to_starting_row():
    """Human piece that has left the starting row cannot return to it."""
    game = Game(board_size=8)
    game.board.reset()
    game.setup_tiles()

    male = Piece(MALE_PIECE, PLAYER_1, PLAYER_1_MALE_SYMBOL)
    game.board.place_piece(2, 3, male)
    game.board.set_tile(0, 3, EARTH_TILE)

    moved, reward = game.make_move(2, 3, 0, 3)
    assert moved is False
    assert reward == ILLEGAL_MOVE_PENALTY


def test_element_cannot_move_within_starting_row():
    """Element pieces cannot move horizontally within their starting row."""
    game = Game(board_size=8)
    
    moved, reward = game.make_move(0, 2, 0, 5)
    assert moved is False
    assert reward == ILLEGAL_MOVE_PENALTY




def test_element_move_converts_neutral_tile():
    """Element moving over neutral squares converts them to its element type."""
    game = Game(board_size=8)
    game.board.reset()
    game.setup_tiles()

    attacker = Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_ELEMENT_SYMBOL, element=EARTH)
    game.board.place_piece(1, 3, attacker)
    game.board.set_tile(2, 3, NEUTRAL_TILE)
    game.board.set_tile(3, 3, NEUTRAL_TILE)
    game.board.set_tile(4, 3, NEUTRAL_TILE)

    moved, reward = game.make_move(1, 3, 4, 3)

    assert moved is True
    assert game.board.get_tile(2, 3) == EARTH_TILE
    assert game.board.get_tile(3, 3) == EARTH_TILE


def test_element_move_captures_weaker_element_on_path():
    """Dominant element captures weaker element pieces it passes over."""
    game = Game(board_size=8)
    game.board.reset()
    game.setup_tiles()

    attacker = Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_ELEMENT_SYMBOL, element=EARTH)
    victim   = Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_ELEMENT_SYMBOL, element=WATER)

    game.board.place_piece(1, 3, attacker)
    game.board.place_piece(3, 3, victim)
    game.board.set_tile(2, 3, NEUTRAL_TILE)
    game.board.set_tile(3, 3, WATER_TILE)
    game.board.set_tile(4, 3, NEUTRAL_TILE)

    moved, reward = game.make_move(1, 3, 4, 3)

    assert moved is True
    assert game.board.get_piece(3, 3) is None


def test_equal_elements_cannot_pass_each_other():
    """Equal elements (Earth/Fire or Water/Air) cannot pass through each other."""
    game = Game(board_size=8)
    game.board.reset()
    game.setup_tiles()

    from src.constants import FIRE, FIRE_TILE
    attacker = Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_ELEMENT_SYMBOL, element=EARTH)
    blocker  = Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_ELEMENT_SYMBOL, element=FIRE)

    game.board.place_piece(1, 3, attacker)
    game.board.place_piece(3, 3, blocker)
    game.board.set_tile(2, 3, NEUTRAL_TILE)
    game.board.set_tile(3, 3, FIRE_TILE)

    moved, reward = game.make_move(1, 3, 4, 3)
    assert moved is False




def test_player_1_wins_when_both_humans_reach_destination():
    game = Game(board_size=8)
    game.board.reset()

    male   = Piece(MALE_PIECE,   PLAYER_1, PLAYER_1_MALE_SYMBOL)
    female = Piece(FEMALE_PIECE, PLAYER_1, PLAYER_1_FEMALE_SYMBOL)

    game.board.place_piece(7, 0, male)
    game.board.place_piece(7, 1, female)

    game.check_winner()

    assert game.game_over is True
    assert game.winner == PLAYER_1


def test_player_2_wins_when_both_humans_reach_destination():
    from src.constants import PLAYER_2_MALE_SYMBOL, PLAYER_2_FEMALE_SYMBOL
    game = Game(board_size=8)
    game.board.reset()

    male   = Piece(MALE_PIECE,   PLAYER_2, PLAYER_2_MALE_SYMBOL)
    female = Piece(FEMALE_PIECE, PLAYER_2, PLAYER_2_FEMALE_SYMBOL)

    game.board.place_piece(0, 0, male)
    game.board.place_piece(0, 1, female)

    game.check_winner()

    assert game.game_over is True
    assert game.winner == PLAYER_2


def test_draw_when_both_players_lose_humans():
    """If both players lose all human pieces it is a draw."""
    game = Game(board_size=8)
    game.board.reset()

    game.check_winner()

    assert game.game_over is True
    assert game.winner is None


def test_player_wins_when_opponent_loses_humans():
    """If only one player loses their humans the other player wins."""
    from src.constants import PLAYER_2_MALE_SYMBOL, PLAYER_2_FEMALE_SYMBOL
    game = Game(board_size=8)
    game.board.reset()

    
    male   = Piece(MALE_PIECE,   PLAYER_2, PLAYER_2_MALE_SYMBOL)
    female = Piece(FEMALE_PIECE, PLAYER_2, PLAYER_2_FEMALE_SYMBOL)
    game.board.place_piece(4, 4, male)
    game.board.place_piece(4, 5, female)

    game.check_winner()

    assert game.game_over is True
    assert game.winner == PLAYER_2




def test_game_state_export():
    """Game state export should return all required keys for Unity."""
    game = Game(board_size=8)
    state = game.get_game_state_for_export()

    assert "board_size"      in state
    assert "current_player"  in state
    assert "game_over"       in state
    assert "winner"          in state
    assert "steps"           in state
    assert "max_steps"       in state
    assert "pieces"          in state
    assert "tiles"           in state
    assert state["board_size"] == 8
    assert len(state["pieces"]) == 8
    assert len(state["tiles"])  == 8