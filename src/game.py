from src.board import Board
from src.pieces import Piece
from src.rules import (
    is_legal_move,
    get_legal_moves_for_player,
    get_path_squares,
    is_element_piece,
    is_human_piece,
    element_dominates,
    elements_are_equal,
    get_tile_element,
    ELEMENT_TO_TILE,
)
from src.constants import (
    PLAYER_1,
    PLAYER_2,
    MALE_PIECE,
    FEMALE_PIECE,
    ELEMENT_PIECE,
    EARTH,
    WATER,
    FIRE,
    AIR,
    PLAYER_1_MALE_SYMBOL,
    PLAYER_1_FEMALE_SYMBOL,
    PLAYER_1_EARTH_SYMBOL,
    PLAYER_1_WATER_SYMBOL,
    PLAYER_1_FIRE_SYMBOL,
    PLAYER_1_AIR_SYMBOL,
    PLAYER_2_MALE_SYMBOL,
    PLAYER_2_FEMALE_SYMBOL,
    PLAYER_2_EARTH_SYMBOL,
    PLAYER_2_WATER_SYMBOL,
    PLAYER_2_FIRE_SYMBOL,
    PLAYER_2_AIR_SYMBOL,
    WIN_REWARD,
    ILLEGAL_MOVE_PENALTY,
    NORMAL_MOVE_REWARD,
    EARTH_TILE,
    WATER_TILE,
    FIRE_TILE,
    AIR_TILE,
    NEUTRAL_TILE,
    PROTOTYPE_MAX_STEPS,
    FULL_GAME_MAX_STEPS,
)


class Game:
    def __init__(self, board_size: int = 8):
        self.board_size = board_size
        self.board = Board(size=board_size)
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None
        self.steps = 0
        self.max_steps = (
            FULL_GAME_MAX_STEPS if board_size == 8 else PROTOTYPE_MAX_STEPS
        )
        self.reset()

    def reset(self) -> None:
        self.board = Board(size=self.board_size)
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None
        self.steps = 0
        self.setup_tiles()
        self.setup_board()

    def setup_tiles(self) -> None:
        if self.board.size == 8:
            tile_layout = [
                [EARTH_TILE, NEUTRAL_TILE, WATER_TILE, NEUTRAL_TILE, FIRE_TILE,  NEUTRAL_TILE, AIR_TILE,   NEUTRAL_TILE],
                [NEUTRAL_TILE, EARTH_TILE, NEUTRAL_TILE, WATER_TILE, NEUTRAL_TILE, FIRE_TILE,  NEUTRAL_TILE, AIR_TILE  ],
                [FIRE_TILE,  NEUTRAL_TILE, AIR_TILE,   NEUTRAL_TILE, EARTH_TILE, NEUTRAL_TILE, WATER_TILE, NEUTRAL_TILE],
                [NEUTRAL_TILE, FIRE_TILE,  NEUTRAL_TILE, AIR_TILE,   NEUTRAL_TILE, EARTH_TILE, NEUTRAL_TILE, WATER_TILE],
                [EARTH_TILE, NEUTRAL_TILE, WATER_TILE, NEUTRAL_TILE, FIRE_TILE,  NEUTRAL_TILE, AIR_TILE,   NEUTRAL_TILE],
                [NEUTRAL_TILE, EARTH_TILE, NEUTRAL_TILE, WATER_TILE, NEUTRAL_TILE, FIRE_TILE,  NEUTRAL_TILE, AIR_TILE  ],
                [FIRE_TILE,  NEUTRAL_TILE, AIR_TILE,   NEUTRAL_TILE, EARTH_TILE, NEUTRAL_TILE, WATER_TILE, NEUTRAL_TILE],
                [NEUTRAL_TILE, FIRE_TILE,  NEUTRAL_TILE, AIR_TILE,   NEUTRAL_TILE, EARTH_TILE, NEUTRAL_TILE, WATER_TILE],
            ]
        else:
            tile_layout = [
                [EARTH_TILE,  NEUTRAL_TILE, WATER_TILE,  NEUTRAL_TILE],
                [NEUTRAL_TILE, FIRE_TILE,  NEUTRAL_TILE, AIR_TILE    ],
                [AIR_TILE,   NEUTRAL_TILE, FIRE_TILE,   NEUTRAL_TILE ],
                [NEUTRAL_TILE, WATER_TILE, NEUTRAL_TILE, EARTH_TILE  ],
            ]

        for row in range(self.board.size):
            for col in range(self.board.size):
                self.board.set_tile(row, col, tile_layout[row][col])

    def setup_board(self) -> None:
        last = self.board.size - 1

        if self.board.size == 8:
            player_1_pieces = [
                Piece(MALE_PIECE,    PLAYER_1, PLAYER_1_MALE_SYMBOL),
                Piece(FEMALE_PIECE,  PLAYER_1, PLAYER_1_FEMALE_SYMBOL),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_EARTH_SYMBOL, element=EARTH),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_EARTH_SYMBOL, element=EARTH),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_WATER_SYMBOL, element=WATER),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_WATER_SYMBOL, element=WATER),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_FIRE_SYMBOL,  element=FIRE),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_FIRE_SYMBOL,  element=FIRE),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_AIR_SYMBOL,   element=AIR),
                Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_AIR_SYMBOL,   element=AIR),
            ]

            player_2_pieces = [
                Piece(MALE_PIECE,    PLAYER_2, PLAYER_2_MALE_SYMBOL),
                Piece(FEMALE_PIECE,  PLAYER_2, PLAYER_2_FEMALE_SYMBOL),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_EARTH_SYMBOL, element=EARTH),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_EARTH_SYMBOL, element=EARTH),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_WATER_SYMBOL, element=WATER),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_WATER_SYMBOL, element=WATER),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_FIRE_SYMBOL,  element=FIRE),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_FIRE_SYMBOL,  element=FIRE),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_AIR_SYMBOL,   element=AIR),
                Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_AIR_SYMBOL,   element=AIR),
            ]

            player_1_positions = [
                (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                (0, 5), (0, 6), (0, 7), (1, 3), (1, 4),
            ]

            player_2_positions = [
                (7, 7), (7, 6), (7, 5), (7, 4), (7, 3),
                (7, 2), (7, 1), (7, 0), (6, 4), (6, 3),
            ]

            for piece, (row, col) in zip(player_1_pieces, player_1_positions):
                self.board.place_piece(row, col, piece)

            for piece, (row, col) in zip(player_2_pieces, player_2_positions):
                self.board.place_piece(row, col, piece)

        else:
            # 4x4 prototype setup
            self.board.place_piece(0, 0, Piece(MALE_PIECE,    PLAYER_1, PLAYER_1_MALE_SYMBOL))
            self.board.place_piece(0, 1, Piece(FEMALE_PIECE,  PLAYER_1, PLAYER_1_FEMALE_SYMBOL))
            self.board.place_piece(0, 2, Piece(ELEMENT_PIECE, PLAYER_1, PLAYER_1_EARTH_SYMBOL, element=EARTH))

            self.board.place_piece(last, last,     Piece(MALE_PIECE,    PLAYER_2, PLAYER_2_MALE_SYMBOL))
            self.board.place_piece(last, last - 1, Piece(FEMALE_PIECE,  PLAYER_2, PLAYER_2_FEMALE_SYMBOL))
            self.board.place_piece(last, last - 2, Piece(ELEMENT_PIECE, PLAYER_2, PLAYER_2_EARTH_SYMBOL, element=EARTH))

    def switch_turn(self) -> None:
        self.current_player = PLAYER_2 if self.current_player == PLAYER_1 else PLAYER_1

    def destination_row_for_player(self, player: str) -> int:
        return self.board.size - 1 if player == PLAYER_1 else 0

    def is_human_locked_on_goal(self, row: int, col: int) -> bool:
        piece = self.board.get_piece(row, col)
        if piece is None or not is_human_piece(piece):
            return False
        return row == self.destination_row_for_player(piece.owner)

    def player_has_required_humans(self, player: str) -> bool:
        male_exists = False
        female_exists = False

        for row in range(self.board.size):
            for col in range(self.board.size):
                piece = self.board.get_piece(row, col)
                if piece is None or piece.owner != player:
                    continue
                if piece.piece_type == MALE_PIECE:
                    male_exists = True
                elif piece.piece_type == FEMALE_PIECE:
                    female_exists = True

        return male_exists and female_exists

    def humans_on_destination_row(self, player: str) -> tuple[bool, bool]:
        target_row = self.destination_row_for_player(player)
        male_on_goal = False
        female_on_goal = False

        for col in range(self.board.size):
            piece = self.board.get_piece(target_row, col)
            if piece is None or piece.owner != player:
                continue
            if piece.piece_type == MALE_PIECE:
                male_on_goal = True
            elif piece.piece_type == FEMALE_PIECE:
                female_on_goal = True

        return male_on_goal, female_on_goal

    def check_winner(self) -> None:
        p1_has_both = self.player_has_required_humans(PLAYER_1)
        p2_has_both = self.player_has_required_humans(PLAYER_2)

        if not p1_has_both and not p2_has_both:
            self.game_over = True
            self.winner = None
            return

        if not p1_has_both:
            self.game_over = True
            self.winner = PLAYER_2
            return

        if not p2_has_both:
            self.game_over = True
            self.winner = PLAYER_1
            return

        p1_male_goal, p1_female_goal = self.humans_on_destination_row(PLAYER_1)
        if p1_male_goal and p1_female_goal:
            self.game_over = True
            self.winner = PLAYER_1
            return

        p2_male_goal, p2_female_goal = self.humans_on_destination_row(PLAYER_2)
        if p2_male_goal and p2_female_goal:
            self.game_over = True
            self.winner = PLAYER_2
            return

    def check_no_moves_draw(self) -> None:
        if self.game_over:
            return
        legal_moves = get_legal_moves_for_player(self.board, self.current_player)
        if not legal_moves:
            self.game_over = True
            self.winner = None

    def neutralise_tile_and_capture_if_needed(self, row: int, col: int) -> None:
        piece = self.board.get_piece(row, col)
        if piece is not None and is_human_piece(piece):
            if not self.is_human_locked_on_goal(row, col):
                self.board.remove_piece(row, col)
        self.board.set_tile(row, col, NEUTRAL_TILE)

    def apply_element_effects_along_path(self, moving_piece, path) -> None:
        moving_element = moving_piece.element
        moving_tile = ELEMENT_TO_TILE[moving_element]

        for row, col in path:
            tile_type = self.board.get_tile(row, col)
            occupying_piece = self.board.get_piece(row, col)

            if tile_type == NEUTRAL_TILE:
                self.board.set_tile(row, col, moving_tile)
            else:
                tile_element = get_tile_element(tile_type)
                if tile_element is not None and element_dominates(moving_element, tile_element):
                    self.neutralise_tile_and_capture_if_needed(row, col)
                    occupying_piece = self.board.get_piece(row, col)

            if occupying_piece is not None and is_element_piece(occupying_piece):
                other_element = occupying_piece.element
                if (
                    other_element != moving_element
                    and not elements_are_equal(moving_element, other_element)
                    and element_dominates(moving_element, other_element)
                ):
                    self.board.remove_piece(row, col)

    def apply_element_effects_on_target(self, moving_piece, to_row: int, to_col: int) -> None:
        moving_element = moving_piece.element
        moving_tile = ELEMENT_TO_TILE[moving_element]

        target_tile = self.board.get_tile(to_row, to_col)

        if target_tile == NEUTRAL_TILE:
            self.board.set_tile(to_row, to_col, moving_tile)
        else:
            tile_element = get_tile_element(target_tile)
            if tile_element is not None and element_dominates(moving_element, tile_element):
                self.neutralise_tile_and_capture_if_needed(to_row, to_col)

        target_piece = self.board.get_piece(to_row, to_col)
        if target_piece is not None and is_element_piece(target_piece):
            if (
                target_piece.element != moving_element
                and element_dominates(moving_element, target_piece.element)
            ):
                self.board.remove_piece(to_row, to_col)

    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        if self.game_over:
            return False, 0

        piece = self.board.get_piece(from_row, from_col)

        if piece is None or piece.owner != self.current_player:
            return False, ILLEGAL_MOVE_PENALTY

        if not is_legal_move(
            self.board, from_row, from_col, to_row, to_col, self.current_player
        ):
            return False, ILLEGAL_MOVE_PENALTY

        if is_element_piece(piece):
            path = get_path_squares(from_row, from_col, to_row, to_col)
            if path is None:
                return False, ILLEGAL_MOVE_PENALTY

            self.apply_element_effects_along_path(piece, path)
            self.apply_element_effects_on_target(piece, to_row, to_col)

        self.board.move_piece(from_row, from_col, to_row, to_col)
        self.steps += 1

        self.check_winner()
        if self.game_over:
            return True, WIN_REWARD

        if self.steps >= self.max_steps:
            self.game_over = True
            self.winner = None
            return True, 0

        self.switch_turn()
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

    def get_game_state_for_export(self) -> dict:
        """
        Export full game state as dictionary.
        Designed for Unity integration via JSON serialisation.
        """
        board_state = []
        tile_state  = []

        for row in range(self.board.size):
            piece_row = []
            tile_row  = []
            for col in range(self.board.size):
                piece = self.board.get_piece(row, col)
                tile  = self.board.get_tile(row, col)

                if piece is None:
                    piece_row.append(None)
                else:
                    piece_row.append({
                        "type":    piece.piece_type,
                        "owner":   piece.owner,
                        "element": piece.element,
                        "symbol":  piece.symbol,
                    })

                tile_row.append(tile)

            board_state.append(piece_row)
            tile_state.append(tile_row)

        return {
            "board_size":     self.board_size,
            "current_player": self.current_player,
            "game_over":      self.game_over,
            "winner":         self.winner,
            "steps":          self.steps,
            "max_steps":      self.max_steps,
            "pieces":         board_state,
            "tiles":          tile_state,
        }

    def display(self) -> None:
        print(f"\nCurrent player: {self.current_player}")
        self.board.display()

        if self.game_over:
            if self.winner is None:
                print("Game Over! Result: Draw")
            else:
                print(f"Game Over! Winner: {self.winner}")