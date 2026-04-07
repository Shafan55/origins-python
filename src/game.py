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
        self.steps = 0
        self.max_steps = 50
        self.setup_board()

    def reset(self) -> None:
        self.board = Board(size=self.board_size)
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None
        self.steps = 0
        self.setup_board()

    def setup_board(self) -> None:
        last = self.board.size - 1

        # Player 1 pieces (top row)
        self.board.place_piece(0, 0, Piece(MALE_PIECE, PLAYER_1, PLAYER_1_MALE_SYMBOL))
        self.board.place_piece(0, 1, Piece(FEMALE_PIECE, PLAYER_1, PLAYER_1_FEMALE_SYMBOL))
        self.board.place_piece(
            0,
            2,
            Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_ELEMENT_SYMBOL, element="earth"),
        )

        # Player 2 pieces (bottom row)
        self.board.place_piece(last, last, Piece(MALE_PIECE, PLAYER_2, PLAYER_2_MALE_SYMBOL))
        self.board.place_piece(last, last - 1, Piece(FEMALE_PIECE, PLAYER_2, PLAYER_2_FEMALE_SYMBOL))
        self.board.place_piece(
            last,
            last - 2,
            Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_ELEMENT_SYMBOL, element="earth"),
        )

    def switch_turn(self) -> None:
        if self.current_player == PLAYER_1:
            self.current_player = PLAYER_2
        else:
            self.current_player = PLAYER_1

    def check_winner(self) -> None:
        """
        Prototype win rule:
        - Player 1 wins if male OR female reaches the bottom row
        - Player 2 wins if male OR female reaches the top row
        """
        last = self.board.size - 1

        for col in range(self.board.size):
            top_piece = self.board.get_piece(0, col)
            bottom_piece = self.board.get_piece(last, col)

            # Player 1 goal = bottom row
            if bottom_piece and bottom_piece.owner == PLAYER_1:
                if bottom_piece.piece_type in (MALE_PIECE, FEMALE_PIECE):
                    self.game_over = True
                    self.winner = PLAYER_1
                    return

            # Player 2 goal = top row
            if top_piece and top_piece.owner == PLAYER_2:
                if top_piece.piece_type in (MALE_PIECE, FEMALE_PIECE):
                    self.game_over = True
                    self.winner = PLAYER_2
                    return

    def check_no_moves_draw(self) -> None:
        """
        If the current player has no legal moves, the game is a draw.
        """
        if self.game_over:
            return

        legal_moves = get_legal_moves_for_player(self.board, self.current_player)
        if not legal_moves:
            self.game_over = True
            self.winner = None

    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        if self.game_over:
            return False, 0

        piece = self.board.get_piece(from_row, from_col)

        # Prevent invalid selection
        if piece is None or piece.owner != self.current_player:
            return False, ILLEGAL_MOVE_PENALTY

        # Check legality
        if not is_legal_move(
            self.board, from_row, from_col, to_row, to_col, self.current_player
        ):
            return False, ILLEGAL_MOVE_PENALTY

        # Apply move
        self.board.move_piece(from_row, from_col, to_row, to_col)
        self.steps += 1

        # Check winner after move
        self.check_winner()
        if self.game_over:
            return True, WIN_REWARD

        # Max step termination
        if self.steps >= self.max_steps:
            self.game_over = True
            self.winner = None
            return True, 0

        # Switch turn
        self.switch_turn()

        # Check whether the next player has no legal moves
        self.check_no_moves_draw()
        if self.game_over:
            return True, 0

        return True, NORMAL_MOVE_REWARD

    def get_legal_moves(self):
        return get_legal_moves_for_player(self.board, self.current_player)

    def is_terminal(self):
        if not self.game_over:
            self.check_no_moves_draw()
        return self.game_over

    def display(self) -> None:
        print(f"\nCurrent player: {self.current_player}")
        self.board.display()

        if self.game_over:
            if self.winner is None:
                print("Game Over! Result: Draw")
            else:
                print(f"Game Over! Winner: {self.winner}")