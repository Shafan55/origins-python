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
            max_future_q = max(self.get_q_value(next_state, next_action) for next_action in next_valid_actions)
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

    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        step_count = 0
        max_steps = 50

        while not done and step_count < max_steps:
            valid_actions = env.get_valid_actions()
            action = agent.choose_action(state, valid_actions)

            if action is None:
                break

            next_state, reward, done, info = env.step(action)
            next_valid_actions = env.get_valid_actions()

            agent.update_q_value(state, action, reward, next_state, next_valid_actions)

            state = next_state
            total_reward += reward
            step_count += 1

        agent.decay_epsilon()
        episode_rewards.append(total_reward)

        if (episode + 1) % 50 == 0:
            average_reward = sum(episode_rewards[-50:]) / 50
            print(
                f"Episode {episode + 1}/{episodes} | "
                f"Average Reward (last 50): {average_reward:.2f} | "
                f"Epsilon: {agent.epsilon:.3f} | "
                f"Q-table size: {len(agent.q_table)}"
            )

    return agent, episode_rewards


def evaluate_agent(agent, episodes: int = 3):
    env = OriginsEnv(board_size=4)

    print("\nEVALUATION RUNS")
    print("=" * 40)

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    for episode in range(episodes):
        state = env.reset()
        done = False
        step_count = 0
        max_steps = 20

        print(f"\nEvaluation Episode {episode + 1}")
        env.render()

        while not done and step_count < max_steps:
            valid_actions = env.get_valid_actions()
            action = agent.choose_action(state, valid_actions)

            if action is None:
                print("No valid actions available.")
                break

            print(f"\nChosen action: {action}")
            next_state, reward, done, info = env.step(action)
            print(f"Reward: {reward} | Done: {done} | Info: {info}")
            env.render()

            state = next_state
            step_count += 1

        print(f"Episode finished in {step_count} steps.")

    agent.epsilon = old_epsilon