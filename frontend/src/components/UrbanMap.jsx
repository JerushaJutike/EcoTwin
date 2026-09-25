import { useEffect, useState } from "react";

import ComparisonChart from "./ComparisonChart";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

function UrbanMap() {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/results/comparison")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch EcoTwin results");
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

  const vehicles = [
    {
      id: 1,
      position: [18.5204, 73.8567],
      color: "blue",
      carbon: 42,
    },
    {
      id: 2,
      position: [18.5225, 73.8585],
      color: "red",
      carbon: 78,
    },
    {
      id: 3,
      position: [18.5185, 73.8545],
      color: "orange",
      carbon: 61,
    },
  ];

  if (loading) {
    return <p>Loading EcoTwin simulation results...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <div className="urban-map">

      {/* Dashboard Metrics */}
      <div className="metrics-grid">

        <div className="metric-card">
          <h3>Simulation Steps</h3>

          <p className="metric-value">
            {comparison.simulation_steps}
          </p>
        </div>

        <div className="metric-card">
          <h3>CO₂ Reduction</h3>

          <p className="metric-value">
            {comparison.percentage_change.co2.toFixed(2)}%
          </p>

          <p className="metric-change">
            Baseline:{" "}
            {comparison.baseline.total_co2.toFixed(2)}
            <br />
            RL:{" "}
            {comparison.rl.total_co2.toFixed(2)}
          </p>
        </div>

        <div className="metric-card">
          <h3>Waiting Time Change</h3>

          <p className="metric-value">
            {comparison.percentage_change.waiting_time.toFixed(2)}%
          </p>

          <p className="metric-change">
            Baseline:{" "}
            {comparison.baseline.total_waiting_time.toFixed(2)}
            <br />
            RL:{" "}
            {comparison.rl.total_waiting_time.toFixed(2)}
          </p>
        </div>

        <div className="metric-card">
          <h3>Average Speed Change</h3>

          <p className="metric-value">
            {comparison.percentage_change.average_speed.toFixed(2)}%
          </p>

          <p className="metric-change">
            Baseline:{" "}
            {comparison.baseline.average_speed.toFixed(2)}
            <br />
            RL:{" "}
            {comparison.rl.average_speed.toFixed(2)}
          </p>
        </div>

      </div>

      {/* Baseline vs RL Chart */}
      <ComparisonChart comparison={comparison} />

      {/* Urban Traffic Map */}
      <div className="map-section">

        <h2>Urban Traffic Simulation</h2>

        <MapContainer
          center={[18.5204, 73.8567]}
          zoom={14}
          style={{
            height: "500px",
            width: "100%",
          }}
        >

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {vehicles.map((vehicle) => (
            <CircleMarker
              key={vehicle.id}
              center={vehicle.position}
              radius={10}
              pathOptions={{
                color: vehicle.color,
                fillColor: vehicle.color,
                fillOpacity: 0.8,
              }}
            >
              <Popup>
                <strong>
                  Vehicle {vehicle.id}
                </strong>

                <br />

                CO₂ Level: {vehicle.carbon}
              </Popup>
            </CircleMarker>
          ))}

        </MapContainer>

      </div>

    </div>
  );
}

export default UrbanMap;