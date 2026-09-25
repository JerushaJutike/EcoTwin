import UrbanMap from "./components/UrbanMap";

function App() {
  return (
    <div className="ecotwin-dashboard">
      <header className="ecotwin-header">
        <h1>EcoTwin</h1>
        <p>Urban Carbon Dispersal Simulation</p>
      </header>

      <UrbanMap />
    </div>
  );
}

export default App;