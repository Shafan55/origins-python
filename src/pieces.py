class Piece:
    def __init__(self, piece_type: str, owner: str, symbol: str):
        self.piece_type = piece_type
        self.owner = owner
        self.symbol = symbol

    def __repr__(self) -> str:
        return self.symbol