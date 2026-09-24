from simulation.rl.environment.ecotwin_env import EcoTwinEnv


def main():
    print("Starting EcoTwin RL environment test...")

    env = EcoTwinEnv()

    try:
        state = env.reset()

        print("\nInitial state:")
        print(state)

        for step_number in range(5):

            action = step_number % 2

            print(f"\nStep {step_number + 1}")
            print(f"Action: {action}")

            state, reward = env.step(action)

            print("State:")
            print(state)

            print(f"Reward: {reward:.4f}")

        print("\nEnvironment test completed successfully.")

    except Exception as error:
        print("\nEnvironment test failed.")
        print(f"Error: {error}")

    finally:
        env.close()
        print("SUMO connection closed.")


if __name__ == "__main__":
    main()