import { useEffect, useMemo, useState } from "react";
import "./App.css";

type Vehicle = {
  id: string;
  x: number;
  y: number;
  speed_mps: number;
  co2_mg_s: number;
};

type TrafficLight = {
  id: string;
  phase: number;
  state: string;
};

type SimulationSnapshot = {
  running: boolean;
  simulation_time: number;
  active_vehicles: number;
  departed_vehicles: number;
  arrived_vehicles: number;

  controller: string;
  current_action: number;

  decision_count: number;
  action_0_count: number;
  action_1_count: number;

  status: string;
  error: string | null;

  vehicles: Vehicle[];

  traffic_light: TrafficLight;

  total_co2_mg_s: number;
  average_speed_mps: number;
};

const INITIAL_STATE: SimulationSnapshot = {
  running: false,
  simulation_time: 0,
  active_vehicles: 0,
  departed_vehicles: 0,
  arrived_vehicles: 0,

  controller: "ppo",
  current_action: 0,

  decision_count: 0,
  action_0_count: 0,
  action_1_count: 0,

  status: "stopped",
  error: null,

  vehicles: [],

  traffic_light: {
    id: "B1",
    phase: 0,
    state: "",
  },

  total_co2_mg_s: 0,
  average_speed_mps: 0,
};

function App() {
  const [snapshot, setSnapshot] =
    useState<SimulationSnapshot>(INITIAL_STATE);

  const [connected, setConnected] =
    useState(false);

  useEffect(() => {
    const websocket = new WebSocket(
      "ws://127.0.0.1:8000/ws/simulation"
    );

    websocket.onopen = () => {
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      const data: SimulationSnapshot =
        JSON.parse(event.data);

      setSnapshot(data);
    };

    websocket.onerror = () => {
      setConnected(false);
    };

    websocket.onclose = () => {
      setConnected(false);
    };

    return () => {
      websocket.close();
    };
  }, []);

  const maxCoordinate = 420;

  const vehiclePoints = useMemo(() => {
    return snapshot.vehicles.map(
      (vehicle) => ({
        ...vehicle,
        cx:
          (vehicle.x / maxCoordinate) *
          100,
        cy:
          100 -
          (vehicle.y / maxCoordinate) *
            100,
      })
    );
  }, [snapshot.vehicles]);

  const speedKmh =
    snapshot.average_speed_mps * 3.6;

  const trafficDirection =
    snapshot.current_action === 0
      ? "East / West"
      : "North / South";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>EcoTwin</h1>

          <p>
            Reinforcement Learning for Urban
            Carbon Dispersal
          </p>
        </div>

        <div
          className={
            connected
              ? "connection online"
              : "connection offline"
          }
        >
          {connected
            ? "WebSocket Connected"
            : "Disconnected"}
        </div>
      </header>

      <main className="dashboard">
        <section className="metrics-grid">
          <MetricCard
            label="Simulation Time"
            value={`${snapshot.simulation_time.toFixed(
              0
            )} s`}
          />

          <MetricCard
            label="Active Vehicles"
            value={snapshot.active_vehicles}
          />

          <MetricCard
            label="Live CO₂"
            value={`${snapshot.total_co2_mg_s.toFixed(
              0
            )} mg/s`}
          />

          <MetricCard
            label="Average Speed"
            value={`${speedKmh.toFixed(
              1
            )} km/h`}
          />

          <MetricCard
            label="Controller"
            value={snapshot.controller.toUpperCase()}
          />

          <MetricCard
            label="PPO Direction"
            value={trafficDirection}
          />
        </section>

        <section className="content-grid">
          <div className="panel map-panel">
            <div className="panel-heading">
              <div>
                <h2>Live Traffic Map</h2>

                <p>
                  Vehicle positions streamed from
                  SUMO via TraCI
                </p>
              </div>

              <span className="status-badge">
                {snapshot.status}
              </span>
            </div>

            <div className="map-wrapper">
              <svg
                viewBox="0 0 100 100"
                className="traffic-map"
              >
                <GridRoads />

                {vehiclePoints.map(
                  (vehicle) => (
                    <circle
                      key={vehicle.id}
                      cx={vehicle.cx}
                      cy={vehicle.cy}
                      r="0.9"
                      className="vehicle-dot"
                    >
                      <title>
                        {vehicle.id}
                        {"\n"}
                        Speed:{" "}
                        {(
                          vehicle.speed_mps *
                          3.6
                        ).toFixed(1)}
                        {" km/h"}
                        {"\n"}
                        CO2:{" "}
                        {vehicle.co2_mg_s.toFixed(
                          0
                        )}
                        {" mg/s"}
                      </title>
                    </circle>
                  )
                )}
              </svg>
            </div>
          </div>

          <div className="panel control-panel">
            <div className="panel-heading">
              <div>
                <h2>PPO Controller</h2>

                <p>
                  Live B1 traffic-light decisions
                </p>
              </div>
            </div>

            <div className="controller-state">
              <div className="signal-box">
                <span>
                  Intersection
                </span>

                <strong>
                  {
                    snapshot
                      .traffic_light
                      .id
                  }
                </strong>
              </div>

              <div className="signal-box">
                <span>
                  SUMO Phase
                </span>

                <strong>
                  {
                    snapshot
                      .traffic_light
                      .phase
                  }
                </strong>
              </div>

              <div className="signal-box">
                <span>
                  Direction
                </span>

                <strong>
                  {trafficDirection}
                </strong>
              </div>

              <div className="signal-box">
                <span>
                  Decisions
                </span>

                <strong>
                  {
                    snapshot
                      .decision_count
                  }
                </strong>
              </div>
            </div>

            <div className="decision-bars">
              <DecisionBar
                label="Action 0 — E/W"
                count={
                  snapshot.action_0_count
                }
                total={
                  snapshot.decision_count
                }
              />

              <DecisionBar
                label="Action 1 — N/S"
                count={
                  snapshot.action_1_count
                }
                total={
                  snapshot.decision_count
                }
              />
            </div>
          </div>
        </section>

        <section className="metrics-grid secondary">
          <MetricCard
            label="Departed"
            value={
              snapshot.departed_vehicles
            }
          />

          <MetricCard
            label="Arrived"
            value={
              snapshot.arrived_vehicles
            }
          />

          <MetricCard
            label="Traffic Phase"
            value={
              snapshot.traffic_light.phase
            }
          />

          <MetricCard
            label="Simulation"
            value={
              snapshot.running
                ? "Running"
                : snapshot.status
            }
          />
        </section>
      </main>
    </div>
  );
}

type MetricCardProps = {
  label: string;
  value: string | number;
};

function MetricCard({
  label,
  value,
}: MetricCardProps) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

type DecisionBarProps = {
  label: string;
  count: number;
  total: number;
};

function DecisionBar({
  label,
  count,
  total,
}: DecisionBarProps) {
  const percentage =
    total > 0
      ? (count / total) * 100
      : 0;

  return (
    <div className="decision-row">
      <div className="decision-header">
        <span>{label}</span>

        <strong>
          {count}
        </strong>
      </div>

      <div className="decision-track">
        <div
          className="decision-fill"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}

function GridRoads() {
  const coordinates = [
    5,
    50,
    95,
  ];

  return (
    <>
      {coordinates.map((value) => (
        <line
          key={`h-${value}`}
          x1="5"
          x2="95"
          y1={value}
          y2={value}
          className="road"
        />
      ))}

      {coordinates.map((value) => (
        <line
          key={`v-${value}`}
          y1="5"
          y2="95"
          x1={value}
          x2={value}
          className="road"
        />
      ))}

      <circle
        cx="50"
        cy="50"
        r="2"
        className="b1-node"
      />

      <text
        x="53"
        y="48"
        className="b1-label"
      >
        B1
      </text>
    </>
  );
}

export default App;