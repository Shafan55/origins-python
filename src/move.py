class Move:
    def __init__(self, from_row: int, from_col: int, to_row: int, to_col: int):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col

    def __repr__(self) -> str:
        return f"Move(({self.from_row}, {self.from_col}) -> ({self.to_row}, {self.to_col}))"

    def to_tuple(self):
        return (self.from_row, self.from_col, self.to_row, self.to_col)