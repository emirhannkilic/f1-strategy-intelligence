import { useState } from "react";
import { predictPit } from "../api/client";
import PitForm from "../components/PitForm";
import PitResult from "../components/PitResult";

export default function Dashboard() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await predictPit(formData);
      setResult(data);
    } catch (err) {
      setError("Failed to connect to API. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-inner">
          <span className="header-tag">F1</span>
          <h1>Strategy Intelligence</h1>
          <p>Real-time pit stop recommendations powered by FastF1 telemetry</p>
        </div>
      </header>

      <main className="main">
        <div className="grid">
          <section className="card">
            <h2>Lap Input</h2>
            <PitForm onSubmit={handlePredict} loading={loading} />
          </section>

          <section className="card">
            <h2>Strategy Output</h2>
            {error && <p className="error">{error}</p>}
            {result ? (
              <PitResult result={result} />
            ) : (
              <p className="placeholder">Submit lap data to see recommendations.</p>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}