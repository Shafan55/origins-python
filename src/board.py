from src.pieces import Piece


class Board:
    def __init__(self, size: int = 8):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]

    def place_piece(self, row: int, col: int, piece: Piece) -> None:
        self.grid[row][col] = piece

    def get_piece(self, row: int, col: int):
        return self.grid[row][col]

    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> None:
        piece = self.grid[from_row][from_col]
        self.grid[from_row][from_col] = None
        self.grid[to_row][to_col] = piece

    def display(self) -> None:
        print("    " + "  ".join(str(col) for col in range(self.size)))
        print("   " + "---" * self.size)

        for row_index, row in enumerate(self.grid):
            row_display = []
            for cell in row:
                if cell is None:
                    row_display.append(".")
                else:
                    row_display.append(str(cell))
            print(f"{row_index} | " + " ".join(f"{cell:>3}" for cell in row_display))