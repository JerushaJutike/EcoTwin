import { useEffect } from "react";
import { useMap } from "react-leaflet";

import L from "leaflet";
import "leaflet.heat";


function CarbonHeatLayer({
  vehicles,
}) {
  const map = useMap();

  useEffect(() => {
    if (!vehicles || vehicles.length === 0) {
      return undefined;
    }

    const heatPoints = vehicles.map(
      (vehicle) => {
        const intensity = Math.min(
          Math.max(
            vehicle.co2 / 5000,
            0
          ),
          1
        );

        return [
          vehicle.position[0],
          vehicle.position[1],
          intensity,
        ];
      }
    );

    const heatLayer = L.heatLayer(
      heatPoints,
      {
        radius: 40,
        blur: 30,
        minOpacity: 0.3,
        maxZoom: 18,
        max: 1.0,
        gradient: {
          0.0: "green",
          0.4: "yellow",
          0.7: "orange",
          1.0: "red",
        },
      }
    );

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(
        heatLayer
      );
    };
  }, [
    map,
    vehicles,
  ]);

  return null;
}


export default CarbonHeatLayer;