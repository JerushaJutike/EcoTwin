import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

function ComparisonChart({
  title,
  baseline,
  rl,
  comparison,
}) {
  // -----------------------------------------
  // CASE 1: UrbanMap.jsx
  // -----------------------------------------
  if (comparison) {
    const data = [
      {
        name: "Baseline",
        value: Number(comparison.baseline?.average_speed) || 0,
      },
      {
        name: "RL",
        value: Number(comparison.rl?.average_speed) || 0,
      },
    ];

    return (
      <div
        style={{
          width: "100%",
          height: "280px",
          minWidth: 0,
        }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{
              top: 10,
              right: 10,
              left: 5,
              bottom: 10,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="name"
              tick={{
                fontSize: 11,
                fill: "#64748b",
              }}
              axisLine={false}
              tickLine={false}
            />

            <YAxis
              tick={{
                fontSize: 10,
                fill: "#64748b",
              }}
              axisLine={false}
              tickLine={false}
              width={55}
            />

            <Tooltip
              formatter={(value) => [
                Number(value).toFixed(2),
                "Value",
              ]}
              contentStyle={{
                borderRadius: "10px",
                border: "1px solid #e2e8f0",
                boxShadow:
                  "0 6px 20px rgba(15, 23, 42, 0.08)",
                fontSize: "12px",
              }}
            />

            <Legend
              wrapperStyle={{
                fontSize: "11px",
              }}
            />

            <Bar
              dataKey="value"
              name="Value"
              fill="#2563eb"
              radius={[6, 6, 0, 0]}
              barSize={45}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // -----------------------------------------
  // CASE 2: App.jsx Simulation Comparison
  // -----------------------------------------

  const data = [
    {
      name: "Baseline",
      value: Number(baseline) || 0,
    },
    {
      name: "RL",
      value: Number(rl) || 0,
    },
  ];

  const formatValue = (value) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(2)}M`;
    }

    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }

    return Number(value).toFixed(2);
  };

  return (
    <div
      style={{
        width: "100%",
        height: "280px",
        minWidth: 0,
      }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{
            top: 10,
            right: 10,
            left: 5,
            bottom: 10,
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
          />

          <XAxis
            dataKey="name"
            tick={{
              fontSize: 11,
              fill: "#64748b",
            }}
            axisLine={false}
            tickLine={false}
          />

          <YAxis
            tickFormatter={formatValue}
            tick={{
              fontSize: 10,
              fill: "#64748b",
            }}
            axisLine={false}
            tickLine={false}
            width={55}
          />

          <Tooltip
            formatter={(value) => [
              Number(value).toLocaleString(undefined, {
                maximumFractionDigits: 2,
              }),
              title || "Value",
            ]}
            contentStyle={{
              borderRadius: "10px",
              border: "1px solid #e2e8f0",
              boxShadow:
                "0 6px 20px rgba(15, 23, 42, 0.08)",
              fontSize: "12px",
            }}
          />

          <Legend
            wrapperStyle={{
              fontSize: "11px",
            }}
          />

          <Bar
            dataKey="value"
            name={title || "Value"}
            fill="#2563eb"
            radius={[6, 6, 0, 0]}
            barSize={45}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ComparisonChart;