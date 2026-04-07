from src.game import Game
from src.constants import PLAYER_1, PLAYER_2


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

    def get_state(self):
        state = []

        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                piece = self.game.board.get_piece(row, col)

                if piece is None:
                    state.append(0)
                elif piece.owner == PLAYER_1:
                    state.append(1)
                elif piece.owner == PLAYER_2:
                    state.append(2)

        return tuple(state)

    def get_valid_actions(self):
        if self.game.game_over:
            return []

        legal_moves = self.game.get_legal_moves()
        return [move.to_tuple() for move in legal_moves]

    def step(self, action):
        self.current_step += 1

        from_row, from_col, to_row, to_col = action
        success, reward = self.game.make_move(from_row, from_col, to_row, to_col)

        next_state = self.get_state()

        # --- FIX 1: penalise invalid moves ---
        if not success:
            reward = -0.1

        # --- FIX 2: force game termination on max steps ---
        done = self.game.game_over

        if not done and self.current_step >= self.max_steps:
            done = True
            reward = -1.0  # treat as loss

        return next_state, reward, done, {
            "success": success,
            "current_player": self.game.current_player,
            "winner": self.game.winner,
        }

    def render(self):
        self.game.display()