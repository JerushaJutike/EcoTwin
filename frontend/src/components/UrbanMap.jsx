import { useEffect, useState } from "react";

import ComparisonChart from "./ComparisonChart";
import ResultsComparisonTable from "./ResultsComparisonTable";
import RLImpactSection from "./RLImpactSection";
import SimulationDetails from "./SimulationDetails";
import SimulationMap from "./SimulationMap";

import "./ecotwin-visualizations.css";

function UrbanMap() {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadComparisonResults() {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/results/comparison",
          {
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to fetch EcoTwin results (${response.status})`
          );
        }

        const data = await response.json();

        setComparison(data);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadComparisonResults();

    return () => {
      controller.abort();
    };
  }, []);

  if (loading) {
    return (
      <div className="ecotwin-data-state">
        <div className="ecotwin-loading-spinner" />

        <p>Loading EcoTwin simulation results...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ecotwin-data-state ecotwin-error-state">
        <h3>Simulation results unavailable</h3>

        <p>{error}</p>

        <span>
          Confirm that the EcoTwin API is running on port 8000.
        </span>
      </div>
    );
  }

  if (!comparison) {
    return (
      <div className="ecotwin-data-state">
        <p>No EcoTwin simulation results available.</p>
      </div>
    );
  }

  return (
    <div className="urban-map">
      {/* Existing dashboard KPI metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Simulation Steps</h3>

          <p className="metric-value">
            {comparison.simulation_steps}
          </p>
        </div>

        <div className="metric-card">
          <h3>CO₂ Change</h3>

          <p className="metric-value">
            {comparison.percentage_change.co2.toFixed(2)}%
          </p>

          <p className="metric-change">
            Baseline: {comparison.baseline.total_co2.toFixed(2)}
            <br />
            RL: {comparison.rl.total_co2.toFixed(2)}
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
            RL: {comparison.rl.total_waiting_time.toFixed(2)}
          </p>
        </div>

        <div className="metric-card">
          <h3>Average Speed Change</h3>

          <p className="metric-value">
            {comparison.percentage_change.average_speed.toFixed(2)}%
          </p>

          <p className="metric-change">
            Baseline: {comparison.baseline.average_speed.toFixed(2)}
            <br />
            RL: {comparison.rl.average_speed.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Analytics charts */}
      <ComparisonChart comparison={comparison} />

      {/* Detailed result comparison */}
      <ResultsComparisonTable
        comparison={comparison}
      />

      {/* RL performance impact */}
      <RLImpactSection
        percentageChange={comparison.percentage_change}
      />

      {/* Simulation configuration */}
      <SimulationDetails
        simulationSteps={comparison.simulation_steps}
      />

      {/* Urban simulation visualization */}
      <SimulationMap />
    </div>
  );
}

export default UrbanMap;