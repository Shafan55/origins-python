import random
from src.environment import OriginsEnv


class QLearningAgent:
    def __init__(
        self,
        alpha: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
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
            action for action, q_value in zip(valid_actions, q_values) if q_value == max_q
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


def train_q_learning(episodes: int = 500):
    env = OriginsEnv(board_size=4)
    agent = QLearningAgent()

    episode_rewards = []
    episode_steps = []
    win_count = 0

    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        step_count = 0
        max_steps = 50

        while not done and step_count < max_steps:
            valid_actions = env.get_valid_actions()

            # ✅ SMART ACTION PRUNING
            MAX_ACTIONS = 10
            if len(valid_actions) > MAX_ACTIONS:
                valid_actions = sorted(
                    valid_actions,
                    key=lambda a: agent.get_q_value(state, a),
                    reverse=True
                )[:MAX_ACTIONS]

            action = agent.choose_action(state, valid_actions)

            if action is None:
                break

            next_state, reward, done, info = env.step(action)

            original_reward = reward

            if not done:
                reward -= 0.01

            if done:
                if original_reward > 0:
                    reward = 1.0
                elif original_reward < 0:
                    reward = -1.0
                else:
                    reward = 0.0

            next_valid_actions = env.get_valid_actions()

            agent.update_q_value(state, action, reward, next_state, next_valid_actions)

            state = next_state
            total_reward += reward
            step_count += 1

            if done and original_reward > 0:
                win_count += 1

        # timeout penalty
        if not done:
            agent.update_q_value(state, action, -1.0, state, [])

        agent.decay_epsilon()
        episode_rewards.append(total_reward)
        episode_steps.append(step_count)

        if (episode + 1) % 50 == 0:
            average_reward = sum(episode_rewards[-50:]) / 50
            average_steps = sum(episode_steps[-50:]) / 50
            recent_wins = sum(1 for r in episode_rewards[-50:] if r > 0)

            print(
                f"Episode {episode + 1}/{episodes} | "
                f"Avg Reward (last 50): {average_reward:.2f} | "
                f"Avg Steps (last 50): {average_steps:.2f} | "
                f"Wins (last 50): {recent_wins}/50 | "
                f"Epsilon: {agent.epsilon:.3f} | "
                f"Q-table size: {len(agent.q_table)}"
            )

    overall_average_reward = sum(episode_rewards) / len(episode_rewards)
    overall_average_steps = sum(episode_steps) / len(episode_steps)
    win_rate = (win_count / episodes) * 100

    print("\nTRAINING SUMMARY")
    print("=" * 50)
    print(f"Total episodes: {episodes}")
    print(f"Overall average reward: {overall_average_reward:.2f}")
    print(f"Overall average steps: {overall_average_steps:.2f}")
    print(f"Total wins: {win_count}/{episodes}")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Final epsilon: {agent.epsilon:.3f}")
    print(f"Final Q-table size: {len(agent.q_table)}")

    return agent, episode_rewards, episode_steps


def evaluate_agent(agent, episodes: int = 100, render: bool = False):
    env = OriginsEnv(board_size=4)

    print("\nEVALUATION RUNS")
    print("=" * 40)

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    metrics = {
        "wins": 0,
        "draws": 0,
        "unfinished": 0,
        "total_steps": 0,
    }

    for episode in range(episodes):
        state = env.reset()
        done = False
        step_count = 0
        max_steps = 50
        final_reward = 0

        while not done and step_count < max_steps:
            valid_actions = env.get_valid_actions()

            MAX_ACTIONS = 10
            if len(valid_actions) > MAX_ACTIONS:
                valid_actions = sorted(
                    valid_actions,
                    key=lambda a: agent.get_q_value(state, a),
                    reverse=True
                )[:MAX_ACTIONS]

            action = agent.choose_action(state, valid_actions)

            if action is None:
                break

            next_state, reward, done, info = env.step(action)
            final_reward = reward

            state = next_state
            step_count += 1

        if not done:
            metrics["unfinished"] += 1
        elif final_reward > 0:
            metrics["wins"] += 1
        elif final_reward == 0:
            metrics["draws"] += 1

        metrics["total_steps"] += step_count

    print("\nEVALUATION SUMMARY")
    print("=" * 40)

    win_rate = (metrics["wins"] / episodes) * 100
    unfinished_rate = (metrics["unfinished"] / episodes) * 100
    avg_steps = metrics["total_steps"] / episodes
    losses = episodes - metrics["wins"] - metrics["draws"] - metrics["unfinished"]

    print(f"Episodes: {episodes}")
    print(f"Wins: {metrics['wins']} ({win_rate:.2f}%)")
    print(f"Draws: {metrics['draws']} (0.00%)")
    print(f"Unfinished: {metrics['unfinished']} ({unfinished_rate:.2f}%)")
    print(f"Losses: {losses}")
    print(f"Average steps: {avg_steps:.2f}")

    agent.epsilon = old_epsilon


def evaluate_random_agent(episodes: int = 20):
    env = OriginsEnv(board_size=4)
    wins = 0
    total_steps = 0

    print("\nRANDOM BASELINE EVALUATION")
    print("=" * 40)

    for _ in range(episodes):
        env.reset()
        done = False
        step_count = 0
        max_steps = 20
        final_reward = 0

        while not done and step_count < max_steps:
            valid_actions = env.get_valid_actions()

            if not valid_actions:
                break

            action = random.choice(valid_actions)
            _, reward, done, _ = env.step(action)
            final_reward = reward
            step_count += 1

        if done and final_reward > 0:
            wins += 1

        total_steps += step_count

    win_rate = (wins / episodes) * 100
    average_steps = total_steps / episodes

    print(f"Wins: {wins}/{episodes}")
    print(f"Random agent win rate: {win_rate:.2f}%")
    print(f"Average steps: {average_steps:.2f}")

    return {
        "wins": wins,
        "episodes": episodes,
        "win_rate": win_rate,
        "average_steps": average_steps,
    }


def compare_agents(agent, trained_episodes: int = 20, random_episodes: int = 20):
    print("\nAGENT COMPARISON")
    print("=" * 50)

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    env = OriginsEnv(board_size=4)
    trained_wins = 0
    trained_total_steps = 0

    for _ in range(trained_episodes):
        state = env.reset()
        done = False
        step_count = 0
        max_steps = 20
        final_reward = 0

        while not done and step_count < max_steps:
            valid_actions = env.get_valid_actions()

            MAX_ACTIONS = 10
            if len(valid_actions) > MAX_ACTIONS:
                valid_actions = sorted(
                    valid_actions,
                    key=lambda a: agent.get_q_value(state, a),
                    reverse=True
                )[:MAX_ACTIONS]

            action = agent.choose_action(state, valid_actions)

            if action is None:
                break

            next_state, reward, done, _ = env.step(action)
            state = next_state
            final_reward = reward
            step_count += 1

        if done and final_reward > 0:
            trained_wins += 1

        trained_total_steps += step_count

    trained_win_rate = (trained_wins / trained_episodes) * 100
    trained_average_steps = trained_total_steps / trained_episodes

    agent.epsilon = old_epsilon

    random_results = evaluate_random_agent(episodes=random_episodes)

    print("\nCOMPARISON SUMMARY")
    print("=" * 50)
    print(
        f"Trained agent -> Wins: {trained_wins}/{trained_episodes} | "
        f"Win rate: {trained_win_rate:.2f}% | "
        f"Average steps: {trained_average_steps:.2f}"
    )
    print(
        f"Random agent  -> Wins: {random_results['wins']}/{random_results['episodes']} | "
        f"Win rate: {random_results['win_rate']:.2f}% | "
        f"Average steps: {random_results['average_steps']:.2f}"
    )