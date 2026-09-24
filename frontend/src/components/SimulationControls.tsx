type SimulationControlsProps = {
  running: boolean;
  controller: string;
  status: string;
};


const API_BASE =
  "http://127.0.0.1:8000";


function SimulationControls({
  running,
  controller,
  status,
}: SimulationControlsProps) {
  async function request(
    path: string,
    method = "POST"
  ) {
    const response = await fetch(
      `${API_BASE}${path}`,
      {
        method,
      }
    );

    if (!response.ok) {
      const body =
        await response.json();

      throw new Error(
        body.detail ??
          "Request failed."
      );
    }

    return response.json();
  }


  async function startSimulation() {
    try {
      await request(
        "/api/simulation/start"
      );
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to start simulation."
      );
    }
  }


  async function stopSimulation() {
    try {
      await request(
        "/api/simulation/stop"
      );
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to stop simulation."
      );
    }
  }


  async function setController(
    value: "ppo" | "fixed_time"
  ) {
    try {
      await request(
        `/api/simulation/controller/${value}`
      );
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to change controller."
      );
    }
  }


  return (
    <section className="simulation-controls">
      <div className="controls-heading">
        <div>
          <h2>
            Simulation Control
          </h2>

          <p>
            Start, stop and switch
            EcoTwin traffic controllers
          </p>
        </div>

        <span
          className={
            running
              ? "simulation-indicator running"
              : "simulation-indicator stopped"
          }
        >
          {status}
        </span>
      </div>


      <div className="control-actions">
        <button
          className="control-button start"
          onClick={
            startSimulation
          }
          disabled={running}
        >
          Start Simulation
        </button>


        <button
          className="control-button stop"
          onClick={
            stopSimulation
          }
          disabled={!running}
        >
          Stop Simulation
        </button>


        <div className="controller-selector">
          <span>
            Controller
          </span>

          <button
            className={
              controller === "ppo"
                ? "controller-button selected"
                : "controller-button"
            }
            disabled={running}
            onClick={() =>
              setController(
                "ppo"
              )
            }
          >
            PPO
          </button>

          <button
            className={
              controller ===
              "fixed_time"
                ? "controller-button selected"
                : "controller-button"
            }
            disabled={running}
            onClick={() =>
              setController(
                "fixed_time"
              )
            }
          >
            Fixed-Time
          </button>
        </div>
      </div>


      {running && (
        <p className="controller-lock-note">
          Stop the simulation before
          changing controller mode.
        </p>
      )}
    </section>
  );
}


export default SimulationControls;