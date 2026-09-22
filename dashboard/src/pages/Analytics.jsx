import { useEffect, useState } from "react";

import { api } from "../api/client";

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/analytics/compliance-summary")
      .then((res) => setSummary(res.data))
      .catch(() => setError("Could not load analytics"));
  }, []);

  if (error) return <div className="p-8 text-sm text-signal-red">{error}</div>;
  if (!summary) return <div className="p-8 text-sm text-ink/40">Loading…</div>;

  const total = summary.total_institutes || 1; // avoid divide-by-zero on the bar widths below

  return (
    <div className="h-full overflow-y-auto bg-paper px-8 py-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl">Analytics</h1>
        <p className="mt-1 text-sm text-ink/60">
          The aggregate view a single institute's score can't show — how the whole portfolio is trending.
        </p>

        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard label="Institutes" value={summary.total_institutes} />
          <StatCard label="Avg. score" value={summary.average_compliance_score} mono />
          <StatCard label="Open alerts" value={summary.open_alerts_count} />
          <StatCard label="Red alerts" value={summary.red_alerts_count} accent="text-signal-red" />
        </div>

        <div className="mt-8">
          <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-ink/50">Status distribution</h2>
          <div className="flex h-6 overflow-hidden rounded border border-ink/10">
            <Bar count={summary.green_count} total={total} className="bg-signal-green" />
            <Bar count={summary.yellow_count} total={total} className="bg-signal-amber" />
            <Bar count={summary.red_count} total={total} className="bg-signal-red" />
          </div>
          <div className="mt-2 flex gap-4 font-mono text-xs text-ink/60">
            <span>{summary.green_count} compliant</span>
            <span>{summary.yellow_count} watch</span>
            <span>{summary.red_count} flagged</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, mono, accent }) {
  return (
    <div className="rounded border border-ink/10 bg-white/60 p-4">
      <p className={`text-2xl ${mono ? "font-mono" : "font-display"} ${accent || ""}`}>{value}</p>
      <p className="mt-1 text-[11px] uppercase text-ink/50">{label}</p>
    </div>
  );
}

function Bar({ count, total, className }) {
  const pct = (count / total) * 100;
  if (pct <= 0) return null;
  return <div className={className} style={{ width: `${pct}%` }} />;
}
