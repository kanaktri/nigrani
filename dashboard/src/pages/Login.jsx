import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

const DEMO_ACCOUNTS = [
  { role: "admin", email: "admin@dosje.gov.in" },
  { role: "inspector", email: "inspector1@dosje.gov.in" },
  { role: "official", email: "official@dosje.gov.in" },
  { role: "institute_staff", email: "staff@dosje.gov.in" },
];

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!email || !password) {
      setError("Enter your email and password to continue");
      return;
    }
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError("That email and password don't match our records");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="font-display text-3xl text-paper">DoSJE Sentinel</div>
          <p className="mt-1 text-sm text-paper/50">Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="rounded bg-ink-2 p-6">
          <label className="mb-1 block text-xs uppercase tracking-wide text-paper/50">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mb-4 w-full rounded border border-ink-3 bg-ink px-3 py-2 text-paper outline-none focus:border-paper/40"
            placeholder="you@dosje.gov.in"
          />

          <label className="mb-1 block text-xs uppercase tracking-wide text-paper/50">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mb-4 w-full rounded border border-ink-3 bg-ink px-3 py-2 text-paper outline-none focus:border-paper/40"
            placeholder="••••••••"
          />

          {error && <p className="mb-4 text-sm text-signal-red">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded bg-paper py-2 font-medium text-ink transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="mt-6 rounded border border-ink-2 p-4">
          <p className="mb-2 text-xs uppercase tracking-wide text-paper/40">Demo accounts (password: Password123!)</p>
          <ul className="space-y-1 font-mono text-xs text-paper/60">
            {DEMO_ACCOUNTS.map((a) => (
              <li key={a.email} className="flex justify-between">
                <span>{a.role}</span>
                <span>{a.email}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
