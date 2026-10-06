function ImpactCard({
  label,
  value,
  preferredDirection = "decrease",
  description,
}) {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return null;
  }

  const isDecrease = numericValue < 0;
  const isIncrease = numericValue > 0;

  const symbol = isDecrease ? "↓" : isIncrease ? "↑" : "—";

  const isPositiveImpact =
    preferredDirection === "decrease"
      ? numericValue < 0
      : numericValue > 0;

  return (
    <article
      className={`ecotwin-impact-card ${
        isPositiveImpact
          ? "ecotwin-impact-positive"
          : "ecotwin-impact-neutral"
      }`}
    >
      <span className="ecotwin-impact-label">{label}</span>

      <strong className="ecotwin-impact-value">
        {symbol} {Math.abs(numericValue).toFixed(2)}%
      </strong>

      <span className="ecotwin-impact-description">
        {description}
      </span>
    </article>
  );
}

function RLImpactSection({ percentageChange }) {
  if (!percentageChange) {
    return null;
  }

  return (
    <section className="ecotwin-impact-section">
      <div className="ecotwin-section-heading">
        <span className="ecotwin-eyebrow">Reinforcement Learning</span>

        <h2>RL Controller Impact</h2>

        <p>
          Percentage change relative to the baseline controller from the
          completed EcoTwin simulation.
        </p>
      </div>

      <div className="ecotwin-impact-grid">
        <ImpactCard
          label="CO₂ Emissions"
          value={percentageChange.co2}
          preferredDirection="decrease"
          description="Simulated emissions change"
        />

        <ImpactCard
          label="Waiting Time"
          value={percentageChange.waiting_time}
          preferredDirection="decrease"
          description="Simulated traffic-delay change"
        />

        <ImpactCard
          label="Average Speed"
          value={percentageChange.average_speed}
          preferredDirection="increase"
          description="Simulated mobility change"
        />
      </div>
    </section>
  );
}

export default RLImpactSection;