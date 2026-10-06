import EmissionsChart from "./EmissionsChart";
import WaitingTimeChart from "./WaitingTimeChart";
import SpeedChart from "./SpeedChart";

function ComparisonChart({ comparison }) {
  return (
    <div className="chart-section">
      <h2>Baseline vs RL Comparison</h2>

      <p className="chart-description">
        Comparison of EcoTwin simulation results under the baseline traffic
        controller and the reinforcement-learning controller.
      </p>

      <div className="comparison-charts">
        <EmissionsChart
          baseline={comparison.baseline.total_co2}
          rl={comparison.rl.total_co2}
        />

        <WaitingTimeChart
          baseline={comparison.baseline.total_waiting_time}
          rl={comparison.rl.total_waiting_time}
        />

        <SpeedChart
          baseline={comparison.baseline.average_speed}
          rl={comparison.rl.average_speed}
        />
      </div>
    </div>
  );
}

export default ComparisonChart;