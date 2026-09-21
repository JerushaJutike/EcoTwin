from pathlib import Path
import sys

from gymnasium.utils.env_checker import check_env


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from rl.env.ecotwin_env import EcoTwinEnv


def main() -> None:
    env = EcoTwinEnv()

    try:
        print(
            "Running Gymnasium environment checker..."
        )

        check_env(
            env,
            skip_render_check=True,
        )

        print(
            "Gymnasium environment check passed."
        )

    finally:
        env.close()


if __name__ == "__main__":
    main()