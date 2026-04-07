from src.game import Game
from src.constants import (
    PLAYER_1,
    PLAYER_2,
    MALE_PIECE,
    FEMALE_PIECE,
    ELEMENT_PIECE,
    ILLEGAL_MOVE_PENALTY,
)


class OriginsEnv:
    def __init__(self, board_size: int = 4):
        self.board_size = board_size
        self.game = Game(board_size=board_size)
        self.max_steps = 40
        self.current_step = 0

    def reset(self):
        self.game.reset()
        self.current_step = 0
        return self.get_state()

    def encode_piece(self, piece):
        """
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

    def get_state(self):
        state = []

        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                piece = self.game.board.get_piece(row, col)
                state.append(self.encode_piece(piece))

        # include turn
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

    def get_player_progress_score(self, player):
        """
        Progress toward destination row.
        Male/Female weighted higher than element pieces.
        """
        score = 0
        last_row = self.game.board.size - 1

        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                piece = self.game.board.get_piece(row, col)

                if piece is None or piece.owner != player:
                    continue

                weight = 2 if piece.piece_type in (MALE_PIECE, FEMALE_PIECE) else 1

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

        success, base_reward = self.game.make_move(
            from_row, from_col, to_row, to_col
        )

        reward = float(base_reward)

        if not success:
            reward = float(ILLEGAL_MOVE_PENALTY)

        done = self.game.is_terminal()

        player_progress_after = self.get_player_progress_score(moving_player)
        opponent_pieces_after = self.count_player_pieces(opponent)

        progress_delta = player_progress_after - player_progress_before
        reward += 0.05 * progress_delta

        captured_count = opponent_pieces_before - opponent_pieces_after
        if captured_count > 0:
            reward += 2.0 * captured_count

        if success and not done:
            reward -= 0.1

        # explicit draw penalty so agent does not seek quick draws
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
            "done": done,
        }

        return next_state, reward, done, info

    def render(self):
        self.game.display()