import json
import random
from src.environment import OriginsEnv
from src.constants import PLAYER_1, PLAYER_2


class QLearningAgent:
    def __init__(
        self,
        alpha: float = 0.2,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.99,
        epsilon_min: float = 0.05,
    ):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table = {}

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, valid_actions):
        if not valid_actions:
            return None

        if random.random() < self.epsilon:
            return random.choice(valid_actions)

        q_values = [self.get_q_value(state, action) for action in valid_actions]
        max_q = max(q_values)

        best_actions = [
            action
            for action, q_value in zip(valid_actions, q_values)
            if q_value == max_q
        ]
        return random.choice(best_actions)

    def update_q_value(self, state, action, reward, next_state, next_valid_actions):
        current_q = self.get_q_value(state, action)

        if next_valid_actions:
            max_future_q = max(
                self.get_q_value(next_state, next_action)
                for next_action in next_valid_actions
            )
        else:
            max_future_q = 0.0

        new_q = current_q + self.alpha * (
            reward + self.gamma * max_future_q - current_q
        )

        self.q_table[(state, action)] = new_q

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_q_table(self, filepath: str):
        """
        Save Q-table and agent settings to a JSON file.
        """
        serializable_q_table = {}

        for (state, action), value in self.q_table.items():
            key = {
                "state": list(state),
                "action": list(action),
            }
            serializable_q_table[json.dumps(key)] = value

        payload = {
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "epsilon_decay": self.epsilon_decay,
            "epsilon_min": self.epsilon_min,
            "q_table": serializable_q_table,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    @classmethod
    def load_q_table(cls, filepath: str):
        """
        Load Q-table and agent settings from a JSON file.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)

        agent = cls(
            alpha=payload["alpha"],
            gamma=payload["gamma"],
            epsilon=payload["epsilon"],
            epsilon_decay=payload["epsilon_decay"],
            epsilon_min=payload["epsilon_min"],
        )

        restored_q_table = {}

        for key_str, value in payload["q_table"].items():
            key_data = json.loads(key_str)
            state = tuple(key_data["state"])
            action = tuple(key_data["action"])
            restored_q_table[(state, action)] = value

        agent.q_table = restored_q_table
        return agent


class RandomAgent:
    def choose_action(self, state, valid_actions):
        if not valid_actions:
            return None
        return random.choice(valid_actions)


def train_q_learning(episodes: int = 300, board_size: int = 4):
    """
    Self-play training:
    the same Q-learning agent controls both players.
    """
    env = OriginsEnv(board_size=board_size)
    agent = QLearningAgent()

    episode_rewards = []
    episode_steps = []
    episode_p1_wins = []
    episode_p2_wins = []
    episode_draws = []

    print("Starting Q-learning training...")

    for episode in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0.0
        step_count = 0
        info = {"winner": None}

        while not done:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break

            action = agent.choose_action(state, valid_actions)
            if action is None:
                break

            next_state, reward, done, info = env.step(action)

            next_valid_actions = env.get_valid_actions()

            agent.update_q_value(
                state,
                action,
                reward,
                next_state,
                next_valid_actions,
            )

            state = next_state
            total_reward += reward
            step_count += 1

        winner = info["winner"]

        p1_win = 1 if winner == PLAYER_1 else 0
        p2_win = 1 if winner == PLAYER_2 else 0
        draw = 1 if done and winner is None else 0

        agent.decay_epsilon()

        episode_rewards.append(total_reward)
        episode_steps.append(step_count)
        episode_p1_wins.append(p1_win)
        episode_p2_wins.append(p2_win)
        episode_draws.append(draw)

        if (episode + 1) % 50 == 0:
            recent_rewards = episode_rewards[-50:]
            recent_steps = episode_steps[-50:]
            recent_p1 = sum(episode_p1_wins[-50:])
            recent_p2 = sum(episode_p2_wins[-50:])
            recent_draws = sum(episode_draws[-50:])

            average_reward = sum(recent_rewards) / len(recent_rewards)
            average_steps = sum(recent_steps) / len(recent_steps)

            print(
                f"Episode {episode + 1}/{episodes} | "
                f"Avg Reward (last 50): {average_reward:.2f} | "
                f"Avg Steps (last 50): {average_steps:.2f} | "
                f"P1 wins: {recent_p1}/50 | "
                f"P2 wins: {recent_p2}/50 | "
                f"Draws: {recent_draws}/50 | "
                f"Epsilon: {agent.epsilon:.3f} | "
                f"Q-table size: {len(agent.q_table)}"
            )

    overall_average_reward = sum(episode_rewards) / len(episode_rewards)
    overall_average_steps = sum(episode_steps) / len(episode_steps)
    total_p1_wins = sum(episode_p1_wins)
    total_p2_wins = sum(episode_p2_wins)
    total_draws = sum(episode_draws)

    print("\nTRAINING SUMMARY")
    print("=" * 50)
    print(f"Total episodes: {episodes}")
    print(f"Overall average reward: {overall_average_reward:.2f}")
    print(f"Overall average steps: {overall_average_steps:.2f}")
    print(f"Player 1 wins: {total_p1_wins}/{episodes}")
    print(f"Player 2 wins: {total_p2_wins}/{episodes}")
    print(f"Draws: {total_draws}/{episodes}")
    print(f"Final epsilon: {agent.epsilon:.3f}")
    print(f"Final Q-table size: {len(agent.q_table)}")

    return agent, episode_rewards, episode_steps, episode_p1_wins, episode_p2_wins, episode_draws


def play_episode(agent_p1, agent_p2, board_size: int = 4, render: bool = False):
    """
    Run one episode with separate agents for Player 1 and Player 2.
    """
    env = OriginsEnv(board_size=board_size)
    state = env.reset()
    done = False
    step_count = 0
    info = {"winner": None}

    while not done:
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            break

        current_player = env.game.current_player

        if current_player == PLAYER_1:
            action = agent_p1.choose_action(state, valid_actions)
        else:
            action = agent_p2.choose_action(state, valid_actions)

        if action is None:
            break

        next_state, _, done, info = env.step(action)
        state = next_state
        step_count += 1

        if render:
            env.render()

    winner = info["winner"]
    return {
        "winner": winner,
        "done": done,
        "steps": step_count,
    }


def evaluate_self_play(agent, episodes: int = 100, board_size: int = 4, render: bool = False):
    """
    Trained agent vs itself.
    Useful to inspect self-play behaviour, not strength vs an opponent.
    """
    print("\nSELF-PLAY EVALUATION")
    print("=" * 40)

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    metrics = {
        "p1_wins": 0,
        "p2_wins": 0,
        "draws": 0,
        "unfinished": 0,
        "total_steps": 0,
    }

    for _ in range(episodes):
        result = play_episode(agent, agent, board_size=board_size, render=render)

        if not result["done"]:
            metrics["unfinished"] += 1
        elif result["winner"] == PLAYER_1:
            metrics["p1_wins"] += 1
        elif result["winner"] == PLAYER_2:
            metrics["p2_wins"] += 1
        else:
            metrics["draws"] += 1

        metrics["total_steps"] += result["steps"]

    avg_steps = metrics["total_steps"] / episodes

    print(f"Episodes: {episodes}")
    print(f"Player 1 wins: {metrics['p1_wins']}")
    print(f"Player 2 wins: {metrics['p2_wins']}")
    print(f"Draws: {metrics['draws']}")
    print(f"Unfinished: {metrics['unfinished']}")
    print(f"Average steps: {avg_steps:.2f}")

    agent.epsilon = old_epsilon
    return metrics


def evaluate_agent_as_player1_vs_random(agent, episodes: int = 100, board_size: int = 4, render: bool = False):
    """
    Trained agent controls Player 1.
    Random agent controls Player 2.
    """
    print("\nTRAINED AS PLAYER 1 VS RANDOM")
    print("=" * 40)

    random_agent = RandomAgent()

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    metrics = {
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "unfinished": 0,
        "total_steps": 0,
    }

    for _ in range(episodes):
        result = play_episode(agent, random_agent, board_size=board_size, render=render)

        if not result["done"]:
            metrics["unfinished"] += 1
        elif result["winner"] == PLAYER_1:
            metrics["wins"] += 1
        elif result["winner"] == PLAYER_2:
            metrics["losses"] += 1
        else:
            metrics["draws"] += 1

        metrics["total_steps"] += result["steps"]

    avg_steps = metrics["total_steps"] / episodes
    win_rate = (metrics["wins"] / episodes) * 100
    draw_rate = (metrics["draws"] / episodes) * 100
    loss_rate = (metrics["losses"] / episodes) * 100
    unfinished_rate = (metrics["unfinished"] / episodes) * 100

    print(f"Episodes: {episodes}")
    print(f"Wins: {metrics['wins']} ({win_rate:.2f}%)")
    print(f"Draws: {metrics['draws']} ({draw_rate:.2f}%)")
    print(f"Losses: {metrics['losses']} ({loss_rate:.2f}%)")
    print(f"Unfinished: {metrics['unfinished']} ({unfinished_rate:.2f}%)")
    print(f"Average steps: {avg_steps:.2f}")

    agent.epsilon = old_epsilon
    return metrics


def evaluate_agent_as_player2_vs_random(agent, episodes: int = 100, board_size: int = 4, render: bool = False):
    """
    Random agent controls Player 1.
    Trained agent controls Player 2.
    """
    print("\nTRAINED AS PLAYER 2 VS RANDOM")
    print("=" * 40)

    random_agent = RandomAgent()

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    metrics = {
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "unfinished": 0,
        "total_steps": 0,
    }

    for _ in range(episodes):
        result = play_episode(random_agent, agent, board_size=board_size, render=render)

        if not result["done"]:
            metrics["unfinished"] += 1
        elif result["winner"] == PLAYER_2:
            metrics["wins"] += 1
        elif result["winner"] == PLAYER_1:
            metrics["losses"] += 1
        else:
            metrics["draws"] += 1

        metrics["total_steps"] += result["steps"]

    avg_steps = metrics["total_steps"] / episodes
    win_rate = (metrics["wins"] / episodes) * 100
    draw_rate = (metrics["draws"] / episodes) * 100
    loss_rate = (metrics["losses"] / episodes) * 100
    unfinished_rate = (metrics["unfinished"] / episodes) * 100

    print(f"Episodes: {episodes}")
    print(f"Wins: {metrics['wins']} ({win_rate:.2f}%)")
    print(f"Draws: {metrics['draws']} ({draw_rate:.2f}%)")
    print(f"Losses: {metrics['losses']} ({loss_rate:.2f}%)")
    print(f"Unfinished: {metrics['unfinished']} ({unfinished_rate:.2f}%)")
    print(f"Average steps: {avg_steps:.2f}")

    agent.epsilon = old_epsilon
    return metrics


def evaluate_agent_fair(agent, episodes_each_side: int = 100, board_size: int = 4, render: bool = False):
    """
    Fair combined evaluation:
    trained agent tested from both Player 1 and Player 2 sides.
    """
    print("\nFAIR COMBINED EVALUATION")
    print("=" * 40)

    p1_metrics = evaluate_agent_as_player1_vs_random(
        agent,
        episodes=episodes_each_side,
        board_size=board_size,
        render=render,
    )

    p2_metrics = evaluate_agent_as_player2_vs_random(
        agent,
        episodes=episodes_each_side,
        board_size=board_size,
        render=render,
    )

    total_episodes = episodes_each_side * 2
    total_wins = p1_metrics["wins"] + p2_metrics["wins"]
    total_draws = p1_metrics["draws"] + p2_metrics["draws"]
    total_losses = p1_metrics["losses"] + p2_metrics["losses"]
    total_unfinished = p1_metrics["unfinished"] + p2_metrics["unfinished"]
    total_steps = p1_metrics["total_steps"] + p2_metrics["total_steps"]

    avg_steps = total_steps / total_episodes
    win_rate = (total_wins / total_episodes) * 100
    draw_rate = (total_draws / total_episodes) * 100
    loss_rate = (total_losses / total_episodes) * 100
    unfinished_rate = (total_unfinished / total_episodes) * 100

    print("\nFAIR SUMMARY")
    print("=" * 40)
    print(f"Total episodes: {total_episodes}")
    print(f"Wins: {total_wins} ({win_rate:.2f}%)")
    print(f"Draws: {total_draws} ({draw_rate:.2f}%)")
    print(f"Losses: {total_losses} ({loss_rate:.2f}%)")
    print(f"Unfinished: {total_unfinished} ({unfinished_rate:.2f}%)")
    print(f"Average steps: {avg_steps:.2f}")

    return {
        "wins": total_wins,
        "draws": total_draws,
        "losses": total_losses,
        "unfinished": total_unfinished,
        "episodes": total_episodes,
        "win_rate": win_rate,
        "draw_rate": draw_rate,
        "loss_rate": loss_rate,
        "unfinished_rate": unfinished_rate,
        "average_steps": avg_steps,
    }


def evaluate_random_vs_random(episodes: int = 100, board_size: int = 4):
    """
    Baseline reference:
    random Player 1 vs random Player 2
    """
    print("\nRANDOM VS RANDOM")
    print("=" * 40)

    random_agent_1 = RandomAgent()
    random_agent_2 = RandomAgent()

    metrics = {
        "p1_wins": 0,
        "p2_wins": 0,
        "draws": 0,
        "unfinished": 0,
        "total_steps": 0,
    }

    for _ in range(episodes):
        result = play_episode(random_agent_1, random_agent_2, board_size=board_size)

        if not result["done"]:
            metrics["unfinished"] += 1
        elif result["winner"] == PLAYER_1:
            metrics["p1_wins"] += 1
        elif result["winner"] == PLAYER_2:
            metrics["p2_wins"] += 1
        else:
            metrics["draws"] += 1

        metrics["total_steps"] += result["steps"]

    avg_steps = metrics["total_steps"] / episodes
    p1_win_rate = (metrics["p1_wins"] / episodes) * 100
    p2_win_rate = (metrics["p2_wins"] / episodes) * 100
    draw_rate = (metrics["draws"] / episodes) * 100
    unfinished_rate = (metrics["unfinished"] / episodes) * 100

    print(f"Episodes: {episodes}")
    print(f"Player 1 wins: {metrics['p1_wins']} ({p1_win_rate:.2f}%)")
    print(f"Player 2 wins: {metrics['p2_wins']} ({p2_win_rate:.2f}%)")
    print(f"Draws: {metrics['draws']} ({draw_rate:.2f}%)")
    print(f"Unfinished: {metrics['unfinished']} ({unfinished_rate:.2f}%)")
    print(f"Average steps: {avg_steps:.2f}")

    return metrics