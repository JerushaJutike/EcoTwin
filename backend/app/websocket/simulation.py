import asyncio

import traci
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from simulation.rl.agents.rl_controller import RLController
from simulation.rl.environment.ecotwin_env import EcoTwinEnv


router = APIRouter()


def build_live_state(simulation_time):
    """
    Build a JSON-serializable snapshot of the current SUMO state.
    """

    vehicle_ids = traci.vehicle.getIDList()

    vehicles = []

    total_co2 = 0.0
    total_speed = 0.0
    total_waiting_time = 0.0

    for vehicle_id in vehicle_ids:
        x, y = traci.vehicle.getPosition(vehicle_id)

        speed = traci.vehicle.getSpeed(vehicle_id)
        co2 = traci.vehicle.getCO2Emission(vehicle_id)
        waiting_time = (
            traci.vehicle.getAccumulatedWaitingTime(
                vehicle_id
            )
        )

        vehicles.append(
            {
                "id": vehicle_id,
                "x": x,
                "y": y,
                "speed": speed,
                "co2": co2,
                "waiting_time": waiting_time,
            }
        )

        total_co2 += co2
        total_speed += speed
        total_waiting_time += waiting_time

    vehicle_count = len(vehicles)

    if vehicle_count > 0:
        average_speed = total_speed / vehicle_count
    else:
        average_speed = 0.0

    traffic_light_phase = (
        traci.trafficlight.getPhase("J1")
    )

    return {
        "simulation_time": simulation_time,
        "vehicle_count": vehicle_count,
        "vehicles": vehicles,
        "metrics": {
            "co2": total_co2,
            "waiting_time": total_waiting_time,
            "average_speed": average_speed,
        },
        "traffic_light": {
            "id": "J1",
            "phase": traffic_light_phase,
        },
    }


@router.websocket("/ws/simulation")
async def simulation_websocket(
    websocket: WebSocket,
):
    """
    Stream live SUMO simulation state to the frontend.

    The trained RL agent selects a traffic-light action
    every 10 SUMO seconds. A live state snapshot is sent
    after every simulation second.
    """

    await websocket.accept()

    env = EcoTwinEnv()
    controller = RLController()

    simulation_steps = 200
    decision_interval = 10

    try:
        state = env.reset()
        rl_state = state["rl_state"]

        for simulation_second in range(
            simulation_steps
        ):
            if (
                simulation_second
                % decision_interval
                == 0
            ):
                action = controller.choose_action(
                    rl_state
                )

                env.apply_action(action)

            traci.simulationStep()

            state = env.get_state()
            rl_state = state["rl_state"]

            live_state = build_live_state(
                simulation_second + 1
            )

            await websocket.send_json(
                live_state
            )

            # Slow down delivery so the browser can
            # visually follow the simulation.
            await asyncio.sleep(0.1)

        await websocket.send_json(
            {
                "type": "simulation_complete",
                "simulation_time": simulation_steps,
            }
        )

    except WebSocketDisconnect:
        pass

    except Exception as error:
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": str(error),
                }
            )
        except Exception:
            pass

    finally:
        env.close()