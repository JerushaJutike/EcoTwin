import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function WaitingTimeChart({ baseline, rl }) {
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
      <h3>Waiting Time</h3>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="controller" />

          <YAxis />

          <Tooltip
            formatter={(value) => [
              Number(value).toFixed(2),
              "Waiting Time",
            ]}
          />

          <Bar
            dataKey="value"
            name="Waiting Time"
            fill="#16a34a"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default WaitingTimeChart;