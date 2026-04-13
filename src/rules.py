from src.move import Move
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
    NEUTRAL_TILE,
    EARTH_TILE,
    WATER_TILE,
    FIRE_TILE,
    AIR_TILE,
)


ELEMENT_TO_TILE = {
    EARTH: EARTH_TILE,
    WATER: WATER_TILE,
    FIRE: FIRE_TILE,
    AIR: AIR_TILE,
}

DOMINATES = {
    EARTH: WATER,
    WATER: FIRE,
    FIRE: AIR,
    AIR: EARTH,
}

EQUAL_ELEMENTS = {
    EARTH: {FIRE},
    FIRE: {EARTH},
    WATER: {AIR},
    AIR: {WATER},
}


def is_within_bounds(row: int, col: int, size: int) -> bool:
    return 0 <= row < size and 0 <= col < size


def is_same_position(from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    return from_row == to_row and from_col == to_col


def get_player_forward_direction(current_player: str) -> int:
    return 1 if current_player == PLAYER_1 else -1


def get_starting_row(player: str, board_size: int) -> int:
    return 0 if player == PLAYER_1 else board_size - 1


def get_destination_row(player: str, board_size: int) -> int:
    return board_size - 1 if player == PLAYER_1 else 0


def is_human_piece(piece) -> bool:
    return piece is not None and piece.piece_type in {MALE_PIECE, FEMALE_PIECE}


def is_element_piece(piece) -> bool:
    return piece is not None and piece.piece_type == ELEMENT_PIECE


def get_tile_element(tile_type: str):
    if tile_type == EARTH_TILE:
        return EARTH
    if tile_type == WATER_TILE:
        return WATER
    if tile_type == FIRE_TILE:
        return FIRE
    if tile_type == AIR_TILE:
        return AIR
    return None


def element_dominates(element_a: str, element_b: str) -> bool:
    return DOMINATES.get(element_a) == element_b


def elements_are_equal(element_a: str, element_b: str) -> bool:
    return element_b in EQUAL_ELEMENTS.get(element_a, set())


def get_path_squares(from_row: int, from_col: int, to_row: int, to_col: int):
    row_diff = to_row - from_row
    col_diff = to_col - from_col

    step_row = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
    step_col = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)

    if row_diff != 0 and col_diff != 0 and abs(row_diff) != abs(col_diff):
        return None

    path = []
    current_row = from_row + step_row
    current_col = from_col + step_col

    while (current_row, current_col) != (to_row, to_col):
        path.append((current_row, current_col))
        current_row += step_row
        current_col += step_col

    return path


def is_straight_line_move(from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    return (
        from_row == to_row
        or from_col == to_col
        or row_diff == col_diff
    )


def is_on_starting_row(row: int, player: str, board_size: int) -> bool:
    return row == get_starting_row(player, board_size)


def is_on_destination_row(row: int, player: str, board_size: int) -> bool:
    return row == get_destination_row(player, board_size)


def is_human_locked_on_destination(row: int, player: str, board_size: int) -> bool:
    return is_on_destination_row(row, player, board_size)


def human_move_respects_direction(from_row: int, to_row: int, current_player: str) -> bool:
    """
    Human pieces may move:
    - forward vertically
    - forward diagonally
    - horizontally
    But not backward.
    """
    row_change = to_row - from_row

    if row_change == 0:
        return True

    forward = get_player_forward_direction(current_player)
    return row_change * forward > 0


def path_is_clear_for_human(board, path) -> bool:
    for row, col in path:
        if board.get_piece(row, col) is not None:
            return False
    return True


def human_target_tile_is_valid(board, to_row: int, to_col: int) -> bool:
    return board.get_tile(to_row, to_col) != NEUTRAL_TILE


def is_legal_human_move(
    board,
    piece,
    from_row: int,
    from_col: int,
    to_row: int,
    to_col: int,
    current_player: str,
) -> bool:
    # locked on destination — cannot move
    if is_on_destination_row(from_row, current_player, board.size):
        return False

    # cannot move horizontally within starting row
    if is_on_starting_row(from_row, current_player, board.size):
        if to_row == from_row:
            return False

    # cannot move back to starting row
    if is_on_starting_row(to_row, current_player, board.size):
        return False

    if not is_straight_line_move(from_row, from_col, to_row, to_col):
        return False

    if not human_move_respects_direction(from_row, to_row, current_player):
        return False

    if not human_target_tile_is_valid(board, to_row, to_col):
        return False

    path = get_path_squares(from_row, from_col, to_row, to_col)
    if path is None:
        return False

    if not path_is_clear_for_human(board, path):
        return False

    # cannot jump over a human locked on destination row
    for r, c in path:
        blocking = board.get_piece(r, c)
        if blocking is not None and is_human_piece(blocking):
            if is_on_destination_row(r, blocking.owner, board.size):
                return False

    target_piece = board.get_piece(to_row, to_col)
    if target_piece is not None:
        return False

    return True


def element_can_enter_tile(moving_element: str, target_tile: str) -> bool:
    if target_tile == NEUTRAL_TILE:
        return True

    target_element = get_tile_element(target_tile)
    if target_element is None:
        return False

    if target_element == moving_element:
        return True

    if elements_are_equal(moving_element, target_element):
        return False

    if element_dominates(moving_element, target_element):
        return True

    return False


def path_is_clear_for_element(board, piece, path, current_player: str) -> bool:
    """
    An element piece can pass through a square if:
    - the tile is passable (neutral, same element, or weaker element)
    - any occupying piece is either:
        - a weaker opponent element (can capture by passing)
        - nothing blocking otherwise

    Blocked by:
    - own pieces of any type
    - equal element opponent pieces
    - stronger element opponent pieces
    - any human piece (cannot pass through humans)
    - locked humans on destination row
    """
    moving_element = piece.element

    for row, col in path:
        tile_type = board.get_tile(row, col)

        if not element_can_enter_tile(moving_element, tile_type):
            return False

        occupying_piece = board.get_piece(row, col)

        if occupying_piece is None:
            continue

        # own pieces always block
        if occupying_piece.owner == current_player:
            return False

        # human pieces always block (cannot pass through humans)
        if is_human_piece(occupying_piece):
            return False

        # opponent element pieces
        if is_element_piece(occupying_piece):
            other_element = occupying_piece.element

            # same element blocks
            if other_element == moving_element:
                return False

            # equal element blocks
            if elements_are_equal(moving_element, other_element):
                return False

            # weaker element — can pass through (capture on the way)
            if element_dominates(moving_element, other_element):
                continue

            # stronger element blocks
            return False

    return True


def element_target_is_valid(board, piece, to_row: int, to_col: int, current_player: str) -> bool:
    moving_element = piece.element
    target_tile = board.get_tile(to_row, to_col)

    if not element_can_enter_tile(moving_element, target_tile):
        return False

    target_piece = board.get_piece(to_row, to_col)

    if target_piece is None:
        return True

    # own pieces block landing
    if target_piece.owner == current_player:
        return False

    # cannot land on human pieces
    if is_human_piece(target_piece):
        return False

    if is_element_piece(target_piece):
        other_element = target_piece.element

        if other_element == moving_element:
            return False

        if elements_are_equal(moving_element, other_element):
            return False

        return element_dominates(moving_element, other_element)

    return False


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
    Element rules:
    - cannot move within starting row
    - cannot return to either starting row
    - move any distance in straight line
    - interacts with tiles/pieces by dominance rules
    """
    # cannot move within starting row
    if is_on_starting_row(from_row, current_player, board.size):
        if to_row == from_row:
            return False

    # cannot return to own starting row
    if is_on_starting_row(to_row, current_player, board.size):
        return False

    # cannot enter opponent starting row either
    opponent = PLAYER_2 if current_player == PLAYER_1 else PLAYER_1
    if is_on_starting_row(to_row, opponent, board.size):
        return False

    if not is_straight_line_move(from_row, from_col, to_row, to_col):
        return False

    path = get_path_squares(from_row, from_col, to_row, to_col)
    if path is None:
        return False

    # path cannot pass through either starting row squares with locked humans
    for r, c in path:
        blocking = board.get_piece(r, c)
        if blocking is not None and is_human_piece(blocking):
            if is_on_destination_row(r, blocking.owner, board.size):
                return False

    if not path_is_clear_for_element(board, piece, path, current_player):
        return False

    if not element_target_is_valid(board, piece, to_row, to_col, current_player):
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
            board, piece, from_row, from_col, to_row, to_col, current_player,
        )

    if is_element_piece(piece):
        return is_legal_element_move(
            board, piece, from_row, from_col, to_row, to_col, current_player,
        )

    return False


def get_candidate_destinations(board, piece, from_row: int, from_col: int):
    candidates = []

    if is_human_piece(piece):
        for to_row in range(board.size):
            for to_col in range(board.size):
                if (to_row, to_col) != (from_row, from_col):
                    candidates.append((to_row, to_col))
        return candidates

    if is_element_piece(piece):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
        ]

        for d_row, d_col in directions:
            step = 1
            while True:
                new_row = from_row + d_row * step
                new_col = from_col + d_col * step

                if not is_within_bounds(new_row, new_col, board.size):
                    break

                candidates.append((new_row, new_col))
                step += 1

        return candidates

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

            candidate_destinations = get_candidate_destinations(
                board, piece, from_row, from_col,
            )

            for to_row, to_col in candidate_destinations:
                if not is_within_bounds(to_row, to_col, board.size):
                    continue

                if is_legal_move(
                    board, from_row, from_col, to_row, to_col, current_player,
                ):
                    legal_moves.append(Move(from_row, from_col, to_row, to_col))

    return legal_moves