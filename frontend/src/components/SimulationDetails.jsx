function SimulationDetails({ simulationSteps }) {
  const details = [
    {
      label: "Environment",
      value: "SUMO",
    },
    {
      label: "Traffic Controller",
      value: "Reinforcement Learning",
    },
    {
      label: "RL Algorithm",
      value: "Q-Learning",
    },
    {
      label: "Simulation Type",
      value: "Urban Traffic Grid",
    },
    {
      label: "Simulation Steps",
      value: simulationSteps,
    },
    {
      label: "Status",
      value: "Completed",
    },
  ];

  return (
    <section className="ecotwin-simulation-details">
      <div className="ecotwin-section-heading">
        <span className="ecotwin-eyebrow">
          Simulation Configuration
        </span>

        <h2>Simulation Details</h2>

        <p>
          Configuration used to generate the displayed EcoTwin comparison
          results.
        </p>
      </div>

      <div className="ecotwin-details-grid">
        {details.map((detail) => (
          <article
            className="ecotwin-detail-card"
            key={detail.label}
          >
            <span className="ecotwin-detail-label">
              {detail.label}
            </span>

            <strong className="ecotwin-detail-value">
              {detail.value ?? "—"}
            </strong>
          </article>
        ))}
      </div>
    </section>
  );
}

export default SimulationDetails;