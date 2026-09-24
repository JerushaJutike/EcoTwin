from simulation.rl.environment.ecotwin_env import EcoTwinEnv
from simulation.rl.agents.q_learning_agent import QLearningAgent


def main():
    print("Starting EcoTwin Q-learning training...")

    env = EcoTwinEnv()

    agent = QLearningAgent(
        action_count=2,
        learning_rate=0.1,
        discount_factor=0.95,
        exploration_rate=1.0,
        exploration_decay=0.995,
        min_exploration_rate=0.01,
    )

    episodes = 20
    steps_per_episode = 10

    try:
        for episode in range(1, episodes + 1):

            state = env.reset()
            rl_state = state["rl_state"]

            total_reward = 0.0

            for step in range(steps_per_episode):

                action = agent.choose_action(rl_state)

                next_state, reward = env.step(action)

                next_rl_state = next_state["rl_state"]

                agent.update(
                    rl_state,
                    action,
                    reward,
                    next_rl_state,
                )

                rl_state = next_rl_state
                total_reward += reward

            agent.decay_exploration()

            print(
                f"Episode {episode:02d} | "
                f"Reward: {total_reward:.4f} | "
                f"Exploration: {agent.exploration_rate:.4f} | "
                f"States: {len(agent.q_table)}"
            )

        print("\nQ-learning training completed.")
        print(f"Total learned states: {len(agent.q_table)}")

    except Exception as error:
        print("\nQ-learning training failed.")
        print(f"Error: {error}")

    finally:
        env.close()
        print("SUMO connection closed.")


if __name__ == "__main__":
    main()