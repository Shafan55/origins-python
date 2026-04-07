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
)


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


def test_legal_moves_exist_for_player_1_on_8x8():
    game = Game(board_size=8)
    legal_moves = game.get_legal_moves()
    assert len(legal_moves) > 0


def test_4x4_environment_reset_returns_valid_state():
    env = OriginsEnv(board_size=4)
    state = env.reset()

    assert isinstance(state, tuple)
    assert len(state) == 17


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
    assert len(next_state) == 17
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert isinstance(info, dict)
    assert "success" in info
    assert "current_player" in info
    assert "winner" in info
    assert "steps" in info


def test_illegal_move_fails():
    game = Game(board_size=4)
    moved, reward = game.make_move(0, 0, 3, 3)

    assert moved is False
    assert reward == ILLEGAL_MOVE_PENALTY
    assert game.current_player == PLAYER_1


def test_element_move_can_convert_neutral_tile():
    game = Game(board_size=8)

    # clear board
    game.board.reset()

    element_piece = None
    for row in range(game.board.size):
        for col in range(game.board.size):
            piece = game.board.get_piece(row, col)
            if piece is not None and piece.owner == PLAYER_1 and piece.piece_type == ELEMENT_PIECE:
                element_piece = piece

    if element_piece is None:
        element_piece = game.board.get_piece(0, 2)
    if element_piece is None:
        from src.pieces import Piece
        from src.constants import PLAYER_1_ELEMENT_SYMBOL, EARTH
        element_piece = Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_ELEMENT_SYMBOL, element=EARTH)

    game.board.place_piece(3, 3, element_piece)
    game.board.set_tile(4, 3, NEUTRAL_TILE)
    game.board.set_tile(5, 3, NEUTRAL_TILE)

    moved, reward = game.make_move(3, 3, 5, 3)

    assert moved is True
    assert game.board.get_tile(4, 3) == EARTH_TILE


def test_element_move_can_capture_weaker_element_on_path():
    game = Game(board_size=8)
    game.board.reset()

    from src.pieces import Piece
    from src.constants import (
        PLAYER_1_ELEMENT_SYMBOL,
        PLAYER_2_ELEMENT_SYMBOL,
        EARTH,
        WATER,
    )

    attacker = Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_ELEMENT_SYMBOL, element=EARTH)
    victim = Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_ELEMENT_SYMBOL, element=WATER)

    game.board.place_piece(3, 3, attacker)
    game.board.place_piece(4, 3, victim)
    game.board.set_tile(4, 3, EARTH_TILE)

    moved, reward = game.make_move(3, 3, 5, 3)

    assert moved is True
    assert game.board.get_piece(4, 3) is None


def test_player_1_wins_when_both_humans_reach_destination():
    game = Game(board_size=8)
    game.board.reset()

    from src.pieces import Piece
    from src.constants import PLAYER_1_MALE_SYMBOL, PLAYER_1_FEMALE_SYMBOL

    male = Piece(MALE_PIECE, PLAYER_1, PLAYER_1_MALE_SYMBOL)
    female = Piece(FEMALE_PIECE, PLAYER_1, PLAYER_1_FEMALE_SYMBOL)

    game.board.place_piece(7, 0, male)
    game.board.place_piece(7, 1, female)

    game.check_winner()

    assert game.game_over is True
    assert game.winner == PLAYER_1


def test_draw_when_both_players_lose_required_humans():
    game = Game(board_size=8)
    game.board.reset()

    game.check_winner()

    assert game.game_over is True
    assert game.winner is None