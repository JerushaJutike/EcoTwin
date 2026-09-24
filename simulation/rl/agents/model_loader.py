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

    with open(model_path, "r") as model_file:
        model_data = json.load(model_file)

    q_table = {}

    for state, values in model_data["states"].items():
        state_key = eval(state)
        q_table[state_key] = values

    return {
        "algorithm": model_data["algorithm"],
        "action_count": model_data["action_count"],
        "learning_rate": model_data["learning_rate"],
        "discount_factor": model_data["discount_factor"],
        "exploration_rate": model_data["exploration_rate"],
        "q_table": q_table,
    }