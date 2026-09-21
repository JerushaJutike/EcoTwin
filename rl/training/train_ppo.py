from __future__ import annotations

from pathlib import Path
import sys

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from rl.env.ecotwin_env import EcoTwinEnv


MODELS_DIR = (
    PROJECT_ROOT
    / "rl"
    / "models"
)

MODEL_PATH = (
    MODELS_DIR
    / "ppo_b1_initial"
)


def main() -> None:
    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("EcoTwin PPO Training")
    print("=" * 70)

    env = EcoTwinEnv()

    env = Monitor(
        env
    )

    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=256,
        batch_size=64,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        verbose=1,
        device="auto",
    )

    try:
        model.learn(
            total_timesteps=10_000,
            progress_bar=True,
        )

        model.save(
            str(MODEL_PATH)
        )

        print("\nTraining completed.")

        print(
            f"Model saved to:\n"
            f"{MODEL_PATH}.zip"
        )

    finally:
        env.close()


if __name__ == "__main__":
    main()