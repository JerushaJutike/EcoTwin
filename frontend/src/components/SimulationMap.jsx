import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  LayersControl,
  ScaleControl,
  ZoomControl,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

const DEFAULT_VEHICLES = [
  {
    id: 1,
    position: [18.5204, 73.8567],
    carbon: 42,
    traffic: "Normal",
  },
  {
    id: 2,
    position: [18.5225, 73.8585],
    carbon: 78,
    traffic: "High",
  },
  {
    id: 3,
    position: [18.5185, 73.8545],
    carbon: 61,
    traffic: "Moderate",
  },
];

function getCarbonColor(carbon) {
  if (carbon >= 70) {
    return "#dc2626";
  }

  if (carbon >= 55) {
    return "#f59e0b";
  }

  return "#16a34a";
}

function SimulationMap({
  vehicles = DEFAULT_VEHICLES,
}) {
  return (
    <section className="ecotwin-map-section">
      <div className="ecotwin-map-header">
        <div>
          <span className="ecotwin-eyebrow">
            Urban Simulation
          </span>

          <h2>Traffic & CO₂ Map</h2>

          <p>
            Visualization of simulated traffic activity and carbon indicators
            across the EcoTwin urban environment.
          </p>
        </div>

        <div className="ecotwin-map-status">
          <span className="ecotwin-status-dot" />
          Simulation Complete
        </div>
      </div>

      <div className="ecotwin-map-layout">
        <div className="ecotwin-map-shell">
          <MapContainer
            center={[18.5204, 73.8567]}
            zoom={14}
            zoomControl={false}
            className="ecotwin-leaflet-map"
          >
            <LayersControl position="topright">
              <LayersControl.BaseLayer
                checked
                name="Urban Map"
              >
                <TileLayer
                  attribution="&copy; OpenStreetMap contributors"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
              </LayersControl.BaseLayer>
            </LayersControl>

            <ZoomControl position="bottomright" />

            <ScaleControl
              position="bottomleft"
              imperial={false}
            />

            {vehicles.map((vehicle) => {
              const markerColor = getCarbonColor(
                vehicle.carbon
              );

              return (
                <CircleMarker
                  key={vehicle.id}
                  center={vehicle.position}
                  radius={10}
                  pathOptions={{
                    color: markerColor,
                    fillColor: markerColor,
                    fillOpacity: 0.85,
                    weight: 2,
                  }}
                >
                  <Popup>
                    <div className="ecotwin-vehicle-popup">
                      <strong>
                        Vehicle {vehicle.id}
                      </strong>

                      <span>
                        CO₂ Indicator: {vehicle.carbon}
                      </span>

                      <span>
                        Traffic: {vehicle.traffic}
                      </span>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>

        <aside className="ecotwin-map-legend">
          <h3>CO₂ Indicator</h3>

          <div className="ecotwin-legend-item">
            <span className="ecotwin-legend-dot ecotwin-legend-low" />

            <div>
              <strong>Low</strong>
              <span>Below 55</span>
            </div>
          </div>

          <div className="ecotwin-legend-item">
            <span className="ecotwin-legend-dot ecotwin-legend-medium" />

            <div>
              <strong>Moderate</strong>
              <span>55 – 69</span>
            </div>
          </div>

          <div className="ecotwin-legend-item">
            <span className="ecotwin-legend-dot ecotwin-legend-high" />

            <div>
              <strong>High</strong>
              <span>70 and above</span>
            </div>
          </div>

          <div className="ecotwin-map-info">
            <span>Environment</span>
            <strong>SUMO</strong>
          </div>

          <div className="ecotwin-map-info">
            <span>Controller</span>
            <strong>Q-Learning RL</strong>
          </div>

          <p className="ecotwin-map-note">
            Vehicle markers are visualization indicators. Baseline and RL
            performance metrics are loaded from the EcoTwin simulation API.
          </p>
        </aside>
      </div>
    </section>
  );
}

export default SimulationMap;