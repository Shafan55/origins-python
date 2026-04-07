from src.game import Game
from src.constants import (
    PLAYER_1,
    PLAYER_2,
    MALE_PIECE,
    FEMALE_PIECE,
    ELEMENT_PIECE,
    ILLEGAL_MOVE_PENALTY,
    NEUTRAL_TILE,
    EARTH_TILE,
    WATER_TILE,
    FIRE_TILE,
    AIR_TILE,
    PROTOTYPE_MAX_STEPS,
    FULL_GAME_MAX_STEPS,
)


class OriginsEnv:
    def __init__(self, board_size: int = 4, include_tile_state: bool = False):
        self.board_size = board_size
        self.include_tile_state = include_tile_state
        self.game = Game(board_size=board_size)
        self.max_steps = (
            PROTOTYPE_MAX_STEPS if board_size == 4 else FULL_GAME_MAX_STEPS
        )
        self.current_step = 0

    def reset(self):
        self.game.reset()
        self.current_step = 0
        return self.get_state()

    def encode_piece(self, piece):
        """
        Piece encoding:
        0 = empty

        Player 1:
        1 = male
        2 = female
        3 = element

        Player 2:
        4 = male
        5 = female
        6 = element
        """
        if piece is None:
            return 0

        if piece.owner == PLAYER_1:
            if piece.piece_type == MALE_PIECE:
                return 1
            if piece.piece_type == FEMALE_PIECE:
                return 2
            if piece.piece_type == ELEMENT_PIECE:
                return 3

        if piece.owner == PLAYER_2:
            if piece.piece_type == MALE_PIECE:
                return 4
            if piece.piece_type == FEMALE_PIECE:
                return 5
            if piece.piece_type == ELEMENT_PIECE:
                return 6

        return 0

    def encode_tile(self, tile_type: str):
        """
        Tile encoding:
        0 = neutral
        1 = earth
        2 = water
        3 = fire
        4 = air
        """
        if tile_type == NEUTRAL_TILE:
            return 0
        if tile_type == EARTH_TILE:
            return 1
        if tile_type == WATER_TILE:
            return 2
        if tile_type == FIRE_TILE:
            return 3
        if tile_type == AIR_TILE:
            return 4
        return 0

    def get_piece_state(self):
        state = []

        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                piece = self.game.board.get_piece(row, col)
                state.append(self.encode_piece(piece))

        return state

    def get_tile_state(self):
        tile_state = []

        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                tile_type = self.game.board.get_tile(row, col)
                tile_state.append(self.encode_tile(tile_type))

        return tile_state

    def get_state(self):
        """
        Default RL prototype state:
        - piece encoding
        - current turn

        Optional scalable state:
        - piece encoding
        - tile encoding
        - current turn
        """
        state = self.get_piece_state()

        if self.include_tile_state:
            state.extend(self.get_tile_state())

        state.append(1 if self.game.current_player == PLAYER_1 else 2)

        return tuple(state)

    def get_valid_actions(self):
        if self.game.is_terminal():
            return []

        legal_moves = self.game.get_legal_moves()

        return [
            (move.from_row, move.from_col, move.to_row, move.to_col)
            for move in legal_moves
        ]

    def count_player_pieces(self, player):
        count = 0
        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                piece = self.game.board.get_piece(row, col)
                if piece is not None and piece.owner == player:
                    count += 1
        return count

    def count_player_humans_on_goal_row(self, player):
        target_row = self.game.board.size - 1 if player == PLAYER_1 else 0
        count = 0

        for col in range(self.game.board.size):
            piece = self.game.board.get_piece(target_row, col)
            if piece is None:
                continue

            if piece.owner == player and piece.piece_type in (MALE_PIECE, FEMALE_PIECE):
                count += 1

        return count

    def get_player_progress_score(self, player):
        """
        Progress toward destination row.
        Human pieces weighted higher than element pieces.
        """
        score = 0
        last_row = self.game.board.size - 1

        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                piece = self.game.board.get_piece(row, col)

                if piece is None or piece.owner != player:
                    continue

                weight = 3 if piece.piece_type in (MALE_PIECE, FEMALE_PIECE) else 1

                if player == PLAYER_1:
                    progress = row
                else:
                    progress = last_row - row

                score += weight * progress

        return score

    def step(self, action):
        self.current_step += 1

        from_row, from_col, to_row, to_col = action

        moving_player = self.game.current_player
        opponent = PLAYER_2 if moving_player == PLAYER_1 else PLAYER_1

        player_progress_before = self.get_player_progress_score(moving_player)
        opponent_pieces_before = self.count_player_pieces(opponent)
        humans_on_goal_before = self.count_player_humans_on_goal_row(moving_player)

        success, base_reward = self.game.make_move(
            from_row, from_col, to_row, to_col
        )

        reward = float(base_reward)

        if not success:
            reward = float(ILLEGAL_MOVE_PENALTY)

        done = self.game.is_terminal()

        player_progress_after = self.get_player_progress_score(moving_player)
        opponent_pieces_after = self.count_player_pieces(opponent)
        humans_on_goal_after = self.count_player_humans_on_goal_row(moving_player)

        progress_delta = player_progress_after - player_progress_before
        reward += 0.05 * progress_delta

        captured_count = opponent_pieces_before - opponent_pieces_after
        if captured_count > 0:
            reward += 2.0 * captured_count

        goal_progress_delta = humans_on_goal_after - humans_on_goal_before
        if goal_progress_delta > 0:
            reward += 3.0 * goal_progress_delta

        if success and not done:
            reward -= 0.1

        if done and self.game.winner is None:
            reward -= 2.0

        if not done and self.current_step >= self.max_steps:
            done = True
            reward -= 2.0

        next_state = self.get_state()

        info = {
            "success": success,
            "current_player": self.game.current_player,
            "winner": self.game.winner,
            "steps": self.current_step,
            "progress_delta": progress_delta,
            "captured_count": captured_count,
            "goal_progress_delta": goal_progress_delta,
            "done": done,
        }

        return next_state, reward, done, info

    def render(self):
        self.game.display()