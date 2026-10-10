import { useEffect, useState } from "react";

import ComparisonChart from "./ComparisonChart";
import EmissionsChart from "./EmissionsChart";
import WaitingTimeChart from "./WaitingTimeChart";
import SpeedChart from "./SpeedChart";
import ResultsComparisonTable from "./ResultsComparisonTable";
import RLImpactSection from "./RLImpactSection";
import SimulationDetails from "./SimulationDetails";

import "./ecotwin-visualizations.css";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";


const MAP_CENTER = [
  18.5204,
  73.8567,
];

const SUMO_GRID_SIZE = 300;
const MAP_SPAN = 0.01;


function convertSumoToLatLng(
  x,
  y,
) {
  const normalizedX =
    x / SUMO_GRID_SIZE;

  const normalizedY =
    y / SUMO_GRID_SIZE;

  const latitude =
    MAP_CENTER[0]
    + (normalizedY - 0.5)
    * MAP_SPAN;

  const longitude =
    MAP_CENTER[1]
    + (normalizedX - 0.5)
    * MAP_SPAN;

  return [
    latitude,
    longitude,
  ];
}


function getVehicleColor(co2) {
  if (co2 > 3000) {
    return "red";
  }

  if (co2 > 1500) {
    return "orange";
  }

  return "green";
}


function UrbanMap() {
  const [comparison, setComparison] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState(null);

  const [liveState, setLiveState] =
    useState(null);

  const [wsStatus, setWsStatus] =
    useState("connecting");


  /*
   * Load completed baseline vs RL results.
   */
  useEffect(() => {
    const apiUrl =
      import.meta.env.VITE_API_URL
      || "http://127.0.0.1:8000";

    fetch(
      `${apiUrl}/api/results/comparison`
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Failed to fetch EcoTwin results"
          );
        }

        return response.json();
      })
      .then((data) => {
        setComparison(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);


  /*
   * Connect to the live SUMO simulation stream.
   */
  useEffect(() => {
    const apiUrl =
      import.meta.env.VITE_API_URL
      || "http://127.0.0.1:8000";

    const wsBaseUrl = apiUrl
      .replace(
        "http://",
        "ws://"
      )
      .replace(
        "https://",
        "wss://"
      );

    const socket = new WebSocket(
      `${wsBaseUrl}/ws/simulation`
    );


    socket.onopen = () => {
      setWsStatus(
        "connected"
      );
    };


    socket.onmessage = (
      event
    ) => {
      const data =
        JSON.parse(
          event.data
        );

      if (
        data.type
        === "simulation_complete"
      ) {
        setWsStatus(
          "completed"
        );

        return;
      }

      if (
        data.type
        === "error"
      ) {
        setWsStatus(
          "error"
        );

        console.error(
          "EcoTwin simulation error:",
          data.message
        );

        return;
      }

      setLiveState(
        data
      );
    };


    socket.onerror = () => {
      setWsStatus(
        "error"
      );
    };


    socket.onclose = () => {
      setWsStatus(
        (currentStatus) => {
          if (
            currentStatus
            === "completed"
          ) {
            return "completed";
          }

          if (
            currentStatus
            === "error"
          ) {
            return "error";
          }

          return "disconnected";
        }
      );
    };


    return () => {
      socket.close();
    };
  }, []);


  /*
   * Convert live SUMO vehicle coordinates
   * to positions suitable for the Leaflet map.
   */
  const vehicles =
    liveState?.vehicles?.map(
      (vehicle) => ({
        ...vehicle,

        position:
          convertSumoToLatLng(
            vehicle.x,
            vehicle.y,
          ),

        color:
          getVehicleColor(
            vehicle.co2
          ),
      })
    ) ?? [];


  const simulationStatus = (() => {
    if (
      wsStatus
      === "connected"
    ) {
      return "Simulation Running";
    }

    if (
      wsStatus
      === "completed"
    ) {
      return "Simulation Completed";
    }

    if (
      wsStatus
      === "error"
    ) {
      return "Simulation Error";
    }

    if (
      wsStatus
      === "disconnected"
    ) {
      return "Disconnected";
    }

    return "Connecting...";
  })();


  if (loading) {
    return (
      <p>
        Loading EcoTwin simulation results...
      </p>
    );
  }


  if (error) {
    return (
      <p>
        Error: {error}
      </p>
    );
  }


  return (
    <div className="urban-map">

      {/* ================================
          SIMULATION SUMMARY
      ================================= */}

      <div className="metrics-grid">

        <div className="metric-card">
          <h3>
            Simulation Steps
          </h3>

          <p className="metric-value">
            {
              comparison
                .simulation_steps
            }
          </p>
        </div>


        <div className="metric-card">
          <h3>
            CO₂ Change
          </h3>

          <p className="metric-value">
            {
              comparison
                .percentage_change
                .co2
                .toFixed(2)
            }
            %
          </p>

          <p className="metric-change">
            Baseline:{" "}
            {
              comparison
                .baseline
                .total_co2
                .toFixed(2)
            }

            <br />

            RL:{" "}
            {
              comparison
                .rl
                .total_co2
                .toFixed(2)
            }
          </p>
        </div>


        <div className="metric-card">
          <h3>
            Waiting Time Change
          </h3>

          <p className="metric-value">
            {
              comparison
                .percentage_change
                .waiting_time
                .toFixed(2)
            }
            %
          </p>

          <p className="metric-change">
            Baseline:{" "}
            {
              comparison
                .baseline
                .total_waiting_time
                .toFixed(2)
            }

            <br />

            RL:{" "}
            {
              comparison
                .rl
                .total_waiting_time
                .toFixed(2)
            }
          </p>
        </div>


        <div className="metric-card">
          <h3>
            Average Speed Change
          </h3>

          <p className="metric-value">
            {
              comparison
                .percentage_change
                .average_speed
                .toFixed(2)
            }
            %
          </p>

          <p className="metric-change">
            Baseline:{" "}
            {
              comparison
                .baseline
                .average_speed
                .toFixed(2)
            }

            <br />

            RL:{" "}
            {
              comparison
                .rl
                .average_speed
                .toFixed(2)
            }
          </p>
        </div>

      </div>


      {/* ================================
          URBAN SIMULATION INFORMATION
      ================================= */}

      <div className="urban-info-card">

        <div className="urban-info-header">

          <div>
            <span className="urban-label">
              URBAN SIMULATION
            </span>

            <h2>
              Urban Traffic Simulation
            </h2>

            <p>
              Real-time urban traffic
              and carbon monitoring
            </p>
          </div>


          <div className="simulation-status">
            <span className="status-dot"></span>

            {simulationStatus}
          </div>

        </div>


        <div className="urban-info-grid">

          <div className="urban-info-item">
            <span>
              Controller
            </span>

            <strong>
              Reinforcement Learning
            </strong>
          </div>


          <div className="urban-info-item">
            <span>
              Live Simulation Time
            </span>

            <strong>
              {
                liveState
                  ?.simulation_time
                ?? 0
              }
              {" / "}
              {
                comparison
                  .simulation_steps
              }
            </strong>
          </div>


          <div className="urban-info-item">
            <span>
              Active Vehicles
            </span>

            <strong>
              {vehicles.length}
            </strong>
          </div>


          <div className="urban-info-item">
            <span>
              Traffic Light Phase
            </span>

            <strong>
              {
                liveState
                  ?.traffic_light
                  ?.phase
                ?? "-"
              }
            </strong>
          </div>


          <div className="urban-info-item">
            <span>
              Live CO₂
            </span>

            <strong>
              {
                liveState
                  ?.metrics
                  ?.co2
                  ?.toFixed(2)
                ?? "0.00"
              }
            </strong>
          </div>


          <div className="urban-info-item">
            <span>
              Live Average Speed
            </span>

            <strong>
              {
                liveState
                  ?.metrics
                  ?.average_speed
                  ?.toFixed(2)
                ?? "0.00"
              }
              {" m/s"}
            </strong>
          </div>


          <div className="urban-info-item">
            <span>
              Live Waiting Time
            </span>

            <strong>
              {
                liveState
                  ?.metrics
                  ?.waiting_time
                  ?.toFixed(2)
                ?? "0.00"
              }
              {" s"}
            </strong>
          </div>


          <div className="urban-info-item">
            <span>
              System Status
            </span>

            <strong
              className="operational"
            >
              {
                wsStatus
                === "error"
                  ? "Error"
                  : "Operational"
              }
            </strong>
          </div>

        </div>


        {/* CO₂ LEGEND */}

        <div className="co2-legend">

          <h3>
            Vehicle CO₂ Level
          </h3>

          <div className="co2-legend-items">

            <div className="co2-legend-item">
              <span
                className="legend-dot low"
              ></span>

              <span>
                Low
              </span>
            </div>


            <div className="co2-legend-item">
              <span
                className="legend-dot medium"
              ></span>

              <span>
                Medium
              </span>
            </div>


            <div className="co2-legend-item">
              <span
                className="legend-dot high"
              ></span>

              <span>
                High
              </span>
            </div>

          </div>

        </div>

      </div>


      {/* ================================
          BASELINE VS RL
      ================================= */}

      <div className="urban-chart-card">

        <div className="urban-chart-header">

          <div>
            <span className="urban-label">
              PERFORMANCE COMPARISON
            </span>

            <h2>
              Baseline vs Reinforcement Learning
            </h2>

            <p>
              Comparison of the current simulation results
            </p>
          </div>

        </div>

        <ComparisonChart
          comparison={comparison}
        />

      </div>


      {/* ================================
          PERSON 2 — DETAILED ANALYTICS
      ================================= */}

      <section className="ecotwin-comparison-card">

        <div className="ecotwin-section-heading">

          <span className="ecotwin-eyebrow">
            Detailed Analytics
          </span>

          <h2>
            Controller Performance
          </h2>

          <p>
            Detailed comparison of baseline and
            reinforcement-learning simulation results.
          </p>

        </div>


        <div className="comparison-charts">

          <EmissionsChart
            baseline={
              comparison
                .baseline
                .total_co2
            }
            rl={
              comparison
                .rl
                .total_co2
            }
          />

          <WaitingTimeChart
            baseline={
              comparison
                .baseline
                .total_waiting_time
            }
            rl={
              comparison
                .rl
                .total_waiting_time
            }
          />

          <SpeedChart
            baseline={
              comparison
                .baseline
                .average_speed
            }
            rl={
              comparison
                .rl
                .average_speed
            }
          />

        </div>

      </section>


      <ResultsComparisonTable
        comparison={comparison}
      />


      <RLImpactSection
        percentageChange={
          comparison
            .percentage_change
        }
      />


      <SimulationDetails
        simulationSteps={
          comparison
            .simulation_steps
        }
      />


      {/* ================================
          LIVE MAP
      ================================= */}

      <div className="map-section">

        <h2>
          Live Urban Traffic Simulation
        </h2>

        <MapContainer
          center={MAP_CENTER}
          zoom={15}
          style={{
            height: "500px",
            width: "100%",
          }}
        >

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url={
              "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            }
          />


          {vehicles.map(
            (vehicle) => (
              <CircleMarker
                key={vehicle.id}
                center={
                  vehicle.position
                }
                radius={8}
                pathOptions={{
                  color:
                    vehicle.color,

                  fillColor:
                    vehicle.color,

                  fillOpacity:
                    0.8,
                }}
              >

                <Popup>

                  <strong>
                    {vehicle.id}
                  </strong>

                  <br />

                  Speed:{" "}
                  {
                    vehicle
                      .speed
                      .toFixed(2)
                  }
                  {" m/s"}

                  <br />

                  CO₂:{" "}
                  {
                    vehicle
                      .co2
                      .toFixed(2)
                  }
                  {" mg/s"}

                  <br />

                  Waiting:{" "}
                  {
                    vehicle
                      .waiting_time
                      .toFixed(2)
                  }
                  {" s"}

                  <br />

                  SUMO X:{" "}
                  {
                    vehicle
                      .x
                      .toFixed(2)
                  }

                  <br />

                  SUMO Y:{" "}
                  {
                    vehicle
                      .y
                      .toFixed(2)
                  }

                </Popup>

              </CircleMarker>
            )
          )}

        </MapContainer>

      </div>

    </div>
  );
}


export default UrbanMap;