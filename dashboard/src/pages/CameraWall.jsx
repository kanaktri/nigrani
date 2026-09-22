import { useEffect, useState } from "react";

import { api } from "../api/client";

// This is connection-health monitoring (is the feed reachable, has it
// pinged recently) - a real, useful signal - not a live video wall.
// Actual video streaming would need a WebRTC/RTSP gateway (documented in
// the README as an integration point), which is a materially different
// and heavier piece of infrastructure than what a camera health check
// needs. Showing a fake video frame here would be the kind of overclaim
// this project has deliberately avoided everywhere else.
const STATUS_STYLE = {
  online: { border: "border-signal-green", dot: "bg-signal-green", label: "Online" },
  stale: { border: "border-signal-amber", dot: "bg-signal-amber", label: "Feed stale" },
  offline: { border: "border-signal-red", dot: "bg-signal-red", label: "Offline" },
};

export default function CameraWall() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/cameras")
      .then((res) => setCameras(res.data))
      .catch(() => setError("Could not load the camera wall"))
      .finally(() => setLoading(false));
  }, []);

  const counts = cameras.reduce((acc, c) => ({ ...acc, [c.status]: (acc[c.status] || 0) + 1 }), {});

  return (
    <div className="h-full overflow-y-auto bg-paper px-8 py-8">
      <div className="mx-auto max-w-5xl">
        <h1 className="font-display text-3xl">CCTV Wall</h1>
        <p className="mt-1 text-sm text-ink/60">
          Connection health across every institute's cameras — a feed going stale or offline right before a scheduled
          visit is itself a signal worth flagging, alongside the anomaly model.
        </p>

        <div className="mt-4 flex gap-4 font-mono text-sm text-ink/70">
          <span>{counts.online || 0} online</span>
          <span>{counts.stale || 0} stale</span>
          <span>{counts.offline || 0} offline</span>
        </div>

        {error && <p className="mt-4 text-sm text-signal-red">{error}</p>}

        {loading ? (
          <p className="mt-8 text-sm text-ink/40">Loading…</p>
        ) : (
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {cameras.map((cam) => {
              const style = STATUS_STYLE[cam.status] || STATUS_STYLE.offline;
              return (
                <div key={cam.id} className={`rounded border-l-4 bg-white/60 p-3 ${style.border}`}>
                  <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 rounded-full ${style.dot}`} />
                    <span className="text-xs uppercase text-ink/50">{style.label}</span>
                  </div>
                  <p className="mt-2 text-sm font-medium">{cam.name}</p>
                  {cam.last_ping_at && (
                    <p className="mt-1 font-mono text-[11px] text-ink/40">
                      last ping {new Date(cam.last_ping_at).toLocaleTimeString()}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
