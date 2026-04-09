import { useState, useEffect } from "react";
import axios from "axios";
import LapChart from "../components/LapChart";
import StrategyCompare from "../components/StrategyCompare";

const API_BASE = "http://127.0.0.1:8000";

const SEASONS = [2019, 2020, 2021, 2022, 2023, 2024];

export default function RaceAnalysis() {
  const [year, setYear] = useState(2024);
  const [round, setRound] = useState(1);
  const [raceInfo, setRaceInfo] = useState(null);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [laps, setLaps] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [compareData, setCompareData] = useState(null);

  const fetchRace = async () => {
    setLoading(true);
    setError(null);
    setLaps(null);
    setSelectedDriver(null);
    try {
      const res = await axios.get(`${API_BASE}/race-analysis/${year}/${round}`);
      setRaceInfo(res.data);
    } catch {
      setError("Race not found.");
    } finally {
      setLoading(false);
    }
  };

  const fetchDriverLaps = async (driver) => {
    setSelectedDriver(driver);
    setLaps(null);
    setCompareData(null);
    try {
      const [lapsRes, compareRes] = await Promise.all([
        axios.get(`${API_BASE}/driver-laps/${year}/${round}/${driver}`),
        axios.get(`${API_BASE}/compare-strategies/${year}/${round}/${driver}`)
      ]);
      setLaps(lapsRes.data.laps);
      setCompareData(compareRes.data);
    } catch {
      setError("Failed to load driver data.");
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-inner">
          <span className="header-tag">F1</span>
          <h1>Race Analysis</h1>
          <p>Lap-by-lap pit probability for any driver and race</p>
        </div>
      </header>

      <main className="main">
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <h2>Select Race</h2>
          <div className="form-grid" style={{ gridTemplateColumns: "1fr 1fr auto" }}>
            <div className="form-group">
              <label>Season</label>
              <select value={year} onChange={(e) => setYear(parseInt(e.target.value))}>
                {SEASONS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Round</label>
              <input
                type="number"
                min={1}
                max={24}
                value={round}
                onChange={(e) => setRound(parseInt(e.target.value))}
              />
            </div>
            <div className="form-group" style={{ justifyContent: "flex-end" }}>
              <label>&nbsp;</label>
              <button className="submit-btn" onClick={fetchRace} disabled={loading}>
                {loading ? "Loading..." : "Load Race"}
              </button>
            </div>
          </div>
        </div>

        {error && <p className="error">{error}</p>}

        {raceInfo && (
          <>
            <div className="card" style={{ marginBottom: "1.5rem" }}>
              <h2>Race Info</h2>
              <p style={{ marginBottom: "1rem" }}>
                <strong>{raceInfo.event_name}</strong> — {raceInfo.year} R{raceInfo.round_number} — {raceInfo.total_laps} laps
              </p>
              <div className="driver-grid">
                {raceInfo.drivers.map((d) => (
                  <button
                    key={d}
                    className={`driver-btn ${selectedDriver === d ? "active" : ""}`}
                    onClick={() => fetchDriverLaps(d)}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {laps && (
              <div className="card">
                <h2>{selectedDriver} — Pit Probability</h2>
                <LapChart laps={laps} />
                <StrategyCompare data={compareData} />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}