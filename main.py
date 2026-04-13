import sys
sys.stdout.reconfigure(line_buffering=True)
from src.q_learning import (
    QLearningAgent,
    train_q_learning,
    evaluate_self_play,
    evaluate_agent_fair,
    evaluate_random_vs_random,
)
from src.dqn_agent import (
    DQNAgent,
    train_dqn,
    train_dqn_8x8,
    evaluate_dqn_self_play,
    evaluate_dqn_agent_fair,
    build_all_actions,
    build_action_index_map,
)
from src.environment import OriginsEnv
from src.constants import PLAYER_1, PLAYER_2


Q_MODEL_PATH = "trained_q_agent.json"
DQN_MODEL_PATH_4X4 = "trained_dqn_agent_4x4.pth"
DQN_MODEL_PATH_8X8 = "trained_dqn_agent_8x8.pth"


def print_last_training_info(agent, rewards, steps, p1_wins, p2_wins, draws):
    print("\nTraining complete.")
    print("=" * 50)
    print(f"Last 10 episode rewards: {rewards[-10:]}")
    print(f"Last 10 episode steps:   {steps[-10:]}")
    print(f"Last 10 Player 1 wins:   {p1_wins[-10:]}")
    print(f"Last 10 Player 2 wins:   {p2_wins[-10:]}")
    print(f"Last 10 draws:           {draws[-10:]}")


def choose_board_size():
    print("\nChoose board size:")
    print("1. 4x4")
    print("2. 8x8")
    choice = input("Enter 1 or 2: ").strip()
    return 8 if choice == "2" else 4


def parse_human_move(user_input: str):
    parts = user_input.strip().split()
    if len(parts) != 4:
        return None
    try:
        from_row, from_col, to_row, to_col = map(int, parts)
        return from_row, from_col, to_row, to_col
    except ValueError:
        return None


def train_and_save_q_agent():
    (
        agent,
        rewards,
        steps,
        p1_wins,
        p2_wins,
        draws,
    ) = train_q_learning(episodes=300, board_size=4)

    print_last_training_info(agent, rewards, steps, p1_wins, p2_wins, draws)
    agent.save_q_table(Q_MODEL_PATH)
    print(f"\nSaved trained Q-learning agent to: {Q_MODEL_PATH}")
    return agent


def load_q_agent():
    agent = QLearningAgent.load_q_table(Q_MODEL_PATH)
    print(f"\nLoaded trained Q-learning agent from: {Q_MODEL_PATH}")
    print(f"Loaded Q-values: {len(agent.q_table)}")
    return agent


def run_q_evaluations(agent, board_size=4):
    print("\nRunning Q-learning evaluations...")
    print("=" * 50)
    print(f"Board size: {board_size}x{board_size}")
    evaluate_self_play(agent, episodes=100, board_size=board_size)
    evaluate_agent_fair(agent, episodes_each_side=100, board_size=board_size)
    evaluate_random_vs_random(episodes=100, board_size=board_size)


def human_vs_q_ai(agent, board_size=4):
    env = OriginsEnv(board_size=board_size)
    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    state = env.reset()
    done = False

    print("\nHuman vs Q-Learning AI started!")
    print(f"Board size: {board_size}x{board_size}")
    print("You are Player 1.")
    print("Enter moves as: from_row from_col to_row to_col")

    if board_size == 8:
        print("\nNote: Q-learning agent was trained on 4x4.")
        print("AI quality on 8x8 may be limited.\n")

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
                    print("That move is not legal. Try again.")
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


def q_ai_vs_ai(agent, board_size=4):
    env = OriginsEnv(board_size=board_size)
    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    state = env.reset()
    done = False

    print("\nQ-Learning AI vs AI started!")
    print(f"Board size: {board_size}x{board_size}")

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


def train_and_save_dqn_agent_4x4():
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
        episodes=1000,
        board_size=4,
        include_tile_state=False,
    )

    print_last_training_info(agent, rewards, steps, p1_wins, p2_wins, draws)
    agent.save_model(DQN_MODEL_PATH_4X4)
    print(f"\nSaved trained DQN 4x4 agent to: {DQN_MODEL_PATH_4X4}")
    return agent, all_actions, action_to_index


def train_and_save_dqn_agent_8x8():
    (
        agent,
        rewards,
        steps,
        p1_wins,
        p2_wins,
        draws,
        all_actions,
        action_to_index,
    ) = train_dqn_8x8(episodes=4000)

    print_last_training_info(agent, rewards, steps, p1_wins, p2_wins, draws)
    agent.save_model(DQN_MODEL_PATH_8X8)
    print(f"\nSaved trained DQN 8x8 agent to: {DQN_MODEL_PATH_8X8}")
    return agent, all_actions, action_to_index


def load_dqn_agent(board_size=4):
    # fixed indentation bug — both branches now correctly aligned
    if board_size == 8:
        model_path = "trained_dqn_agent_8x8_best.pth"
        include_tile_state = False
    else:
        model_path = DQN_MODEL_PATH_4X4
        include_tile_state = False

    agent = DQNAgent.load_model(model_path)
    all_actions = build_all_actions(board_size)
    action_to_index = build_action_index_map(all_actions)

    print(f"\nLoaded trained DQN agent from: {model_path}")
    print(f"Board size for action space: {board_size}x{board_size}")
    print(f"State size: {agent.state_size}")
    print(f"Action size: {agent.action_size}")
    print(f"Tile-aware state: {include_tile_state}")

    return agent, all_actions, action_to_index, include_tile_state


def run_dqn_evaluations(
    agent,
    all_actions,
    action_to_index,
    board_size=4,
    include_tile_state=False,
):
    print("\nRunning DQN evaluations...")
    print("=" * 50)
    print(f"Board size: {board_size}x{board_size}")
    print(f"Tile-aware state: {include_tile_state}")

    evaluate_dqn_self_play(
        agent, all_actions, action_to_index,
        episodes=100, board_size=board_size,
        include_tile_state=include_tile_state,
    )
    evaluate_dqn_agent_fair(
        agent, all_actions, action_to_index,
        episodes_each_side=100, board_size=board_size,
        include_tile_state=include_tile_state,
    )
    evaluate_random_vs_random(episodes=100, board_size=board_size)


def human_vs_dqn_ai(
    agent,
    all_actions,
    action_to_index,
    board_size=4,
    include_tile_state=False,
):
    env = OriginsEnv(board_size=board_size, include_tile_state=include_tile_state)
    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    state = env.reset()
    done = False

    print("\nHuman vs DQN AI started!")
    print(f"Board size: {board_size}x{board_size}")
    print(f"Tile-aware state: {include_tile_state}")
    print("You are Player 1.")
    print("Enter moves as: from_row from_col to_row to_col")

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
                    print("That move is not legal. Try again.")
                    continue
                action = parsed
        else:
            print("DQN AI is thinking...")
            action = agent.choose_action(
                state, valid_actions, all_actions, action_to_index
            )
            if action is None:
                print("DQN AI could not select an action.")
                break
            print(f"DQN AI move: {action}")

        next_state, reward, done, info = env.step(action)
        state = next_state

    print("\nFinal board:")
    env.render()
    print("\nGame result:")
    if env.game.winner == PLAYER_1:
        print("You win!")
    elif env.game.winner == PLAYER_2:
        print("DQN AI wins!")
    else:
        print("Draw!")

    agent.epsilon = old_epsilon


def dqn_ai_vs_ai(
    agent,
    all_actions,
    action_to_index,
    board_size=4,
    include_tile_state=False,
):
    env = OriginsEnv(board_size=board_size, include_tile_state=include_tile_state)
    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    state = env.reset()
    done = False

    print("\nDQN AI vs AI started!")
    print(f"Board size: {board_size}x{board_size}")
    print(f"Tile-aware state: {include_tile_state}")

    while not done:
        env.render()
        print()

        valid_actions = env.get_valid_actions()
        if not valid_actions:
            print("No valid actions available.")
            break

        action = agent.choose_action(
            state, valid_actions, all_actions, action_to_index
        )
        if action is None:
            print("DQN AI could not select an action.")
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


def export_game_state(board_size=8):
    """
    Quick utility to export a game state as JSON.
    Useful for testing Unity integration later.
    """
    import json
    game_env = OriginsEnv(board_size=board_size)
    game_env.reset()
    state = game_env.game.get_game_state_for_export()
    print("\nExported game state:")
    print(json.dumps(state, indent=2))
    return state


def main():
    while True:
        print("\n" + "=" * 70)
        print("ORIGINS AI PROJECT")
        print("=" * 70)
        print("1.  Train new Q-learning agent and save (4x4)")
        print("2.  Load saved Q-learning agent")
        print("3.  Evaluate Q-learning agent")
        print("4.  Play Human vs Q-learning AI")
        print("5.  Watch Q-learning AI vs AI")
        print("6.  Train new DQN agent and save (4x4)")
        print("7.  Train new DQN agent and save (8x8)")
        print("8.  Evaluate DQN agent")
        print("9.  Play Human vs DQN AI")
        print("10. Watch DQN AI vs AI")
        print("11. Export game state to JSON (Unity prep)")
        print("12. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            train_and_save_q_agent()

        elif choice == "2":
            try:
                load_q_agent()
            except FileNotFoundError:
                print(f"No saved Q-learning model found at: {Q_MODEL_PATH}")

        elif choice == "3":
            try:
                agent = load_q_agent()
                board_size = choose_board_size()
                run_q_evaluations(agent, board_size=board_size)
            except FileNotFoundError:
                print(f"No saved Q-learning model found at: {Q_MODEL_PATH}")

        elif choice == "4":
            try:
                agent = load_q_agent()
                board_size = choose_board_size()
                human_vs_q_ai(agent, board_size=board_size)
            except FileNotFoundError:
                print(f"No saved Q-learning model found at: {Q_MODEL_PATH}")

        elif choice == "5":
            try:
                agent = load_q_agent()
                board_size = choose_board_size()
                q_ai_vs_ai(agent, board_size=board_size)
            except FileNotFoundError:
                print(f"No saved Q-learning model found at: {Q_MODEL_PATH}")

        elif choice == "6":
            train_and_save_dqn_agent_4x4()

        elif choice == "7":
            train_and_save_dqn_agent_8x8()

        elif choice == "8":
            board_size = choose_board_size()
            try:
                agent, all_actions, action_to_index, include_tile_state = load_dqn_agent(
                    board_size=board_size
                )
                run_dqn_evaluations(
                    agent, all_actions, action_to_index,
                    board_size=board_size,
                    include_tile_state=include_tile_state,
                )
            except FileNotFoundError:
                path = DQN_MODEL_PATH_8X8 if board_size == 8 else DQN_MODEL_PATH_4X4
                print(f"No saved DQN model found at: {path}")

        elif choice == "9":
            board_size = choose_board_size()
            try:
                agent, all_actions, action_to_index, include_tile_state = load_dqn_agent(
                    board_size=board_size
                )
                human_vs_dqn_ai(
                    agent, all_actions, action_to_index,
                    board_size=board_size,
                    include_tile_state=include_tile_state,
                )
            except FileNotFoundError:
                path = DQN_MODEL_PATH_8X8 if board_size == 8 else DQN_MODEL_PATH_4X4
                print(f"No saved DQN model found at: {path}")

        elif choice == "10":
            board_size = choose_board_size()
            try:
                agent, all_actions, action_to_index, include_tile_state = load_dqn_agent(
                    board_size=board_size
                )
                dqn_ai_vs_ai(
                    agent, all_actions, action_to_index,
                    board_size=board_size,
                    include_tile_state=include_tile_state,
                )
            except FileNotFoundError:
                path = DQN_MODEL_PATH_8X8 if board_size == 8 else DQN_MODEL_PATH_4X4
                print(f"No saved DQN model found at: {path}")

        elif choice == "11":
            board_size = choose_board_size()
            export_game_state(board_size=board_size)

        elif choice == "12":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1 to 12.")


if __name__ == "__main__":
    main()