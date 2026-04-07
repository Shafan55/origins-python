from src.q_learning import (
    QLearningAgent,
    train_q_learning,
    evaluate_self_play,
    evaluate_agent_fair,
    evaluate_random_vs_random,
)
from src.environment import OriginsEnv
from src.constants import PLAYER_1, PLAYER_2


MODEL_PATH = "trained_q_agent.json"


def print_last_training_info(agent, rewards, steps, p1_wins, p2_wins, draws):
    print("\nTraining complete.")
    print("=" * 50)
    print(f"Total learned Q-values: {len(agent.q_table)}")
    print(f"Last 10 episode rewards: {rewards[-10:]}")
    print(f"Last 10 episode steps: {steps[-10:]}")
    print(f"Last 10 Player 1 wins: {p1_wins[-10:]}")
    print(f"Last 10 Player 2 wins: {p2_wins[-10:]}")
    print(f"Last 10 draws: {draws[-10:]}")


def train_and_save_agent():
    (
        agent,
        rewards,
        steps,
        p1_wins,
        p2_wins,
        draws,
    ) = train_q_learning(episodes=300)

    print_last_training_info(agent, rewards, steps, p1_wins, p2_wins, draws)

    agent.save_q_table(MODEL_PATH)
    print(f"\nSaved trained agent to: {MODEL_PATH}")

    return agent


def load_agent():
    agent = QLearningAgent.load_q_table(MODEL_PATH)
    print(f"\nLoaded trained agent from: {MODEL_PATH}")
    print(f"Loaded Q-values: {len(agent.q_table)}")
    return agent


def run_evaluations(agent):
    print("\nRunning evaluations...")
    print("=" * 50)

    evaluate_self_play(agent, episodes=100)
    evaluate_agent_fair(agent, episodes_each_side=100)
    evaluate_random_vs_random(episodes=100)


def parse_human_move(user_input: str):
    parts = user_input.strip().split()
    if len(parts) != 4:
        return None

    try:
        from_row, from_col, to_row, to_col = map(int, parts)
        return from_row, from_col, to_row, to_col
    except ValueError:
        return None


def human_vs_ai(agent):
    """
    Human plays as Player 1
    AI plays as Player 2
    """
    env = OriginsEnv(board_size=4)

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    state = env.reset()
    done = False

    print("\nHuman vs AI started!")
    print("You are Player1.")
    print("Enter moves as: from_row from_col to_row to_col")
    print("Example: 0 0 1 0")

    while not done:
        env.render()
        print()

        current_player = env.game.current_player
        valid_actions = env.get_valid_actions()

        if not valid_actions:
            print("No valid actions available.")
            break

        if current_player == PLAYER_1:
            print("Your turn.")
            print("Valid actions:", valid_actions)

            action = None
            while action is None:
                user_input = input("Enter your move: ")
                parsed = parse_human_move(user_input)

                if parsed is None:
                    print("Invalid input format. Use: from_row from_col to_row to_col")
                    continue

                if parsed not in valid_actions:
                    print("That move is not legal. Please choose a valid move.")
                    continue

                action = parsed
        else:
            print("AI is thinking...")
            action = agent.choose_action(state, valid_actions)

            if action is None:
                print("AI could not select an action.")
                break

            print(f"AI move: {action}")

        next_state, reward, done, info = env.step(action)
        state = next_state

    print("\nFinal board:")
    env.render()

    print("\nGame result:")
    if env.game.winner == PLAYER_1:
        print("You win!")
    elif env.game.winner == PLAYER_2:
        print("AI wins!")
    else:
        print("Draw!")

    agent.epsilon = old_epsilon


def ai_vs_ai(agent):
    env = OriginsEnv(board_size=4)

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    state = env.reset()
    done = False

    print("\nAI vs AI started!")

    while not done:
        env.render()
        print()

        valid_actions = env.get_valid_actions()
        if not valid_actions:
            print("No valid actions available.")
            break

        action = agent.choose_action(state, valid_actions)
        if action is None:
            print("AI could not select an action.")
            break

        print(f"{env.game.current_player} move: {action}")

        next_state, reward, done, info = env.step(action)
        state = next_state

    print("\nFinal board:")
    env.render()

    print("\nGame result:")
    if env.game.winner is None:
        print("Draw!")
    else:
        print(f"Winner: {env.game.winner}")

    agent.epsilon = old_epsilon


def main():
    while True:
        print("\n" + "=" * 50)
        print("ORIGINS AI PROJECT")
        print("=" * 50)
        print("1. Train new agent and save")
        print("2. Load saved agent")
        print("3. Evaluate loaded agent")
        print("4. Play Human vs AI")
        print("5. Watch AI vs AI")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            train_and_save_agent()

        elif choice == "2":
            try:
                load_agent()
            except FileNotFoundError:
                print(f"No saved model found at: {MODEL_PATH}")

        elif choice == "3":
            try:
                agent = load_agent()
                run_evaluations(agent)
            except FileNotFoundError:
                print(f"No saved model found at: {MODEL_PATH}")

        elif choice == "4":
            try:
                agent = load_agent()
                human_vs_ai(agent)
            except FileNotFoundError:
                print(f"No saved model found at: {MODEL_PATH}")

        elif choice == "5":
            try:
                agent = load_agent()
                ai_vs_ai(agent)
            except FileNotFoundError:
                print(f"No saved model found at: {MODEL_PATH}")

        elif choice == "6":
            print("Goodbye.")
            break

        else:
            print("Invalid choice. Please select 1, 2, 3, 4, 5, or 6.")


if __name__ == "__main__":
    main()