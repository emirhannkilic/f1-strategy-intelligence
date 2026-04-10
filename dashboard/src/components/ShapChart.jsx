export default function ShapChart({ importance }) {
    if (!importance || importance.length === 0) return null;
  
    const max = Math.max(...importance.map((f) => Math.abs(f.shap_value)));
  
    return (
      <div className="shap-chart">
        <p className="chart-label">WHY THIS PREDICTION?</p>
        <div className="shap-bars">
          {importance.slice(0, 5).map((f) => (
            <div key={f.feature} className="shap-row">
              <span className="shap-name">{f.feature}</span>
              <div className="shap-bar-container">
                <div
                  className={`shap-bar ${f.shap_value >= 0 ? "positive" : "negative"}`}
                  style={{ width: `${(Math.abs(f.shap_value) / max) * 100}%` }}
                />
              </div>
              <span className="shap-value">
                {f.shap_value > 0 ? "+" : ""}{f.shap_value.toFixed(3)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }