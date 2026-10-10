# EcoTwin

EcoTwin is a reinforcement-learning-based urban traffic and carbon simulation system built with SUMO, FastAPI, React, Leaflet, and Q-learning.

The project compares a fixed-time traffic-light baseline with a reinforcement-learning controller and visualizes both completed evaluation results and live simulation state.

## Features

- SUMO-based urban traffic simulation
- Fixed-time baseline controller
- Q-learning traffic-light controller
- Baseline vs RL performance comparison
- CO₂ emissions analysis
- Waiting-time analysis
- Average-speed analysis
- FastAPI REST API
- FastAPI WebSocket live simulation stream
- Real-time vehicle positions
- Live traffic-light phase
- Live CO₂, waiting time, and average speed metrics
- React dashboard
- Leaflet map
- Live carbon heatmap
- Baseline vs RL charts and comparison table
- Docker configuration

## Project Architecture

```text
SUMO
  |
  v
TraCI simulation environment
  |
  +--------------------+
  |                    |
  v                    v
Fixed-time        Q-learning
controller        controller
  |                    |
  +---------+----------+
            |
            v
      Evaluation results
            |
            v
        JSON results
            |
            v
        FastAPI REST
            |
            v
      React analytics UI

Live simulation path:

SUMO
  |
  v
TraCI
  |
  v
FastAPI WebSocket
  |
  v
React / Leaflet
  |
  +--> moving vehicle markers
  +--> live CO₂ heatmap
  +--> live metrics
  +--> traffic-light phase
```

## Technology Stack

### Backend
- Python
- FastAPI
- Uvicorn
- SUMO
- TraCI
- Q-learning

### Frontend
- React
- Vite
- React Leaflet
- Leaflet
- leaflet.heat
- Recharts

## Reinforcement Learning

The original project brief proposed PPO/DQN-style reinforcement learning.

The current implementation uses Q-learning as a lightweight discrete-action controller for the SUMO traffic-light environment.

The RL agent chooses between traffic-light phases and attempts to reduce waiting time and CO₂ emissions while maintaining traffic flow.

A new action is selected every 10 SUMO seconds.

## Evaluation Methodology

Both the fixed-time baseline and RL controller are evaluated over the same 200-second SUMO simulation horizon.

Metrics are collected using the same methodology for both controllers.

### Waiting Time
Each vehicle's final accumulated SUMO waiting time is recorded and summed.

### CO₂
Vehicle CO₂ emissions are sampled every SUMO second and accumulated across all active vehicles.

### Average Speed
Average speed is calculated across all vehicle-second samples.

This standardized evaluation avoids comparing metrics sampled at different time intervals.

## Current Comparison Results

| Metric | Baseline | RL | Change |
|---|---:|---:|---:|
| Waiting Time | 248.00 s | 147.00 s | -40.73% |
| CO₂ | 974632.73 | 770841.16 | -20.91% |
| Average Speed | 4.9256 m/s | 5.8708 m/s | +19.19% |

## Project Structure

```text
EcoTwin/
├── backend/
│   └── app/
│       ├── api/
│       ├── services/
│       ├── websocket/
│       └── main.py
├── baseline/
├── data/
│   └── results/
├── frontend/
│   └── src/
│       └── components/
├── simulation/
│   ├── rl/
│   │   ├── agents/
│   │   ├── environment/
│   │   ├── evaluation/
│   │   ├── models/
│   │   └── training/
│   └── sumo/
│       ├── config/
│       ├── network/
│       └── routes/
└── docker-compose.yml
```

## Prerequisites

Install:
- Python 3.10+
- Node.js
- npm
- SUMO 1.27.x
- Git

Verify SUMO:

```bash
sumo --version
```

## Python Dependencies

```bash
pip install -r docker/backend/requirements.txt
```

If required for WebSocket testing:

```bash
pip install websockets
```

## Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local` with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Run Baseline Evaluation

```bash
python -m baseline.fixed_time_controller
```

Output:

```text
data/results/baseline_results.json
```

## Run RL Evaluation

```bash
python -m simulation.rl.environment.evaluate_rl
```

Output:

```text
data/results/rl_results.json
```

## Generate Comparison Results

```bash
python -m simulation.rl.evaluation.compare_results
```

Output:

```text
data/results/comparison_results.json
```

## Run Backend

```bash
py -m uvicorn backend.app.main:app --reload
```

Useful endpoints:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/health
http://127.0.0.1:8000/api/results/comparison
ws://127.0.0.1:8000/ws/simulation
```

## Run Frontend

```bash
cd frontend
npm run dev
```

The Vite development server normally runs at:

```text
http://localhost:5173
```

## Frontend Validation

```bash
npm run lint
npm run build
```

## Live Dashboard

The live simulation dashboard displays:
- simulation time
- active vehicle count
- traffic-light phase
- current CO₂
- current average speed
- current waiting time
- moving SUMO vehicle markers
- per-vehicle speed
- per-vehicle CO₂
- per-vehicle waiting time
- live carbon heatmap

SUMO uses a local Cartesian coordinate system. These coordinates are mapped into a display area around the Leaflet map center for visualization.

## API Error Handling

The backend validates the comparison results file and returns structured HTTP errors when:
- the results file does not exist
- the JSON is invalid
- required result fields are missing

## Security

Saved Q-learning state keys are parsed using `ast.literal_eval()` instead of Python `eval()`.

## Docker

Docker files are included for backend/frontend deployment.

```bash
docker compose up --build
```

## Notes

The live WebSocket simulation currently assumes one active SUMO/TraCI simulation connection per backend process.

For a larger multi-user deployment, simulation execution should be separated from WebSocket broadcasting using a dedicated simulation worker or message broker.
