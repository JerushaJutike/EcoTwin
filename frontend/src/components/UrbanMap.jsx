import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

function UrbanMap() {
  const vehicles = [
    {
      id: 1,
      position: [18.5204, 73.8567],
      color: "blue",
      carbon: 42,
    },
    {
      id: 2,
      position: [18.5225, 73.8585],
      color: "red",
      carbon: 78,
    },
    {
      id: 3,
      position: [18.5185, 73.8545],
      color: "orange",
      carbon: 61,
    },
  ];

  return (
    <div className="urban-map">
      <MapContainer
        center={[18.5204, 73.8567]}
        zoom={14}
        style={{ height: "500px", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {vehicles.map((vehicle) => (
          <CircleMarker
            key={vehicle.id}
            center={vehicle.position}
            radius={10}
            pathOptions={{
              color: vehicle.color,
              fillColor: vehicle.color,
              fillOpacity: 0.8,
            }}
          >
            <Popup>
              <strong>Vehicle {vehicle.id}</strong>
              <br />
              CO₂ Level: {vehicle.carbon}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}

export default UrbanMap;