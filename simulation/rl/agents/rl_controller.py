from simulation.rl.agents.model_loader import load_q_learning_model


class RLController:
    """
    Controls the SUMO traffic light using
    the trained Q-learning model.
    """

    def __init__(self):
        self.model = load_q_learning_model()

        self.q_table = self.model["q_table"]
        self.action_count = self.model["action_count"]

    def choose_action(self, rl_state):
        """
        Select the action with the highest
        learned Q-value for the current state.
        """

        state_key = tuple(
            round(float(value), 2)
            for value in rl_state
        )

        if state_key in self.q_table:
            q_values = self.q_table[state_key]

            return q_values.index(
                max(q_values)
            )

        # If the exact state was not seen
        # during training, choose action 0.
        return 0