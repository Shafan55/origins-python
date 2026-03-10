from src.game import Game
from src.constants import PLAYER_1, PLAYER_2, NORMAL_MOVE_REWARD, ILLEGAL_MOVE_PENALTY


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