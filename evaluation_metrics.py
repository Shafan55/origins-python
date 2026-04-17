import matplotlib.pyplot as plt
import numpy as np

from src.dqn_agent import (
    train_dqn,
    RandomAgent as DQNRandomAgent,
    evaluate_dqn_agent_fair,
)
from src.environment import OriginsEnv
from src.constants import PLAYER_1, PLAYER_2


def rolling_mean(values, window=50):
    if len(values) < window:
        return np.array(values, dtype=float)
    return np.convolve(values, np.ones(window) / window, mode="valid")


def plot_training_curves(rewards, steps, p1_wins, p2_wins, draws, title="DQN Training"):
    episodes = np.arange(1, len(rewards) + 1)

    plt.figure(figsize=(10, 5))
    plt.plot(episodes, rewards)
    plt.title(f"{title} Reward per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(episodes, steps)
    plt.title(f"{title} Steps per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Steps")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(rolling_mean(p1_wins, 50), label="P1 wins (rolling)")
    plt.plot(rolling_mean(p2_wins, 50), label="P2 wins (rolling)")
    plt.plot(rolling_mean(draws, 50), label="Draws (rolling)")
    plt.title(f"{title} Outcomes (Rolling)")
    plt.xlabel("Episode")
    plt.ylabel("Rate")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_eval_bar(metrics, title="DQN Fair Evaluation"):
    labels = ["Wins", "Losses", "Draws", "Unfinished"]
    values = [
        metrics.get("wins", 0),
        metrics.get("losses", 0),
        metrics.get("draws", 0),
        metrics.get("unfinished", 0),
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.title(title)
    plt.ylabel("Count")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()


def plot_histogram(values, title, xlabel):
    plt.figure(figsize=(9, 5))
    plt.hist(values, bins=20)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def evaluate_detailed_dqn(
    agent,
    all_actions,
    action_to_index,
    episodes=50,
    board_size=8,
    include_tile_state=False,
):
    random_agent = DQNRandomAgent()
    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    metrics = {
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "unfinished": 0,
        "steps": [],
        "captures_per_game": [],
        "progress_per_game": [],
        "goal_progress_per_game": [],
        "repeat_events_per_game": [],
    }

    for _ in range(episodes):
        env = OriginsEnv(board_size=board_size, include_tile_state=include_tile_state)
        state = env.reset()
        done = False

        total_captures = 0
        total_progress = 0
        total_goal_progress = 0
        total_repeats = 0
        step_count = 0

        while not done:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break

            current_player = env.game.current_player

            if current_player == PLAYER_1:
                action = agent.choose_action(
                    state, valid_actions, all_actions, action_to_index
                )
            else:
                action = random_agent.choose_action(
                    state, valid_actions, all_actions, action_to_index
                )

            if action is None:
                break

            next_state, reward, done, info = env.step(action)
            state = next_state
            step_count += 1

            total_captures += info.get("captured_count", 0)
            total_progress += info.get("progress_delta", 0)
            total_goal_progress += info.get("goal_progress_delta", 0)
            total_repeats += max(info.get("repeat_count", 1) - 1, 0)

        metrics["steps"].append(step_count)
        metrics["captures_per_game"].append(total_captures)
        metrics["progress_per_game"].append(total_progress)
        metrics["goal_progress_per_game"].append(total_goal_progress)
        metrics["repeat_events_per_game"].append(total_repeats)

        winner = env.game.winner
        if not env.game.game_over:
            metrics["unfinished"] += 1
        elif winner == PLAYER_1:
            metrics["wins"] += 1
        elif winner == PLAYER_2:
            metrics["losses"] += 1
        else:
            metrics["draws"] += 1

    agent.epsilon = old_epsilon
    return metrics


def print_summary(metrics):
    total_finished = metrics["wins"] + metrics["losses"] + metrics["draws"]
    total_games = total_finished + metrics["unfinished"]

    print("\nDETAILED DQN 8x8 SUMMARY")
    print("=" * 40)
    print(f"Total games: {total_games}")
    print(f"Wins: {metrics['wins']}")
    print(f"Losses: {metrics['losses']}")
    print(f"Draws: {metrics['draws']}")
    print(f"Unfinished: {metrics['unfinished']}")
    print(f"Average steps: {np.mean(metrics['steps']):.2f}")
    print(f"Average captures/game: {np.mean(metrics['captures_per_game']):.2f}")
    print(f"Average progress/game: {np.mean(metrics['progress_per_game']):.2f}")
    print(f"Average goal progress/game: {np.mean(metrics['goal_progress_per_game']):.2f}")
    print(f"Average repeat events/game: {np.mean(metrics['repeat_events_per_game']):.2f}")

    if total_games > 0:
        print(f"Win rate: {metrics['wins'] / total_games * 100:.2f}%")
        print(f"Loss rate: {metrics['losses'] / total_games * 100:.2f}%")
        print(f"Draw rate: {metrics['draws'] / total_games * 100:.2f}%")
        print(f"Unfinished rate: {metrics['unfinished'] / total_games * 100:.2f}%")


def run_dqn_pipeline_8x8():
    (
        agent,
        rewards,
        steps,
        p1_wins,
        p2_wins,
        draws,
        all_actions,
        action_to_index,
    ) = train_dqn(
        episodes=2000,
        board_size=8,
        include_tile_state=False,
        checkpoint_prefix="trained_dqn_agent_8x8",
    )

    plot_training_curves(
        rewards=rewards,
        steps=steps,
        p1_wins=p1_wins,
        p2_wins=p2_wins,
        draws=draws,
        title="DQN 8x8",
    )

    fair_metrics = evaluate_dqn_agent_fair(
        agent,
        all_actions,
        action_to_index,
        episodes_each_side=50,
        board_size=8,
        include_tile_state=False,
    )

    plot_eval_bar(fair_metrics, title="DQN 8x8 Fair Evaluation")

    detailed = evaluate_detailed_dqn(
        agent,
        all_actions,
        action_to_index,
        episodes=50,
        board_size=8,
        include_tile_state=False,
    )

    print_summary(detailed)

    plot_histogram(
        detailed["captures_per_game"],
        "DQN 8x8 Captures per Game",
        "Captures",
    )
    plot_histogram(
        detailed["progress_per_game"],
        "DQN 8x8 Progress per Game",
        "Progress",
    )
    plot_histogram(
        detailed["goal_progress_per_game"],
        "DQN 8x8 Goal Progress per Game",
        "Goal Progress",
    )
    plot_histogram(
        detailed["repeat_events_per_game"],
        "DQN 8x8 Repetition Events",
        "Repeat Events",
    )
    plot_histogram(
        detailed["steps"],
        "DQN 8x8 Steps per Game",
        "Steps",
    )


if __name__ == "__main__":
    run_dqn_pipeline_8x8()