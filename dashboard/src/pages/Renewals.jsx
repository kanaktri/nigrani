import { useEffect, useState } from "react";

import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const STATUS_LABEL_CLASS = {
  pending: "text-signal-amber",
  approved: "text-signal-green",
  rejected: "text-signal-red",
};

export default function Renewals() {
  const { user } = useAuth();
  const [institutes, setInstitutes] = useState([]);
  const [error, setError] = useState("");
  const canAct = user?.role === "official" || user?.role === "admin";

  useEffect(() => {
    load();
  }, []);

  function load() {
    api
      .get("/institutes")
      .then((res) => setInstitutes(res.data))
      .catch(() => setError("Could not load institutes"));
  }

  async function decide(id, decision) {
    try {
      await api.patch(`/institutes/${id}/renewal`, { decision });
      load();
    } catch {
      setError("That decision couldn't be recorded");
    }
  }

  return (
    <div className="h-full overflow-y-auto bg-paper px-8 py-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl">Renewals</h1>
        <p className="mt-1 text-sm text-ink/60">Registration renewal status for every institute.</p>

        {error && <p className="mt-4 text-sm text-signal-red">{error}</p>}

        <ul className="mt-6 divide-y divide-ink/10">
          {institutes.map((inst) => (
            <li key={inst.id} className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium">{inst.name}</p>
                <p className={`text-xs uppercase ${STATUS_LABEL_CLASS[inst.renewal_status] || ""}`}>
                  {inst.renewal_status}
                </p>
              </div>
              {canAct && inst.renewal_status === "pending" && (
                <div className="flex gap-2">
                  <button
                    onClick={() => decide(inst.id, "approved")}
                    className="rounded bg-signal-green px-3 py-1.5 text-xs text-white hover:opacity-90"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => decide(inst.id, "rejected")}
                    className="rounded border border-ink/20 px-3 py-1.5 text-xs hover:bg-ink/5"
                  >
                    Reject
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
