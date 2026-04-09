export default function StrategyCompare({ data }) {
    if (!data) return null;
  
    const { actual_pit_windows, model_pit_windows, event_name, driver } = data;
  
    return (
      <div className="strategy-compare">
        <p className="chart-label">{driver} — {event_name}</p>
  
        <div className="compare-grid">
          <div className="compare-col">
            <p className="compare-title">Actual Strategy</p>
            {actual_pit_windows.length === 0 ? (
              <p className="no-data">No pit stops</p>
            ) : (
              actual_pit_windows.map((w, i) => (
                <div key={i} className="window-badge actual">
                  Lap {w.start} — {w.end}
                </div>
              ))
            )}
          </div>
  
          <div className="compare-col">
            <p className="compare-title">Model Suggestion</p>
            {model_pit_windows.length === 0 ? (
              <p className="no-data">No suggestions</p>
            ) : (
              model_pit_windows.map((w, i) => (
                <div key={i} className="window-badge model">
                  Lap {w.start} — {w.end}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    );
  }