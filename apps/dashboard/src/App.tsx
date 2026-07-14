import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import HemaGridMockup from "./components/HemaGridMockup";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Telemetry from "./pages/Telemetry";
import Verification from "./pages/Verification";
import Diagnostics from "./pages/Diagnostics";

/**
 * Main App component containing routing configuration for HemaGrid.
 */
function App() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen w-full" style={{ background: "#0A0D12", fontFamily: "'Inter', sans-serif" }}>
      <Routes>
        {/* Base route redirects to login */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Login page */}
        <Route path="/login" element={<Login onEnter={() => navigate("/dashboard")} />} />

        {/* Main app layout wrapper shell */}
        <Route element={<HemaGridMockup />}>
          <Route path="/dashboard" element={<Home />} />
          <Route path="/telemetry" element={<Telemetry />} />
          <Route path="/verify" element={<Verification />} />
          <Route path="/diagnostics" element={<Diagnostics />} />
        </Route>

        {/* Fallback for undefined paths redirects to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  );
}

export default App;