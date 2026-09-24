from simulation.rl.environment.ecotwin_env import EcoTwinEnv
from simulation.rl.agents.rl_controller import RLController


def main():
    print("Starting EcoTwin RL controller test...")

    env = EcoTwinEnv()
    controller = RLController()

    try:
        state = env.reset()
        rl_state = state["rl_state"]

        print("\nInitial RL state:")
        print(rl_state)

        for step_number in range(5):

            action = controller.choose_action(rl_state)

            print(f"\nStep {step_number + 1}")
            print(f"Selected action: {action}")

            next_state, reward = env.step(action)

            next_rl_state = next_state["rl_state"]

            print("Next RL state:")
            print(next_rl_state)

            print(f"Reward: {reward:.4f}")

            rl_state = next_rl_state

        print("\nRL controller test completed successfully.")

    except Exception as error:
        print("\nRL controller test failed.")
        print(f"Error: {error}")

    finally:
        env.close()
        print("SUMO connection closed.")


if __name__ == "__main__":
    main()