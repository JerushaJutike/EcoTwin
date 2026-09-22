"""
EcoTwin Reinforcement Learning Problem Definition

Defines:
- State / observation space
- Traffic-light actions
- Reward calculation

This module does not train an RL model.
It only defines the RL problem that the environment will use.
"""


# ---------------------------------------------------------
# STATE
# ---------------------------------------------------------

STATE_FEATURES = [
    "total_waiting_time",
    "average_speed",
    "vehicle_count",
    "co2_emission",
    "current_phase",
]


def get_state(
    total_waiting_time,
    average_speed,
    vehicle_count,
    co2_emission,
    current_phase,
):
    """
    Build the observation/state given to the RL agent.
    """

    return [
        float(total_waiting_time),
        float(average_speed),
        float(vehicle_count),
        float(co2_emission),
        float(current_phase),
    ]


# ---------------------------------------------------------
# ACTION
# ---------------------------------------------------------

ACTIONS = {
    0: "KEEP_CURRENT_PHASE",
    1: "SWITCH_PHASE",
}


def get_action_name(action):
    """
    Convert an action number into a readable action name.
    """

    return ACTIONS.get(action, "UNKNOWN_ACTION")


# ---------------------------------------------------------
# REWARD
# ---------------------------------------------------------

def calculate_reward(
    waiting_time,
    co2_emission,
    waiting_weight=1.0,
    co2_weight=0.01,
):
    """
    Calculate the EcoTwin reward.

    Lower waiting time and lower CO2 emissions
    produce a better reward.

    Reward = -(waiting penalty + CO2 penalty)
    """

    waiting_penalty = waiting_weight * float(waiting_time)
    co2_penalty = co2_weight * float(co2_emission)

    reward = -(waiting_penalty + co2_penalty)

    return reward