from src.q_learning import train_q_learning, evaluate_agent


def main():
    print("Starting Q-learning training...")
    agent, rewards = train_q_learning(episodes=300)

    print("\nTraining complete.")
    print(f"Total learned Q-values: {len(agent.q_table)}")
    print(f"Last 10 episode rewards: {rewards[-10:]}")

    evaluate_agent(agent, episodes=2)


if __name__ == "__main__":
    main()