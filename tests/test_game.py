from src.game import Game
from src.environment import OriginsEnv
from src.constants import (
    PLAYER_1,
    PLAYER_2,
    NORMAL_MOVE_REWARD,
    ILLEGAL_MOVE_PENALTY,
    WIN_REWARD,
)


def test_game_starts_with_player_1():
    game = Game(board_size=4)
    assert game.current_player == PLAYER_1


def test_initial_piece_positions():
    game = Game(board_size=4)
    assert game.board.get_piece(0, 0) is not None
    assert game.board.get_piece(3, 3) is not None


def test_legal_moves_exist_for_player_1():
    game = Game(board_size=4)
    legal_moves = game.get_legal_moves()
    assert len(legal_moves) > 0


def test_successful_move_switches_turn():
    game = Game(board_size=4)
    moved, reward = game.make_move(0, 0, 1, 1)

    assert moved is True
    assert reward == NORMAL_MOVE_REWARD
    assert game.current_player == PLAYER_2


def test_illegal_move_fails():
    game = Game(board_size=4)
    moved, reward = game.make_move(0, 0, 3, 3)

    assert moved is False
    assert reward == ILLEGAL_MOVE_PENALTY
    assert game.current_player == PLAYER_1


def test_environment_reset_returns_valid_state():
    env = OriginsEnv(board_size=4)
    state = env.reset()

    assert isinstance(state, tuple)
    assert len(state) == 16
    assert state.count(1) == 1
    assert state.count(2) == 1


def test_environment_returns_valid_actions():
    env = OriginsEnv(board_size=4)
    env.reset()
    actions = env.get_valid_actions()

    assert isinstance(actions, list)
    assert len(actions) > 0
    assert all(len(action) == 4 for action in actions)


def test_environment_step_returns_correct_format():
    env = OriginsEnv(board_size=4)
    env.reset()
    actions = env.get_valid_actions()

    next_state, reward, done, info = env.step(actions[0])

    assert isinstance(next_state, tuple)
    assert len(next_state) == 16
    assert isinstance(reward, int)
    assert isinstance(done, bool)
    assert isinstance(info, dict)
    assert "success" in info


def test_winning_move_sets_game_over_and_winner():
    game = Game(board_size=4)

    # Move Player 1 piece near goal
    piece = game.board.get_piece(0, 0)
    game.board.grid[0][0] = None
    game.board.grid[2][2] = piece

    # Clear goal square
    game.board.grid[3][3] = None

    moved, reward = game.make_move(2, 2, 3, 3)

    assert moved is True
    assert reward == WIN_REWARD
    assert game.game_over is True
    assert game.winner == PLAYER_1


def test_environment_step_sets_done_true_on_win():
    env = OriginsEnv(board_size=4)

    # Move Player 1 piece near goal
    piece = env.game.board.get_piece(0, 0)
    env.game.board.grid[0][0] = None
    env.game.board.grid[2][2] = piece

    # Clear goal square
    env.game.board.grid[3][3] = None

    next_state, reward, done, info = env.step((2, 2, 3, 3))

    assert reward == WIN_REWARD
    assert done is True
    assert info["success"] is True