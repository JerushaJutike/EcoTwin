import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function SpeedChart({ baseline, rl }) {
  const data = [
    {
      controller: "Baseline",
      value: baseline,
    },
    {
      controller: "RL Controller",
      value: rl,
    },
  ];

  return (
    <div className="individual-chart">
      <h3>Average Speed</h3>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="controller" />

          <YAxis />

          <Tooltip
            formatter={(value) => [
              Number(value).toFixed(2),
              "Average Speed",
            ]}
          />

          <Bar
            dataKey="value"
            name="Average Speed"
            fill="#7c3aed"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SpeedChart;