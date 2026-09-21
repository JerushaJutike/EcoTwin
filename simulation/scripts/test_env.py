from pathlib import Path
import sys

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from rl.env.ecotwin_env import EcoTwinEnv


def main() -> None:
    env = EcoTwinEnv()

    try:
        observation, info = env.reset()

        print("=" * 70)
        print("EcoTwin Environment Test")
        print("=" * 70)

        print(
            f"Observation shape: "
            f"{observation.shape}"
        )

        print(
            f"Initial simulation time: "
            f"{info['simulation_time']}"
        )

        print(
            f"Action space: "
            f"{env.action_space}"
        )

        print(
            f"Observation space: "
            f"{env.observation_space}"
        )

        total_reward = 0.0

        for step in range(20):
            action = env.action_space.sample()

            (
                observation,
                reward,
                terminated,
                truncated,
                info,
            ) = env.step(action)

            total_reward += reward

            print(
                f"Step={step + 1:2d} | "
                f"Action={action} | "
                f"Time={info['simulation_time']:6.1f} | "
                f"Reward={reward:8.4f} | "
                f"Total={total_reward:8.4f}"
            )

            assert (
                observation.shape == (13,)
            )

            assert np.all(
                np.isfinite(observation)
            )

            if terminated or truncated:
                print(
                    "Episode finished."
                )
                break

    finally:
        env.close()


if __name__ == "__main__":
    main()