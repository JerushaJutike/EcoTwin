import UrbanMap from "./components/UrbanMap";
import ComparisonChart from "./components/ComparisonChart";

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

function App() {
  return (
    <div className="ecotwin-app">
      {/* ================================
          SIDEBAR
      ================================= */}

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">E</div>

          <div>
            <h2>EcoTwin</h2>
            <span>Urban Intelligence</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button
            className="nav-item active"
            onClick={() => scrollToSection("overview")}
          >
            <span>⌂</span>
            Overview
          </button>

          <button
            className="nav-item"
            onClick={() => scrollToSection("simulation")}
          >
            <span>◉</span>
            Simulation
          </button>

          <button
            className="nav-item"
            onClick={() => scrollToSection("analytics")}
          >
            <span>▥</span>
            Analytics
          </button>

          <button
            className="nav-item"
            onClick={() => scrollToSection("urban-map")}
          >
            <span>⌖</span>
            Urban Map
          </button>
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot"></span>
          Simulation system online
        </div>
      </aside>

      {/* ================================
          MAIN CONTENT
      ================================= */}

      <main className="main-content">
        {/* ================================
            HEADER
        ================================= */}

        <header className="top-header" id="overview">
          <div>
            <p className="breadcrumb">Dashboard / Overview</p>
            <h1>Urban Carbon Overview</h1>
          </div>

          <div className="header-status">
            <span className="status-dot"></span>
            Live Simulation
          </div>
        </header>

        {/* ================================
            HERO
        ================================= */}

        <section className="hero-section">
          <div>
            <span className="hero-label">ECOTWIN SIMULATION</span>

            <h2>
              Smarter traffic.
              <br />
              Cleaner cities.
            </h2>

            <p>
              Monitor urban traffic conditions and compare conventional
              traffic control with reinforcement learning.
            </p>
          </div>

          <div className="hero-stat">
            <span>Simulation Steps</span>
            <strong>200</strong>
            <small>Completed</small>
          </div>
        </section>

        {/* ================================
            KPI METRICS
        ================================= */}

        <section className="metrics-grid" aria-label="Simulation metrics">
          <div className="metric-card">
            <h3>CO₂ Reduction</h3>
            <p className="metric-value">94.31%</p>
            <p className="metric-change">
              Reinforcement learning vs baseline
            </p>
          </div>

          <div className="metric-card">
            <h3>Waiting Time Reduction</h3>
            <p className="metric-value">90.34%</p>
            <p className="metric-change">
              Lower traffic waiting time
            </p>
          </div>

          <div className="metric-card">
            <h3>Simulation Speed</h3>
            <p className="metric-value">4.49</p>
            <p className="metric-change">
              Average RL vehicle speed
            </p>
          </div>

          <div className="metric-card">
            <h3>Simulation Steps</h3>
            <p className="metric-value">200</p>
            <p className="metric-change">
              Completed simulation steps
            </p>
          </div>
        </section>

        {/* ================================
            SIMULATION
        ================================= */}

        <section id="simulation" className="chart-section">
          <h2>Simulation Comparison</h2>

          <div className="comparison-charts">
            <div className="individual-chart">
              <h3>Traffic Waiting Time</h3>

              <ComparisonChart
                title="Waiting Time"
                baseline={9902}
                rl={957}
              />
            </div>

            <div className="individual-chart">
              <h3>CO₂ Emissions</h3>

              <ComparisonChart
                title="CO₂ Emissions"
                baseline={974632.73}
                rl={55453.83}
              />
            </div>

            <div className="individual-chart">
              <h3>Average Speed</h3>

              <ComparisonChart
                title="Average Speed"
                baseline={4.93}
                rl={4.49}
              />
            </div>
          </div>
        </section>

        {/* ================================
            ANALYTICS
        ================================= */}

        <section id="analytics" className="chart-section">
          <h2>Urban Analytics</h2>

          <div className="comparison-charts">
            <div className="individual-chart">
              <h3>Baseline Controller</h3>

              <p className="metric-value">9,902</p>

              <p className="metric-change">
                Waiting time
              </p>

              <p className="metric-value">974,632.73</p>

              <p className="metric-change">
                CO₂ emissions
              </p>
            </div>

            <div className="individual-chart">
              <h3>RL Controller</h3>

              <p className="metric-value">957</p>

              <p className="metric-change">
                Waiting time
              </p>

              <p className="metric-value">55,453.83</p>

              <p className="metric-change">
                CO₂ emissions
              </p>
            </div>

            <div className="individual-chart">
              <h3>Improvement</h3>

              <p className="metric-value">94.31%</p>

              <p className="metric-change">
                CO₂ reduction
              </p>

              <p className="metric-value">90.34%</p>

              <p className="metric-change">
                Waiting-time reduction
              </p>
            </div>
          </div>
        </section>

        {/* ================================
            URBAN MAP
        ================================= */}

        <section id="urban-map" className="map-section">
          <h2>Urban Simulation Map</h2>

          <div className="urban-map">
            <UrbanMap />
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;