from src.move import Move


def is_within_bounds(row: int, col: int, size: int) -> bool:
    return 0 <= row < size and 0 <= col < size


def is_legal_move(board, from_row: int, from_col: int, to_row: int, to_col: int, current_player: str) -> bool:
    if not is_within_bounds(from_row, from_col, board.size):
        return False

    if not is_within_bounds(to_row, to_col, board.size):
        return False

    piece = board.get_piece(from_row, from_col)

    if piece is None:
        return False

    if piece.owner != current_player:
        return False

    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)

    if row_diff == 0 and col_diff == 0:
        return False

    if row_diff <= 1 and col_diff <= 1:
        target_piece = board.get_piece(to_row, to_col)
        if target_piece is None:
            return True

    return False


def get_legal_moves_for_player(board, current_player: str) -> list[Move]:
    legal_moves = []

    for from_row in range(board.size):
        for from_col in range(board.size):
            piece = board.get_piece(from_row, from_col)

            if piece is None:
                continue

            if piece.owner != current_player:
                continue

            for to_row in range(board.size):
                for to_col in range(board.size):
                    if is_legal_move(board, from_row, from_col, to_row, to_col, current_player):
                        legal_moves.append(Move(from_row, from_col, to_row, to_col))

    return legal_moves