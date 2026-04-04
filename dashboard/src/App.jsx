import Dashboard from "./pages/Dashboard";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import RaceAnalysis from "./pages/RaceAnalysis";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">Strategy Predictor</Link>
        <Link to="/race">Race Analysis</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/race" element={<RaceAnalysis />} />
      </Routes>
    </BrowserRouter>
  );
}