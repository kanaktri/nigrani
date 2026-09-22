import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const SEVERITY_BORDER = { red: "border-l-signal-red", yellow: "border-l-signal-amber" };
const SEVERITY_LABEL_CLASS = { red: "text-signal-red", yellow: "text-signal-amber" };

export default function Alerts() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchParams] = useSearchParams();
  const instituteFilter = searchParams.get("institute");

  useEffect(() => {
    load();
  }, []);

  function load() {
    setLoading(true);
    api
      .get("/alerts")
      .then((res) => setAlerts(res.data))
      .catch(() => setError("Could not load the alerts feed"))
      .finally(() => setLoading(false));
  }

  async function act(alertId, action) {
    try {
      await api.patch(`/alerts/${alertId}/action`, { action });
      load();
    } catch {
      setError("That action couldn't be completed");
    }
  }

  const visible = instituteFilter ? alerts.filter((a) => a.institute_id === instituteFilter) : alerts;

  const canAct = user?.role === "official";

  return (
    <div className="h-full overflow-y-auto bg-paper px-8 py-8">
      <div className="mx-auto max-w-4xl">
        <h1 className="font-display text-3xl">Alerts</h1>
        <p className="mt-1 text-sm text-ink/60">
          Every row here was written by a real check — an anomaly score, a missed pickup, a hash mismatch — never a
          manual flag.
        </p>

        {error && <p className="mt-4 text-sm text-signal-red">{error}</p>}

        {loading ? (
          <p className="mt-8 text-sm text-ink/40">Loading…</p>
        ) : visible.length === 0 ? (
          <p className="mt-8 text-sm text-ink/40">No alerts open right now.</p>
        ) : (
          <ul className="mt-6 divide-y divide-ink/10">
            {visible.map((a) => (
              <li
                key={a.id}
                className={`border-l-4 bg-white/40 py-4 pl-4 pr-2 ${SEVERITY_BORDER[a.severity] || "border-l-ink/20"}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-baseline gap-3">
                      <span className={`text-xs font-medium uppercase tracking-wide ${SEVERITY_LABEL_CLASS[a.severity]}`}>
                        {a.severity}
                      </span>
                      <span className="font-medium">{a.type.replace(/_/g, " ")}</span>
                      <span className="rounded bg-ink/5 px-1.5 py-0.5 text-[11px] uppercase text-ink/50">{a.status}</span>
                    </div>
                    {a.detail && <p className="mt-1 max-w-2xl text-sm text-ink/70">{a.detail}</p>}
                    <p className="mt-1 font-mono text-xs text-ink/40">
                      {new Date(a.created_at).toLocaleString()} · institute {a.institute_id.slice(0, 8)}
                    </p>
                  </div>

                  {canAct && a.status === "open" && (
                    <div className="flex shrink-0 gap-2">
                      <button
                        onClick={() => act(a.id, "reviewed")}
                        className="rounded border border-ink/20 px-3 py-1.5 text-xs hover:bg-ink/5"
                      >
                        Mark reviewed
                      </button>
                      <button
                        onClick={() => act(a.id, "escalated")}
                        className="rounded bg-signal-red px-3 py-1.5 text-xs text-white hover:opacity-90"
                      >
                        Escalate
                      </button>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
