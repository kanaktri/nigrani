import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

const NAV_ITEMS = [
  { to: "/", label: "Map", icon: MapIcon },
  { to: "/alerts", label: "Alerts", icon: AlertIcon },
  { to: "/cameras", label: "Cameras", icon: CameraIcon },
  { to: "/analytics", label: "Analytics", icon: AnalyticsIcon },
  { to: "/renewals", label: "Renewals", icon: RenewalIcon },
];

export default function Rail() {
  const { user, logout } = useAuth();

  return (
    <nav className="flex h-full w-20 flex-col items-center justify-between bg-ink py-6">
      <div className="flex flex-col items-center gap-8">
        <div className="text-center leading-none">
          <div className="font-display text-2xl text-paper">DS</div>
        </div>
        <div className="flex flex-col gap-2">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 rounded px-2 py-3 text-[11px] transition-colors ${
                  isActive ? "bg-ink-3 text-paper" : "text-paper/50 hover:text-paper/80"
                }`
              }
            >
              <Icon />
              {label}
            </NavLink>
          ))}
        </div>
      </div>

      <div className="flex flex-col items-center gap-3">
        <div className="text-center text-[10px] leading-tight text-paper/40">
          <div className="font-mono uppercase tracking-wide">{user?.role}</div>
        </div>
        <button
          onClick={logout}
          className="text-[11px] text-paper/50 underline decoration-paper/30 underline-offset-2 hover:text-paper/80"
        >
          Sign out
        </button>
      </div>
    </nav>
  );
}

function MapIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M9 20l-6-3V4l6 3 6-3 6 3v13l-6-3-6 3z" strokeLinejoin="round" />
      <path d="M9 7v13M15 4v13" />
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M12 3l9 16H3l9-16z" strokeLinejoin="round" />
      <path d="M12 10v4" strokeLinecap="round" />
      <circle cx="12" cy="17" r="0.5" fill="currentColor" />
    </svg>
  );
}

function CameraIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="7" width="13" height="11" rx="2" strokeLinejoin="round" />
      <path d="M16 10.5l5-3v9l-5-3" strokeLinejoin="round" />
    </svg>
  );
}

function AnalyticsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 20V10M12 20V4M20 20v-7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function RenewalIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 12a8 8 0 0113.66-5.66M20 12a8 8 0 01-13.66 5.66" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M17 4v3h-3M7 20v-3h3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
