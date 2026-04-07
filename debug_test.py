from src.environment import OriginsEnv

print("\n=== ENVIRONMENT TEST ===")

env = OriginsEnv()
state = env.reset()

print("Initial State:", state)

for i in range(10):
    actions = env.get_valid_actions()

    if not actions:
        print("No actions available")
        break

    action = actions[0]
    next_state, reward, done, info = env.step(action)

    print(f"\nStep {i+1}")
    print("Action:", action)
    print("Reward:", reward)
    print("Done:", done)
    print("Info:", info)

    env.render()

    if done:
        break