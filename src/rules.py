from src.move import Move
from src.constants import (
    PLAYER_1,
    PLAYER_2,
    MALE_PIECE,
    FEMALE_PIECE,
    ELEMENT_PIECE,
)


def is_within_bounds(row: int, col: int, size: int) -> bool:
    return 0 <= row < size and 0 <= col < size


def is_same_position(from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    return from_row == to_row and from_col == to_col


def get_player_forward_direction(current_player: str) -> int:
    """
    Player 1 starts at the top and moves downward (+1 row).
    Player 2 starts at the bottom and moves upward (-1 row).
    """
    return 1 if current_player == PLAYER_1 else -1


def is_human_piece(piece) -> bool:
    return piece.piece_type in {MALE_PIECE, FEMALE_PIECE}


def is_element_piece(piece) -> bool:
    return piece.piece_type == ELEMENT_PIECE


def is_legal_human_move(
    board,
    piece,
    from_row: int,
    from_col: int,
    to_row: int,
    to_col: int,
    current_player: str,
) -> bool:
    """
    Decisive prototype rule for Male/Female pieces:
    - can move 1 step forward
    - can move 1 step diagonally forward
    - cannot move sideways
    - cannot move backward
    - can move into empty square
    - can capture opponent by landing on occupied square
    """
    row_diff = to_row - from_row
    col_diff = to_col - from_col
    forward = get_player_forward_direction(current_player)

    allowed_moves = {
        (forward, 0),    # forward
        (forward, 1),    # forward-right
        (forward, -1),   # forward-left
    }

    if (row_diff, col_diff) not in allowed_moves:
        return False

    target_piece = board.get_piece(to_row, to_col)

    if target_piece is None:
        return True

    if target_piece.owner == current_player:
        return False

    return True


def is_legal_element_move(
    board,
    piece,
    from_row: int,
    from_col: int,
    to_row: int,
    to_col: int,
    current_player: str,
) -> bool:
    """
    Prototype rule for Element piece:
    - can move 1 square in any direction
    - can move into empty square
    - can capture opponent
    - cannot land on own piece
    """
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)

    if row_diff > 1 or col_diff > 1 or (row_diff == 0 and col_diff == 0):
        return False

    target_piece = board.get_piece(to_row, to_col)

    if target_piece is None:
        return True

    if target_piece.owner == current_player:
        return False

    return True


def is_legal_move(
    board,
    from_row: int,
    from_col: int,
    to_row: int,
    to_col: int,
    current_player: str,
) -> bool:
    if not is_within_bounds(from_row, from_col, board.size):
        return False

    if not is_within_bounds(to_row, to_col, board.size):
        return False

    if is_same_position(from_row, from_col, to_row, to_col):
        return False

    piece = board.get_piece(from_row, from_col)

    if piece is None:
        return False

    if piece.owner != current_player:
        return False

    if is_human_piece(piece):
        return is_legal_human_move(
            board,
            piece,
            from_row,
            from_col,
            to_row,
            to_col,
            current_player,
        )

    if is_element_piece(piece):
        return is_legal_element_move(
            board,
            piece,
            from_row,
            from_col,
            to_row,
            to_col,
            current_player,
        )

    return False


def get_candidate_destinations(from_row: int, from_col: int) -> list[tuple[int, int]]:
    """
    Only check nearby squares instead of scanning the whole board.
    """
    candidates = []

    for row_offset in (-1, 0, 1):
        for col_offset in (-1, 0, 1):
            if row_offset == 0 and col_offset == 0:
                continue
            candidates.append((from_row + row_offset, from_col + col_offset))

    return candidates


def get_legal_moves_for_player(board, current_player: str) -> list[Move]:
    legal_moves = []

    for from_row in range(board.size):
        for from_col in range(board.size):
            piece = board.get_piece(from_row, from_col)

            if piece is None:
                continue

            if piece.owner != current_player:
                continue

            candidate_destinations = get_candidate_destinations(from_row, from_col)

            for to_row, to_col in candidate_destinations:
                if not is_within_bounds(to_row, to_col, board.size):
                    continue

                if is_legal_move(
                    board,
                    from_row,
                    from_col,
                    to_row,
                    to_col,
                    current_player,
                ):
                    legal_moves.append(Move(from_row, from_col, to_row, to_col))

    return legal_moves