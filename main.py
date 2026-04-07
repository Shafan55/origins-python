from src.q_learning import train_q_learning, evaluate_agent, compare_agents


def main():
    print("Starting Q-learning training...")

    agent, rewards, steps = train_q_learning(episodes=300)

    print("\nTraining complete.")
    print(f"Total learned Q-values: {len(agent.q_table)}")
    print(f"Last 10 episode rewards: {rewards[-10:]}")
    print(f"Last 10 episode steps: {steps[-10:]}")

    evaluate_agent(agent, episodes=2)
    compare_agents(agent, trained_episodes=20, random_episodes=20)


if __name__ == "__main__":
    main()