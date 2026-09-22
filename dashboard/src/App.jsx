import { Route, Routes } from "react-router-dom";

import Rail from "./components/Rail.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Alerts from "./pages/Alerts.jsx";
import Analytics from "./pages/Analytics.jsx";
import CameraWall from "./pages/CameraWall.jsx";
import Login from "./pages/Login.jsx";
import MapView from "./pages/MapView.jsx";
import Renewals from "./pages/Renewals.jsx";

function Shell({ children }) {
  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Rail />
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Shell>
              <MapView />
            </Shell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <Shell>
              <Alerts />
            </Shell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/cameras"
        element={
          <ProtectedRoute>
            <Shell>
              <CameraWall />
            </Shell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <ProtectedRoute>
            <Shell>
              <Analytics />
            </Shell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/renewals"
        element={
          <ProtectedRoute>
            <Shell>
              <Renewals />
            </Shell>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
