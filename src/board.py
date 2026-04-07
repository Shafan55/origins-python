from src.pieces import Piece
from src.constants import NEUTRAL_TILE


class Board:
    def __init__(self, size: int = 8):
        self.size = size
        self.piece_grid = [[None for _ in range(size)] for _ in range(size)]
        self.tile_grid = [
            [NEUTRAL_TILE for _ in range(size)] for _ in range(size)
        ]

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def is_empty(self, row: int, col: int) -> bool:
        return self.get_piece(row, col) is None

    def place_piece(self, row: int, col: int, piece: Piece) -> None:
        self.piece_grid[row][col] = piece

    def get_piece(self, row: int, col: int):
        return self.piece_grid[row][col]

    def remove_piece(self, row: int, col: int) -> None:
        self.piece_grid[row][col] = None

    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> None:
        piece = self.piece_grid[from_row][from_col]
        self.piece_grid[from_row][from_col] = None
        self.piece_grid[to_row][to_col] = piece

    def set_tile(self, row: int, col: int, tile_type: str) -> None:
        self.tile_grid[row][col] = tile_type

    def get_tile(self, row: int, col: int) -> str:
        return self.tile_grid[row][col]

    def reset(self) -> None:
        self.piece_grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.tile_grid = [
            [NEUTRAL_TILE for _ in range(self.size)] for _ in range(self.size)
        ]

    def display(self) -> None:
        print("    " + "  ".join(str(col) for col in range(self.size)))
        print("   " + "---" * self.size)

        for row_index in range(self.size):
            row_display = []

            for col_index in range(self.size):
                piece = self.piece_grid[row_index][col_index]
                tile = self.tile_grid[row_index][col_index]

                if piece is not None:
                    row_display.append(str(piece))
                else:
                    tile_symbol = {
                        "neutral": ".",
                        "earth": "G",
                        "water": "W",
                        "fire": "R",
                        "air": "A",
                    }.get(tile, ".")

                    row_display.append(tile_symbol)

            print(f"{row_index} | " + " ".join(f"{cell:>3}" for cell in row_display))