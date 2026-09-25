import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function ComparisonChart({ comparison }) {
  const charts = [
    {
      title: "CO₂ Emissions",
      unit: "CO₂",
      baseline: comparison.baseline.total_co2,
      rl: comparison.rl.total_co2,
    },
    {
      title: "Waiting Time",
      unit: "Time",
      baseline: comparison.baseline.total_waiting_time,
      rl: comparison.rl.total_waiting_time,
    },
    {
      title: "Average Speed",
      unit: "Speed",
      baseline: comparison.baseline.average_speed,
      rl: comparison.rl.average_speed,
    },
  ];

  return (
    <div className="chart-section">
      <h2>Baseline vs RL Comparison</h2>

      <div className="comparison-charts">
        {charts.map((chart) => {
          const data = [
            {
              name: "Baseline",
              value: chart.baseline,
            },
            {
              name: "RL",
              value: chart.rl,
            },
          ];

          return (
            <div className="individual-chart" key={chart.title}>
              <h3>{chart.title}</h3>

              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="name" />

                  <YAxis />

                  <Tooltip
                    formatter={(value) => value.toFixed(2)}
                  />

                  <Legend />

                  <Bar
                    dataKey="value"
                    name={chart.unit}
                    fill="#2563eb"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ComparisonChart;