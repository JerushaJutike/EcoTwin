import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/results/comparison")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch EcoTwin results");
        }
        return response.json();
      })
      .then((data) => {
        setResults(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const formatNumber = (value) => {
    if (value === undefined || value === null) return "--";
    return Number(value).toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
  };

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>EcoTwin</h1>
          <p>Reinforcement Learning for Urban Carbon Dispersal</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Simulation Dashboard
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div>
            <span className="badge">AI + SUMO + RL</span>
            <h2>Urban Traffic & Carbon Intelligence</h2>
            <p>
              Monitor traffic conditions, environmental impact, and
              reinforcement-learning results from the EcoTwin simulation.
            </p>
          </div>

          <div className="hero-icon">🌱</div>
        </section>

        <section className="metrics">
          <div className="metric-card">
            <span>Simulation Steps</span>
            <strong>
              {loading ? "..." : formatNumber(results?.simulation_steps)}
            </strong>
            <small>SUMO simulation duration</small>
          </div>

          <div className="metric-card">
            <span>RL Waiting Time</span>
            <strong>
              {loading
                ? "..."
                : formatNumber(results?.rl?.total_waiting_time)}
            </strong>
            <small>RL controller result</small>
          </div>

          <div className="metric-card">
            <span>RL CO₂</span>
            <strong>
              {loading ? "..." : formatNumber(results?.rl?.total_co2)}
            </strong>
            <small>Simulated emissions</small>
          </div>

          <div className="metric-card">
            <span>RL Average Speed</span>
            <strong>
              {loading ? "..." : formatNumber(results?.rl?.average_speed)}
            </strong>
            <small>Vehicle speed</small>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel map-panel">
            <div className="panel-header">
              <div>
                <h3>Urban Simulation Map</h3>
                <p>Live traffic and carbon visualization</p>
              </div>
              <span className="live-badge">LIVE</span>
            </div>

            <div className="map-placeholder">
              <div className="road horizontal road-1"></div>
              <div className="road horizontal road-2"></div>
              <div className="road vertical road-3"></div>
              <div className="road vertical road-4"></div>

              <div className="intersection intersection-1"></div>
              <div className="intersection intersection-2"></div>
              <div className="intersection intersection-3"></div>
              <div className="intersection intersection-4"></div>

              <div className="vehicle vehicle-1">🚗</div>
              <div className="vehicle vehicle-2">🚙</div>
              <div className="vehicle vehicle-3">🚕</div>

              <div className="map-label">
                <span>🌫️</span>
                Carbon Heatmap
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>RL vs Baseline</h3>
                <p>Current simulation comparison</p>
              </div>
            </div>

            {error ? (
              <div className="error">
                Backend connection failed.
                <br />
                Make sure FastAPI is running on port 8000.
              </div>
            ) : loading ? (
              <div className="loading">Loading results...</div>
            ) : (
              <div className="comparison">
                <div className="comparison-row heading">
                  <span>Metric</span>
                  <span>Baseline</span>
                  <span>RL</span>
                </div>

                <div className="comparison-row">
                  <span>Waiting Time</span>
                  <span>
                    {formatNumber(
                      results?.baseline?.total_waiting_time
                    )}
                  </span>
                  <span>
                    {formatNumber(results?.rl?.total_waiting_time)}
                  </span>
                </div>

                <div className="comparison-row">
                  <span>CO₂</span>
                  <span>
                    {formatNumber(results?.baseline?.total_co2)}
                  </span>
                  <span>
                    {formatNumber(results?.rl?.total_co2)}
                  </span>
                </div>

                <div className="comparison-row">
                  <span>Average Speed</span>
                  <span>
                    {formatNumber(results?.baseline?.average_speed)}
                  </span>
                  <span>
                    {formatNumber(results?.rl?.average_speed)}
                  </span>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>EcoTwin System Pipeline</h3>
              <p>How the platform connects the major components</p>
            </div>
          </div>

          <div className="pipeline">
            <div className="pipeline-item">
              <span>🚦</span>
              <strong>SUMO</strong>
              <small>Traffic Simulation</small>
            </div>

            <div className="arrow">→</div>

            <div className="pipeline-item">
              <span>🧠</span>
              <strong>RL Agent</strong>
              <small>Traffic Control</small>
            </div>

            <div className="arrow">→</div>

            <div className="pipeline-item">
              <span>🌫️</span>
              <strong>Carbon Data</strong>
              <small>CO₂ Monitoring</small>
            </div>

            <div className="arrow">→</div>

            <div className="pipeline-item">
              <span>📊</span>
              <strong>Dashboard</strong>
              <small>Visualization</small>
            </div>
          </div>
        </section>

        <footer>
          <p>
            EcoTwin • Reinforcement Learning for Urban Carbon Dispersal
          </p>
          <p>FastAPI • React • SUMO • Reinforcement Learning</p>
        </footer>
      </main>
    </div>
  );
}

export default App;