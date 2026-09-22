import random


class QLearningAgent:
    """
    Basic Q-learning agent for EcoTwin.

    The agent learns which traffic-light action
    gives better rewards for observed traffic states.
    """

    def __init__(
        self,
        action_count=2,
        learning_rate=0.1,
        discount_factor=0.95,
        exploration_rate=1.0,
        exploration_decay=0.995,
        min_exploration_rate=0.01,
    ):
        self.action_count = action_count

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate

        self.q_table = {}

    def _state_key(self, state):
        """
        Convert an RL state into a dictionary key.
        """

        return tuple(
            round(float(value), 2)
            for value in state
        )

    def _ensure_state(self, state):
        """
        Create Q-values for a new state.
        """

        state_key = self._state_key(state)

        if state_key not in self.q_table:
            self.q_table[state_key] = [
                0.0
                for _ in range(self.action_count)
            ]

        return state_key

    def choose_action(self, state):
        """
        Choose an action using epsilon-greedy exploration.
        """

        state_key = self._ensure_state(state)

        if random.random() < self.exploration_rate:
            return random.randrange(
                self.action_count
            )

        q_values = self.q_table[state_key]

        return q_values.index(
            max(q_values)
        )

    def update(
        self,
        state,
        action,
        reward,
        next_state,
    ):
        """
        Update the Q-value using the Q-learning rule.
        """

        state_key = self._ensure_state(state)
        next_state_key = self._ensure_state(
            next_state
        )

        current_q = self.q_table[state_key][action]

        best_next_q = max(
            self.q_table[next_state_key]
        )

        updated_q = current_q + (
            self.learning_rate
            * (
                reward
                + (
                    self.discount_factor
                    * best_next_q
                )
                - current_q
            )
        )

        self.q_table[state_key][action] = updated_q

    def decay_exploration(self):
        """
        Gradually reduce random exploration.
        """

        self.exploration_rate = max(
            self.min_exploration_rate,
            self.exploration_rate
            * self.exploration_decay,
        )