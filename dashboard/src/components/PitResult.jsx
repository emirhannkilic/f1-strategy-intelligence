export default function PitResult({ result }) {
  const {
    recommend_pit,
    pit_probability,
    window_start,
    window_end,
    sc_opportunity,
    confidence,
  } = result;

  return (
    <div className="pit-result">
      <div className={`recommendation ${recommend_pit ? "pit" : "stay"}`}>
        <span className="rec-label">Recommendation</span>
        <span className="rec-value">
          {recommend_pit ? "PIT NOW" : "STAY OUT"}
        </span>
      </div>

      <div className="metrics">
        <div className="metric">
          <span className="metric-label">Pit Probability</span>
          <span className="metric-value">
            {(pit_probability * 100).toFixed(1)}%
          </span>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${pit_probability * 100}%` }}
            />
          </div>
        </div>

        <div className="metric">
          <span className="metric-label">SC Opportunity</span>
          <span className="metric-value">
            {(sc_opportunity * 100).toFixed(1)}%
          </span>
          <div className="progress-bar">
            <div
              className="progress-fill sc"
              style={{ width: `${sc_opportunity * 100}%` }}
            />
          </div>
        </div>

        {recommend_pit && (
          <div className="metric">
            <span className="metric-label">Pit Window</span>
            <span className="metric-value">
              Lap {window_start} — {window_end}
            </span>
          </div>
        )}

        <div className="metric">
          <span className="metric-label">Confidence</span>
          <span className="metric-value">
            {(confidence * 100).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}