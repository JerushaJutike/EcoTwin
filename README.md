# EcoTwin

EcoTwin is a reinforcement-learning-based urban traffic control system designed to reduce congestion and vehicle CO₂ emissions using SUMO traffic simulation, TraCI, PPO reinforcement learning, FastAPI, WebSockets, React, and Docker.

The project compares a conventional fixed-time traffic-light controller against a trained PPO agent at intersection `B1`, then visualizes the simulation and carbon-emission intensity through a live dashboard.

---

## Project Objective

The goal of EcoTwin is to build a digital-twin-style traffic simulation in which an RL agent controls a traffic signal and attempts to improve:

- Vehicle waiting time
- Traffic flow
- Average vehicle speed
- Local vehicle CO₂ emissions

The system combines simulation, reinforcement learning, backend APIs, real-time telemetry, visualization, and containerized deployment.

---

# System Architecture

```text
                    EcoTwin Architecture

                +-----------------------+
                |       SUMO City       |
                |  Traffic Simulation   |
                +-----------+-----------+
                            |
                            | TraCI
                            v
                +-----------------------+
                |   EcoTwin RL State    |
                |-----------------------|
                | Queue lengths         |
                | Waiting times         |
                | CO₂ emissions         |
                | Signal state          |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                |      PPO Agent        |
                |-----------------------|
                | Action 0: E/W Green   |
                | Action 1: N/S Green   |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | Traffic Light B1      |
                | SUMO Signal Control   |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | Simulation Service    |
                | FastAPI Backend       |
                +-----------+-----------+
                            |
                 REST API + WebSocket
                            |
                            v
                +-----------------------+
                |   React Dashboard     |
                |-----------------------|
                | Live traffic map      |
                | CO₂ heatmap           |
                | PPO decisions         |
                | Performance metrics   |
                | Simulation controls   |
                +-----------------------+
```

---

# Technology Stack

## Simulation
- SUMO
- TraCI
- SUMO traffic-light control
- SUMO vehicle emissions

## Machine Learning
- Python 3.12
- Gymnasium
- Stable-Baselines3
- PPO
- NumPy

## Backend
- FastAPI
- Uvicorn
- WebSockets
- Background simulation thread

## Frontend
- React
- TypeScript
- Vite
- Recharts
- SVG-based traffic visualization

## Deployment
- Docker
- Docker Compose
- Nginx
- WSL2 / Docker Desktop on Windows

---

# Traffic Network

EcoTwin uses a generated `3 × 3` SUMO grid network with nine traffic-light-controlled intersections:

```text
A0  A1  A2
B0  B1  B2
C0  C1  C2
```

The reinforcement-learning controller operates at `B1`.

The four incoming approaches to B1 are:

```text
North: A1B1_0
East:  B2B1_0
South: C1B1_0
West:  B0B1_0
```

---

# Traffic-Light Actions

The PPO agent has a discrete action space:

```text
Action 0
East / West green

Action 1
North / South green
```

SUMO signal phases at B1 are:

```text
Phase 0
GGggrrrrGGggrrrr
East / West green

Phase 1
yyyyrrrryyyyrrrr
East / West yellow

Phase 2
rrrrGGggrrrrGGgg
North / South green

Phase 3
rrrryyyyrrrryyyy
North / South yellow
```

Yellow transitions are handled automatically by the environment. The PPO agent does not directly choose yellow phases.

---

# RL State Space

The observation contains 13 normalized values:

```text
Queue North
Queue East
Queue South
Queue West

Waiting Time North
Waiting Time East
Waiting Time South
Waiting Time West

CO₂ North
CO₂ East
CO₂ South
CO₂ West

Current Green Direction
```

Observation shape:

```text
(13,)
```

All observations are normalized into `[0, 1]`.

Normalization constants:

```text
Queue:        20
Waiting Time: 400 seconds
CO₂:          60000 mg/s
```

---

# Reward Function

The reward is a weighted combination of queue length, waiting time, and CO₂ emissions.

```text
Queue:        0.30
Waiting Time: 0.35
CO₂:          0.35
```

Conceptually:

```text
reward =
    - queue_penalty
    - waiting_penalty
    - emission_penalty
```

A better traffic state therefore produces a reward closer to zero.

---

# RL Environment

The EcoTwin environment is implemented using Gymnasium.

```text
Action space:
Discrete(2)

Observation space:
Box(low=0, high=1, shape=(13,))
```

The controller makes a decision every 15 seconds. Yellow transition duration is 3 seconds.

When the action changes:

```text
3 seconds yellow
+
12 seconds new green
=
15 second decision interval
```

When the action remains unchanged:

```text
15 seconds green
```

---

# PPO Training

The PPO configuration uses:

```text
Policy:              MlpPolicy
Learning rate:       3e-4
n_steps:             256
Batch size:          64
Gamma:               0.99
GAE Lambda:          0.95
Clip range:          0.2
Entropy coefficient: 0.01
```

Initial training target:

```text
10,000 timesteps
```

Stable-Baselines3 completed:

```text
10,240 timesteps
```

because PPO collects complete rollout batches.

Trained model:

```text
rl/models/ppo_b1_initial.zip
```

The trained model file is intentionally ignored by Git.

---

# Baseline Results

Fixed-time SUMO controller:

```text
Vehicles:                     500
Simulation time:              1167 seconds
Completed trips:              500
Total CO₂:                    131535.192 g
Total waiting time:           20192 seconds
Average waiting time:         40.384 seconds / vehicle
Average speed:                22.579 km/h
```

---

# PPO Results

Initial PPO evaluation:

```text
Vehicles:                     500
Simulation time:              1164 seconds
Completed trips:              500
Total CO₂:                    123022.491 g
Total waiting time:           14863 seconds
Average waiting time:         29.726 seconds / vehicle
Average speed:                24.879 km/h
```

PPO decisions:

```text
Total decisions: 78
Action 0:        38
Action 1:        40
```

---

# PPO vs Fixed-Time Improvement

On the original evaluation scenario:

```text
Average waiting time
40.384 s → 29.726 s
26.39% reduction

Total CO₂
131535.192 g → 123022.491 g
6.47% reduction

Average speed
22.579 km/h → 24.879 km/h
10.19% increase
```

These results describe the tested EcoTwin scenario and should not be interpreted as universal performance guarantees.

---

# Multi-Scenario Evaluation

The trained PPO controller was evaluated across five reproducible traffic scenarios using seeds:

```text
11
22
33
44
55
```

Average results:

```text
Average Waiting Time
Fixed-Time: 36.313 ± 3.723 s
PPO:        27.731 ± 3.106 s
Improvement: 23.63%
```

```text
Total CO₂
Fixed-Time: 124647.855 ± 3782.803 g
PPO:        117350.930 ± 4141.300 g
Improvement: 5.85%
```

```text
Average Speed
Fixed-Time: 23.511 ± 1.032 km/h
PPO:        25.641 ± 1.095 km/h
Improvement: 9.06%
```

PPO improved waiting time, CO₂ emissions, and average speed in all five tested scenarios.

---

# Backend API

FastAPI provides both REST endpoints and WebSocket telemetry.

Default backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Health

```http
GET /health
```

Example:

```json
{
  "status": "ok"
}
```

## Project Status

```http
GET /api/status
```

## Experiment Results

```http
GET /api/results
GET /api/results/baseline
GET /api/results/ppo
GET /api/results/comparison
GET /api/results/multi_scenario
```

---

# Simulation API

```http
GET  /api/simulation/status
POST /api/simulation/start
POST /api/simulation/stop
POST /api/simulation/controller/ppo
POST /api/simulation/controller/fixed_time
```

The controller cannot be changed while a simulation is running.

---

# WebSocket Telemetry

Live simulation data is streamed through:

```text
ws://127.0.0.1:8000/ws/simulation
```

Approximately four snapshots are transmitted per second.

A snapshot includes:

```text
running
status
simulation_time
active_vehicles
departed_vehicles
arrived_vehicles
controller
current_action
decision_count
action_0_count
action_1_count
traffic_light
    id
    phase
    state
total_co2_mg_s
average_speed_mps
vehicles[]
    id
    x
    y
    speed_mps
    co2_mg_s
```

TraCI is accessed only by the simulation background thread. The WebSocket reads a thread-safe simulation snapshot instead of calling TraCI directly.

---

# React Dashboard

The dashboard displays:

- WebSocket connection status
- Simulation status
- Simulation time
- Active vehicle count
- Departed vehicles
- Arrived vehicles
- Live CO₂ emission rate
- Average vehicle speed
- Active controller
- PPO traffic direction
- PPO decision counts
- B1 traffic-light phase
- Live vehicle positions
- CO₂ emission-intensity heatmap
- Fixed-time vs PPO metrics
- Performance improvement chart
- Simulation start/stop controls
- PPO / fixed-time controller selection

Frontend development URL:

```text
http://localhost:5173
```

---

# CO₂ Heatmap

The dashboard creates a live spatial visualization using:

```text
vehicle x coordinate
vehicle y coordinate
vehicle CO₂ emission rate
```

Higher-emission vehicles generate larger and stronger emission regions.

The heatmap represents **vehicle CO₂ emission intensity**. It does **not** represent measured atmospheric CO₂ concentration.

A full atmospheric dispersion model would require additional variables such as:

- Wind speed
- Wind direction
- Atmospheric stability
- Temperature
- Street geometry
- Diffusion coefficients

---

# Project Structure

```text
EcoTwin/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── services/
│       ├── __init__.py
│       ├── results_service.py
│       └── simulation_service.py
│
├── data/
│   ├── raw/
│   │   ├── emissions.xml
│   │   └── tripinfo.xml
│   └── results/
│       ├── baseline_metrics.json
│       ├── ppo_metrics.json
│       ├── comparison_metrics.json
│       └── multi_scenario_results.json
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── SimulationControls.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.css
│   ├── Dockerfile
│   ├── package.json
│   └── package-lock.json
│
├── rl/
│   ├── env/
│   │   ├── ecotwin_env.py
│   │   ├── reward.py
│   │   └── state.py
│   ├── training/
│   │   └── train_ppo.py
│   ├── evaluation/
│   │   ├── evaluate_ppo.py
│   │   └── multi_scenario_evaluation.py
│   └── models/
│       └── ppo_b1_initial.zip
│
├── simulation/
│   ├── config/
│   │   └── ecotwin.sumocfg
│   ├── network/
│   │   └── ecotwin.net.xml
│   ├── routes/
│   │   ├── ecotwin.rou.xml
│   │   └── scenarios/
│   └── scripts/
│       ├── test_traci.py
│       ├── inspect_traffic_lights.py
│       ├── inspect_phases.py
│       ├── inspect_b1_lanes.py
│       ├── control_traffic_light.py
│       ├── run_baseline.py
│       └── generate_scenarios.py
│
├── backend.Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Local Installation

## Requirements

Install:

```text
Python 3.12
SUMO
Node.js
npm
Git
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

---

# Run Without Docker

## Backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

## Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# Run With Docker

Requirements:

```text
Docker Desktop
WSL2 on Windows
```

Build:

```bash
docker compose build
```

Start:

```bash
docker compose up
```

Open:

```text
Frontend:
http://localhost:5173

Backend:
http://127.0.0.1:8000

API Docs:
http://127.0.0.1:8000/docs
```

Stop:

```bash
docker compose down
```

The trained PPO model is mounted into the backend container:

```text
./rl/models:/app/rl/models:ro
```

SUMO runtime outputs are persisted using:

```text
./data/raw:/app/data/raw
```

---

# Train PPO

```bash
python rl/training/train_ppo.py
```

The model is saved under:

```text
rl/models/
```

---

# Evaluate PPO

Single-scenario evaluation:

```bash
python rl/evaluation/evaluate_ppo.py
```

Multi-scenario evaluation:

```bash
python rl/evaluation/multi_scenario_evaluation.py
```

---

# Generate Traffic Scenarios

```bash
python simulation/scripts/generate_scenarios.py
```

Generated scenarios are stored in:

```text
simulation/routes/scenarios/
```

---

# Limitations

## Single Controlled Intersection

Only intersection `B1` is controlled by reinforcement learning. A larger digital twin could deploy multi-agent RL across the complete network.

## Synthetic Traffic

The traffic demand is generated using SUMO tools rather than real city traffic data.

## Limited Training

The initial PPO model was trained for approximately 10,000 timesteps. More extensive training and hyperparameter tuning could produce different results.

## Emissions vs Dispersion

SUMO provides vehicle emission rates. The current carbon heatmap visualizes spatial emission intensity and does not implement atmospheric fluid-dynamics dispersion.

## Evaluation Scale

The reported multi-scenario experiment uses five reproducible synthetic traffic seeds. More scenarios would be required for stronger statistical conclusions.

---

# Future Work

Potential extensions include:

- Multi-intersection RL
- Multi-agent PPO
- DQN controller comparison
- Real traffic datasets
- Real road networks
- OpenStreetMap integration
- Weather-aware carbon dispersion
- Gaussian plume modelling
- Graph neural networks
- Traffic forecasting
- Pedestrian and public-transport integration
- Larger-scale city simulation
- Automated RL hyperparameter tuning
- Cloud deployment

---

# Demo Workflow

```text
1. Start EcoTwin using Docker Compose
2. Open the React dashboard
3. Confirm WebSocket Connected
4. Select PPO
5. Start Simulation
6. Show:
   - moving vehicles
   - live vehicle count
   - average speed
   - CO₂ emission rate
   - carbon heatmap
   - PPO direction changes
   - action counters
7. Stop Simulation
8. Select Fixed-Time
9. Start Simulation again
10. Show that PPO decision counters remain zero
11. Scroll to Fixed-Time vs PPO comparison
12. Explain:
    - waiting-time reduction
    - CO₂ reduction
    - speed improvement
13. Show FastAPI /docs if required
14. Explain the architecture:
    SUMO → TraCI → PPO → FastAPI → WebSocket → React
```

---

# Key Results

The central finding from the implemented test environment is that the trained PPO controller reduced waiting time and vehicle CO₂ emissions while increasing average speed compared with the fixed-time controller.

Original evaluation scenario:

```text
Waiting time reduction: 26.39%
CO₂ reduction:          6.47%
Average speed increase: 10.19%
```

Five-scenario average:

```text
Waiting time reduction: 23.63%
CO₂ reduction:          5.85%
Average speed increase: 9.06%
```

These results apply to the simulated EcoTwin scenarios used in this project.

---

# Project Status

```text
SUMO Network                Complete
TraCI Integration           Complete
Fixed-Time Baseline         Complete
RL State                    Complete
Reward Function             Complete
Gymnasium Environment       Complete
PPO Training                Complete
PPO Evaluation              Complete
Multi-Scenario Evaluation   Complete
FastAPI Backend             Complete
WebSocket Streaming         Complete
React Dashboard             Complete
CO₂ Heatmap                 Complete
Controller UI               Complete
Docker Deployment           Complete
```

EcoTwin is implemented as an end-to-end reinforcement-learning traffic-control prototype with real-time simulation monitoring and visualization.
