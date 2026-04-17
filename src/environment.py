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
    EARTH,
    WATER,
    FIRE,
    AIR,
)


REWARD_WIN                  =  150.0
REWARD_LOSE                 =  -50.0
REWARD_DRAW_TIMEOUT         =  -40.0
REWARD_DRAW_NO_MOVES        =  -10.0
REWARD_HUMAN_GOAL           =   15.0
REWARD_CAPTURE_OPPONENT     =    5.0
REWARD_LOSE_OWN_HUMAN       =  -20.0
REWARD_PROGRESS_WEIGHT      =    0.25
REWARD_STEP_PENALTY         =   -0.10
REWARD_PASSIVE_PENALTY      =   -0.30
REWARD_REPETITION_PENALTY   =   -1.5
REWARD_LATE_GAME_PENALTY    =   -0.40
LATE_GAME_THRESHOLD         =    0.50


class OriginsEnv:
    def __init__(self, board_size: int = 8, include_tile_state: bool = False):
        self.board_size = board_size
        self.include_tile_state = include_tile_state
        self.game = Game(board_size=board_size)
        self.max_steps = (
            PROTOTYPE_MAX_STEPS if board_size == 4 else FULL_GAME_MAX_STEPS
        )
        self.current_step = 0
        self.state_visit_counts = {}

    def reset(self):
        self.game.reset()
        self.current_step = 0
        self.state_visit_counts = {}
        initial_state = self.get_state()
        self.state_visit_counts[initial_state] = 1
        return initial_state

    def encode_piece(self, piece):
        if piece is None:
            return 0

        if piece.owner == PLAYER_1:
            if piece.piece_type == MALE_PIECE:
                return 1
            if piece.piece_type == FEMALE_PIECE:
                return 2
            if piece.piece_type == ELEMENT_PIECE:
                if piece.element == EARTH:  return 3
                if piece.element == WATER:  return 4
                if piece.element == FIRE:   return 5
                if piece.element == AIR:    return 6
                return 3

        if piece.owner == PLAYER_2:
            if piece.piece_type == MALE_PIECE:
                return 7
            if piece.piece_type == FEMALE_PIECE:
                return 8
            if piece.piece_type == ELEMENT_PIECE:
                if piece.element == EARTH:  return 9
                if piece.element == WATER:  return 10
                if piece.element == FIRE:   return 11
                if piece.element == AIR:    return 12
                return 9

        return 0

    def encode_tile(self, tile_type: str):
        if tile_type == NEUTRAL_TILE:  return 0
        if tile_type == EARTH_TILE:    return 1
        if tile_type == WATER_TILE:    return 2
        if tile_type == FIRE_TILE:     return 3
        if tile_type == AIR_TILE:      return 4
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

    def count_player_humans(self, player):
        """Count how many human pieces (male + female) a player still has."""
        count = 0
        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                piece = self.game.board.get_piece(row, col)
                if piece is not None and piece.owner == player:
                    if piece.piece_type in (MALE_PIECE, FEMALE_PIECE):
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
        Measures how far human pieces have advanced toward the goal.
        Element pieces contribute a small amount too.
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

        
        player_progress_before   = self.get_player_progress_score(moving_player)
        opponent_pieces_before   = self.count_player_pieces(opponent)
        humans_on_goal_before    = self.count_player_humans_on_goal_row(moving_player)
        own_humans_before        = self.count_player_humans(moving_player)

        success, base_reward = self.game.make_move(from_row, from_col, to_row, to_col)

        reward = float(base_reward)

        if not success:
            return self.get_state(), float(ILLEGAL_MOVE_PENALTY), False, {
                "success": False,
                "current_player": self.game.current_player,
                "winner": self.game.winner,
                "steps": self.current_step,
                "progress_delta": 0,
                "captured_count": 0,
                "goal_progress_delta": 0,
                "repeat_count": 1,
                "done": False,
            }

        done = self.game.is_terminal()

        
        player_progress_after  = self.get_player_progress_score(moving_player)
        opponent_pieces_after  = self.count_player_pieces(opponent)
        humans_on_goal_after   = self.count_player_humans_on_goal_row(moving_player)
        own_humans_after       = self.count_player_humans(moving_player)

        progress_delta      = player_progress_after - player_progress_before
        captured_count      = opponent_pieces_before - opponent_pieces_after
        goal_progress_delta = humans_on_goal_after - humans_on_goal_before
        lost_human          = own_humans_before - own_humans_after

        


        reward += REWARD_PROGRESS_WEIGHT * progress_delta

        
        if captured_count > 0:
            reward += REWARD_CAPTURE_OPPONENT * captured_count

        
        if goal_progress_delta > 0:
            reward += REWARD_HUMAN_GOAL * goal_progress_delta

        
        if lost_human > 0:
            reward += REWARD_LOSE_OWN_HUMAN * lost_human

        
        if not done:
            reward += REWARD_STEP_PENALTY

        
        if not done and self.current_step > int(self.max_steps * LATE_GAME_THRESHOLD):
            reward += REWARD_LATE_GAME_PENALTY

        
        if done:
            if self.game.winner == moving_player:
                reward += REWARD_WIN
            elif self.game.winner == opponent:
                reward += REWARD_LOSE
            else:
                
                if self.current_step >= self.max_steps:
                    reward += REWARD_DRAW_TIMEOUT
                else:
                    reward += REWARD_DRAW_NO_MOVES

        
        if not done and self.current_step >= self.max_steps:
            done = True
            reward += REWARD_DRAW_TIMEOUT

        next_state = self.get_state()

        
        self.state_visit_counts[next_state] = (
            self.state_visit_counts.get(next_state, 0) + 1
        )
        repeat_count = self.state_visit_counts[next_state]
        if repeat_count >= 2:
            reward += REWARD_REPETITION_PENALTY * (repeat_count - 1)

        
        if (
            self.board_size == 8
            and progress_delta <= 0
            and captured_count == 0
            and goal_progress_delta == 0
            and not done
        ):
            reward += REWARD_PASSIVE_PENALTY

        info = {
            "success": success,
            "current_player": self.game.current_player,
            "winner": self.game.winner,
            "steps": self.current_step,
            "progress_delta": progress_delta,
            "captured_count": captured_count,
            "goal_progress_delta": goal_progress_delta,
            "repeat_count": repeat_count,
            "done": done,
        }

        return next_state, reward, done, info

    def render(self):
        self.game.display()