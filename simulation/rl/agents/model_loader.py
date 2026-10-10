import ast
import json
from pathlib import Path


def load_q_learning_model(model_path=None):
    """
    Load a saved Q-learning model from JSON.
    """

    if model_path is None:
        model_path = (
            Path(__file__).resolve().parent.parent
            / "models"
            / "trained_model"
            / "q_learning_model.json"
        )

    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model not found: {model_path}"
        )

    with open(
        model_path,
        "r",
        encoding="utf-8",
    ) as model_file:
        model_data = json.load(model_file)

    required_fields = {
        "algorithm",
        "action_count",
        "learning_rate",
        "discount_factor",
        "exploration_rate",
        "states",
    }

    missing_fields = (
        required_fields
        - model_data.keys()
    )

    if missing_fields:
        raise ValueError(
            "Invalid Q-learning model. "
            f"Missing fields: {sorted(missing_fields)}"
        )

    q_table = {}

    for state, values in model_data["states"].items():
        try:
            state_key = ast.literal_eval(
                state
            )
        except (
            ValueError,
            SyntaxError,
        ) as error:
            raise ValueError(
                f"Invalid model state key: {state}"
            ) from error

        if not isinstance(
            state_key,
            tuple,
        ):
            raise ValueError(
                "Model state keys must decode to tuples."
            )

        q_table[state_key] = values

    return {
        "algorithm":
            model_data["algorithm"],

        "action_count":
            model_data["action_count"],

        "learning_rate":
            model_data["learning_rate"],

        "discount_factor":
            model_data["discount_factor"],

        "exploration_rate":
            model_data["exploration_rate"],

        "q_table":
            q_table,
    }