import SimulationControls from "./components/SimulationControls";

import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

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


type ControllerMetrics = {
  average_waiting_time_seconds: number;
  total_co2_g: number;
  average_speed_kmh: number;
  completed_trips: number;
  simulation_time_seconds: number;
};


type ComparisonData = {
  baseline: ControllerMetrics;

  ppo: ControllerMetrics;

  improvements: {
    waiting_time_reduction_percent: number;
    co2_reduction_percent: number;
    average_speed_change_percent: number;
    simulation_duration_reduction_percent: number;
  };
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
    useState<SimulationSnapshot>(
      INITIAL_STATE
    );

  const [connected, setConnected] =
    useState(false);

  const [
    comparison,
    setComparison,
  ] =
    useState<ComparisonData | null>(
      null
    );

  const [
    comparisonError,
    setComparisonError,
  ] = useState<string | null>(
    null
  );


  /*
   * Live SUMO WebSocket
   */
  useEffect(() => {
    const websocket =
      new WebSocket(
        "ws://127.0.0.1:8000/ws/simulation"
      );

    websocket.onopen = () => {
      setConnected(true);
    };

    websocket.onmessage = (
      event
    ) => {
      const data: SimulationSnapshot =
        JSON.parse(
          event.data
        );

      setSnapshot(
        data
      );
    };

    websocket.onerror = () => {
      setConnected(
        false
      );
    };

    websocket.onclose = () => {
      setConnected(
        false
      );
    };

    return () => {
      websocket.close();
    };
  }, []);


  /*
   * Historical baseline vs PPO results
   */
  useEffect(() => {
    async function loadComparison() {
      try {
        const response =
          await fetch(
            "http://127.0.0.1:8000/api/results/comparison"
          );

        if (!response.ok) {
          throw new Error(
            `HTTP ${response.status}`
          );
        }

        const data: ComparisonData =
          await response.json();

        setComparison(
          data
        );

        setComparisonError(
          null
        );
      } catch (error) {
        setComparisonError(
          error instanceof Error
            ? error.message
            : "Unable to load comparison data."
        );
      }
    }

    loadComparison();
  }, []);


  /*
   * SUMO coordinate conversion
   */
  const maxCoordinate = 420;

  const vehiclePoints =
    useMemo(() => {
      return snapshot.vehicles.map(
        (vehicle) => {
          const rawX =
            (
              vehicle.x /
              maxCoordinate
            ) * 100;

          const rawY =
            100 -
            (
              vehicle.y /
              maxCoordinate
            ) *
              100;

          return {
            ...vehicle,

            cx: Math.min(
              100,
              Math.max(
                0,
                rawX
              )
            ),

            cy: Math.min(
              100,
              Math.max(
                0,
                rawY
              )
            ),
          };
        }
      );
    }, [
      snapshot.vehicles,
    ]);


  /*
   * Improvement chart
   */
  const improvementChartData =
    useMemo(() => {
      if (!comparison) {
        return [];
      }

      return [
        {
          metric:
            "Waiting time",
          improvement:
            comparison
              .improvements
              .waiting_time_reduction_percent,
        },
        {
          metric:
            "CO₂",
          improvement:
            comparison
              .improvements
              .co2_reduction_percent,
        },
        {
          metric:
            "Speed",
          improvement:
            comparison
              .improvements
              .average_speed_change_percent,
        },
      ];
    }, [comparison]);


  const speedKmh =
    snapshot.average_speed_mps *
    3.6;


  const trafficDirection =
    snapshot.current_action === 0
      ? "East / West"
      : "North / South";


  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>
            EcoTwin
          </h1>

          <p>
            Reinforcement Learning
            for Urban Carbon
            Dispersal
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
            <SimulationControls
              running={snapshot.running}
              controller={snapshot.controller}
              status={snapshot.status}
/>
        {/* LIVE METRICS */}

        <section className="metrics-grid">
          <MetricCard
            label="Simulation Time"
            value={`${snapshot.simulation_time.toFixed(
              0
            )} s`}
          />

          <MetricCard
            label="Active Vehicles"
            value={
              snapshot.active_vehicles
            }
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
            value={
              snapshot.controller.toUpperCase()
            }
          />

          <MetricCard
            label="PPO Direction"
            value={
              trafficDirection
            }
          />
        </section>


        {/* LIVE SIMULATION */}

        <section className="content-grid">

          <div className="panel map-panel">
            <div className="panel-heading">
              <div>
                <h2>
                  Live Traffic &
                  Carbon Map
                </h2>

                <p>
                  Vehicle movement and
                  live CO₂ emission
                  intensity
                </p>
              </div>

              <span className="status-badge">
                {
                  snapshot.status
                }
              </span>
            </div>


            <div className="map-legend">
              <span>
                <i className="legend-vehicle" />
                Vehicle
              </span>

              <span>
                <i className="legend-carbon-low" />
                Low CO₂
              </span>

              <span>
                <i className="legend-carbon-high" />
                High CO₂
              </span>
            </div>


            <div className="map-wrapper">
              <svg
                viewBox="0 0 100 100"
                className="traffic-map"
              >

                <defs>
                  <radialGradient
                    id="carbonGlow"
                  >
                    <stop
                      offset="0%"
                      stopColor="#ff8c42"
                      stopOpacity="0.75"
                    />

                    <stop
                      offset="45%"
                      stopColor="#ff5c35"
                      stopOpacity="0.35"
                    />

                    <stop
                      offset="100%"
                      stopColor="#ff5c35"
                      stopOpacity="0"
                    />
                  </radialGradient>
                </defs>


                <GridRoads />


                {/* CO2 HEAT LAYER */}

                {vehiclePoints.map(
                  (vehicle) => {
                    const intensity =
                      Math.min(
                        vehicle.co2_mg_s /
                          6000,
                        1
                      );

                    const radius =
                      2 +
                      intensity *
                        5;

                    return (
                      <circle
                        key={
                          `carbon-${vehicle.id}`
                        }
                        cx={
                          vehicle.cx
                        }
                        cy={
                          vehicle.cy
                        }
                        r={
                          radius
                        }
                        fill="url(#carbonGlow)"
                        opacity={
                          0.25 +
                          intensity *
                            0.65
                        }
                        className="carbon-cloud"
                      />
                    );
                  }
                )}


                {/* VEHICLES */}

                {vehiclePoints.map(
                  (vehicle) => (
                    <circle
                      key={
                        vehicle.id
                      }
                      cx={
                        vehicle.cx
                      }
                      cy={
                        vehicle.cy
                      }
                      r="0.85"
                      className="vehicle-dot"
                    >
                      <title>
                        {
                          vehicle.id
                        }
                        {"\n"}

                        Speed:{" "}
                        {(
                          vehicle.speed_mps *
                          3.6
                        ).toFixed(
                          1
                        )}
                        {" km/h"}

                        {"\n"}

                        CO₂:{" "}
                        {
                          vehicle.co2_mg_s.toFixed(
                            0
                          )
                        }
                        {" mg/s"}
                      </title>
                    </circle>
                  )
                )}

              </svg>
            </div>


            <div className="heatmap-note">
              Carbon layer represents
              spatial vehicle-emission
              intensity from SUMO
              (mg/s), not measured
              atmospheric CO₂
              concentration.
            </div>
          </div>


          {/* PPO CONTROLLER */}

          <div className="panel control-panel">

            <div className="panel-heading">
              <div>
                <h2>
                  PPO Controller
                </h2>

                <p>
                  Live B1
                  traffic-light
                  decisions
                </p>
              </div>
            </div>


            <div className="controller-state">

              <SignalBox
                label="Intersection"
                value={
                  snapshot
                    .traffic_light
                    .id
                }
              />

              <SignalBox
                label="SUMO Phase"
                value={
                  snapshot
                    .traffic_light
                    .phase
                }
              />

              <SignalBox
                label="Direction"
                value={
                  trafficDirection
                }
              />

              <SignalBox
                label="Decisions"
                value={
                  snapshot
                    .decision_count
                }
              />

            </div>


            <div className="decision-bars">

              <DecisionBar
                label="Action 0 — E/W"
                count={
                  snapshot
                    .action_0_count
                }
                total={
                  snapshot
                    .decision_count
                }
              />

              <DecisionBar
                label="Action 1 — N/S"
                count={
                  snapshot
                    .action_1_count
                }
                total={
                  snapshot
                    .decision_count
                }
              />

            </div>


            <div className="signal-state">
              <span>
                Raw SUMO signal
              </span>

              <code>
                {
                  snapshot
                    .traffic_light
                    .state ||
                  "Waiting for simulation..."
                }
              </code>
            </div>

          </div>

        </section>


        {/* BASELINE VS PPO */}

        <section className="comparison-section">

          <div className="section-heading">
            <div>
              <h2>
                Fixed-Time vs PPO
              </h2>

              <p>
                Performance measured
                on the original EcoTwin
                evaluation scenario
              </p>
            </div>
          </div>


          {comparisonError && (
            <div className="error-box">
              Unable to load
              comparison metrics:{" "}
              {comparisonError}
            </div>
          )}


          {comparison && (
            <>
              <div className="comparison-grid">

                <ComparisonCard
                  title="Average Waiting Time"
                  baseline={
                    comparison
                      .baseline
                      .average_waiting_time_seconds
                  }
                  ppo={
                    comparison
                      .ppo
                      .average_waiting_time_seconds
                  }
                  unit="s"
                  improvement={
                    comparison
                      .improvements
                      .waiting_time_reduction_percent
                  }
                  improvementLabel="reduction"
                  lowerIsBetter
                />


                <ComparisonCard
                  title="Total CO₂"
                  baseline={
                    comparison
                      .baseline
                      .total_co2_g
                  }
                  ppo={
                    comparison
                      .ppo
                      .total_co2_g
                  }
                  unit="g"
                  improvement={
                    comparison
                      .improvements
                      .co2_reduction_percent
                  }
                  improvementLabel="reduction"
                  lowerIsBetter
                />


                <ComparisonCard
                  title="Average Speed"
                  baseline={
                    comparison
                      .baseline
                      .average_speed_kmh
                  }
                  ppo={
                    comparison
                      .ppo
                      .average_speed_kmh
                  }
                  unit="km/h"
                  improvement={
                    comparison
                      .improvements
                      .average_speed_change_percent
                  }
                  improvementLabel="increase"
                />

              </div>


              <div className="panel improvement-panel">

                <div className="panel-heading">
                  <div>
                    <h2>
                      PPO Improvement
                    </h2>

                    <p>
                      Percentage change
                      relative to the
                      fixed-time controller
                    </p>
                  </div>
                </div>


                <div className="chart-wrapper">
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <BarChart
                      data={
                        improvementChartData
                      }
                      margin={{
                        top: 10,
                        right: 20,
                        bottom: 10,
                        left: 0,
                      }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="rgba(255,255,255,0.08)"
                      />

                      <XAxis
                        dataKey="metric"
                        stroke="#8fa9a0"
                      />

                      <YAxis
                        stroke="#8fa9a0"
                        unit="%"
                      />

                      <Tooltip
                        formatter={(
                          value
                        ) => [
                          `${Number(
                            value
                          ).toFixed(
                            2
                          )}%`,
                          "Improvement",
                        ]}
                        contentStyle={{
                          background:
                            "#0d1d19",
                          border:
                            "1px solid rgba(255,255,255,0.1)",
                          borderRadius:
                            "8px",
                        }}
                      />

                      <Bar
                        dataKey="improvement"
                        fill="#5eead4"
                        radius={[
                          6,
                          6,
                          0,
                          0,
                        ]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

              </div>
            </>
          )}

        </section>


        {/* SECONDARY METRICS */}

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
              snapshot
                .traffic_light
                .phase
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
  value:
    | string
    | number;
};


function MetricCard({
  label,
  value,
}: MetricCardProps) {
  return (
    <div className="metric-card">
      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}


type SignalBoxProps = {
  label: string;
  value:
    | string
    | number;
};


function SignalBox({
  label,
  value,
}: SignalBoxProps) {
  return (
    <div className="signal-box">
      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
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
      ? (
          count /
          total
        ) *
        100
      : 0;

  return (
    <div className="decision-row">

      <div className="decision-header">
        <span>
          {label}
        </span>

        <strong>
          {count}
        </strong>
      </div>

      <div className="decision-track">
        <div
          className="decision-fill"
          style={{
            width:
              `${percentage}%`,
          }}
        />
      </div>

    </div>
  );
}


type ComparisonCardProps = {
  title: string;

  baseline: number;

  ppo: number;

  unit: string;

  improvement: number;

  improvementLabel: string;

  lowerIsBetter?: boolean;
};


function ComparisonCard({
  title,
  baseline,
  ppo,
  unit,
  improvement,
  improvementLabel,
}: ComparisonCardProps) {
  const maxValue =
    Math.max(
      baseline,
      ppo
    );

  const baselineWidth =
    maxValue > 0
      ? (
          baseline /
          maxValue
        ) *
        100
      : 0;

  const ppoWidth =
    maxValue > 0
      ? (
          ppo /
          maxValue
        ) *
        100
      : 0;

  return (
    <div className="comparison-card">

      <div className="comparison-title">
        <span>
          {title}
        </span>

        <strong>
          {improvement.toFixed(
            2
          )}
          %{" "}
          {improvementLabel}
        </strong>
      </div>


      <ComparisonBar
        label="Fixed-time"
        value={
          baseline
        }
        unit={
          unit
        }
        width={
          baselineWidth
        }
        variant="baseline"
      />


      <ComparisonBar
        label="PPO"
        value={
          ppo
        }
        unit={
          unit
        }
        width={
          ppoWidth
        }
        variant="ppo"
      />

    </div>
  );
}


type ComparisonBarProps = {
  label: string;

  value: number;

  unit: string;

  width: number;

  variant:
    | "baseline"
    | "ppo";
};


function ComparisonBar({
  label,
  value,
  unit,
  width,
  variant,
}: ComparisonBarProps) {
  return (
    <div className="comparison-row">

      <div className="comparison-row-header">

        <span>
          {label}
        </span>

        <strong>
          {value.toLocaleString(
            undefined,
            {
              maximumFractionDigits:
                3,
            }
          )}
          {" "}
          {unit}
        </strong>

      </div>


      <div className="comparison-track">

        <div
          className={
            `comparison-fill ${variant}`
          }
          style={{
            width:
              `${width}%`,
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
      {coordinates.map(
        (
          value
        ) => (
          <line
            key={
              `h-${value}`
            }
            x1="5"
            x2="95"
            y1={
              value
            }
            y2={
              value
            }
            className="road"
          />
        )
      )}


      {coordinates.map(
        (
          value
        ) => (
          <line
            key={
              `v-${value}`
            }
            y1="5"
            y2="95"
            x1={
              value
            }
            x2={
              value
            }
            className="road"
          />
        )
      )}


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