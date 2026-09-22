import L from "leaflet";
import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { Link } from "react-router-dom";

import { api } from "../api/client";

const STATUS_COLOR = { green: "#3E7A55", yellow: "#C68A2B", red: "#C6432B" };

function pinIcon(status) {
  const color = STATUS_COLOR[status] || "#294A61";
  return L.divIcon({
    className: "",
    html: `<div style="width:16px;height:16px;border-radius:50%;background:${color};border:2px solid #F3F0E7;box-shadow:0 0 0 1px ${color}"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
}

export default function MapView() {
  const [institutes, setInstitutes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/institutes").then((res) => {
      setInstitutes(res.data);
      setLoading(false);
    });
  }, []);

  const counts = institutes.reduce(
    (acc, i) => ({ ...acc, [i.status]: (acc[i.status] || 0) + 1 }),
    { green: 0, yellow: 0, red: 0 }
  );

  const center = institutes.length
    ? [institutes[0].latitude, institutes[0].longitude]
    : [26.8467, 80.9462]; // Lucknow default

  return (
    <div className="relative h-full w-full">
      {!loading && (
        <MapContainer center={center} zoom={7} className="h-full w-full" scrollWheelZoom>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {institutes.map((inst) => (
            <Marker key={inst.id} position={[inst.latitude, inst.longitude]} icon={pinIcon(inst.status)}>
              <Popup>
                <div className="font-sans">
                  <p className="font-medium">{inst.name}</p>
                  <p className="text-xs text-ink/60">{inst.type.replace("_", " ")}</p>
                  <p className="mt-1 font-mono text-xs">score: {inst.compliance_score}</p>
                  <Link to={`/alerts?institute=${inst.id}`} className="mt-1 block text-xs underline">
                    View alerts →
                  </Link>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      )}

      <div className="pointer-events-none absolute left-4 top-4 z-[1000] flex gap-2">
        <StatChip label="Compliant" count={counts.green} color="signal-green" />
        <StatChip label="Watch" count={counts.yellow} color="signal-amber" />
        <StatChip label="Flagged" count={counts.red} color="signal-red" />
      </div>
    </div>
  );
}

const CHIP_DOT_CLASS = {
  "signal-green": "bg-signal-green",
  "signal-amber": "bg-signal-amber",
  "signal-red": "bg-signal-red",
};

function StatChip({ label, count, color }) {
  return (
    <div className="rounded border border-ink-2/10 bg-paper/95 px-3 py-2 shadow-sm backdrop-blur">
      <div className="flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full ${CHIP_DOT_CLASS[color]}`} />
        <span className="font-mono text-lg leading-none">{count}</span>
      </div>
      <p className="mt-0.5 text-[11px] text-ink/60">{label}</p>
    </div>
  );
}
