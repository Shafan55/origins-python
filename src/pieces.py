class Piece:
    def __init__(
        self,
        piece_type: str,
        owner: str,
        symbol: str,
        element: str | None = None,
    ):
        self.piece_type = piece_type
        self.owner = owner
        self.symbol = symbol
        self.element = element

    def is_human_piece(self) -> bool:
        return self.piece_type in ["male", "female", "human"]

    def is_element_piece(self) -> bool:
        return self.piece_type == "element"

    def is_male(self) -> bool:
        return self.piece_type == "male"

    def is_female(self) -> bool:
        return self.piece_type == "female"

    def is_owned_by(self, player: str) -> bool:
        return self.owner == player

    def __repr__(self) -> str:
        return self.symbol