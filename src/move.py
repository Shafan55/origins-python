class Move:
    def __init__(self, from_row: int, from_col: int, to_row: int, to_col: int):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col

    def __repr__(self) -> str:
        return f"Move(({self.from_row}, {self.from_col}) -> ({self.to_row}, {self.to_col}))"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Move):
            return False
        return (
            self.from_row == other.from_row
            and self.from_col == other.from_col
            and self.to_row == other.to_row
            and self.to_col == other.to_col
        )

    def to_tuple(self):
        return (self.from_row, self.from_col, self.to_row, self.to_col)

    @staticmethod
    def from_tuple(action_tuple):
        from_row, from_col, to_row, to_col = action_tuple
        return Move(from_row, from_col, to_row, to_col)