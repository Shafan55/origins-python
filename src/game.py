from src.board import Board
from src.pieces import Piece
from src.rules import is_legal_move, get_legal_moves_for_player
from src.constants import (
    PLAYER_1,
    PLAYER_2,
    MALE_PIECE,
    FEMALE_PIECE,
    ELEMENT_PIECE,
    PLAYER_1_MALE_SYMBOL,
    PLAYER_1_FEMALE_SYMBOL,
    PLAYER_1_ELEMENT_SYMBOL,
    PLAYER_2_MALE_SYMBOL,
    PLAYER_2_FEMALE_SYMBOL,
    PLAYER_2_ELEMENT_SYMBOL,
    WIN_REWARD,
    ILLEGAL_MOVE_PENALTY,
    NORMAL_MOVE_REWARD,
)


class Game:
    def __init__(self, board_size: int = 8):
        self.board_size = board_size
        self.board = Board(size=board_size)
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None
        self.setup_board()

    def reset(self) -> None:
        self.board = Board(size=self.board_size)
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None
        self.setup_board()

    def setup_board(self) -> None:
        last_index = self.board.size - 1

        # Player 1 pieces on top row
        self.board.place_piece(0, 0, Piece(MALE_PIECE, PLAYER_1, PLAYER_1_MALE_SYMBOL))
        self.board.place_piece(0, 1, Piece(FEMALE_PIECE, PLAYER_1, PLAYER_1_FEMALE_SYMBOL))
        self.board.place_piece(0, 2, Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_ELEMENT_SYMBOL, element="earth"))

        # Player 2 pieces on bottom row
        self.board.place_piece(last_index, last_index, Piece(MALE_PIECE, PLAYER_2, PLAYER_2_MALE_SYMBOL))
        self.board.place_piece(last_index, last_index - 1, Piece(FEMALE_PIECE, PLAYER_2, PLAYER_2_FEMALE_SYMBOL))
        self.board.place_piece(last_index, last_index - 2, Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_ELEMENT_SYMBOL, element="earth"))

    def switch_turn(self) -> None:
        if self.current_player == PLAYER_1:
            self.current_player = PLAYER_2
        else:
            self.current_player = PLAYER_1

    def check_winner(self) -> None:
        last_index = self.board.size - 1

        top_left = self.board.get_piece(0, 0)
        bottom_right = self.board.get_piece(last_index, last_index)

        if bottom_right is not None and bottom_right.owner == PLAYER_1:
            self.game_over = True
            self.winner = PLAYER_1

        elif top_left is not None and top_left.owner == PLAYER_2:
            self.game_over = True
            self.winner = PLAYER_2

    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        if self.game_over:
            return False, 0

        if not is_legal_move(
            self.board, from_row, from_col, to_row, to_col, self.current_player
        ):
            return False, ILLEGAL_MOVE_PENALTY

        self.board.move_piece(from_row, from_col, to_row, to_col)
        self.check_winner()

        if self.game_over:
            return True, WIN_REWARD

        self.switch_turn()
        return True, NORMAL_MOVE_REWARD

    def get_legal_moves(self):
        return get_legal_moves_for_player(self.board, self.current_player)

    def display(self) -> None:
        print(f"\nCurrent player: {self.current_player}")
        self.board.display()

        if self.game_over:
            print(f"Game Over! Winner: {self.winner}")