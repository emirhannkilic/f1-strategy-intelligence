import { useState } from "react";

const COMPOUNDS = [
  { value: 0, label: "SOFT" },
  { value: 1, label: "MEDIUM" },
  { value: 2, label: "HARD" },
  { value: 3, label: "INTERMEDIATE" },
  { value: 4, label: "WET" },
];

const defaultValues = {
  current_lap: 15,
  total_laps: 57,
  stint_length: 15,
  compound: 1,
  pace_delta_3lap: 0.08,
  pace_delta_5lap: 0.06,
  position: 5,
  gap_ahead: 3.2,
  gap_behind: 1.8,
  pit_stop_count: 0,
  safety_car_active: false,
  track_temp: 42.0,
  rain: false,
};

export default function PitForm({ onSubmit, loading }) {
  const [form, setForm] = useState(defaultValues);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : type === "number" ? parseFloat(value) : parseInt(value),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="pit-form">
      <div className="form-grid">
        <div className="form-group">
          <label>Current Lap</label>
          <input type="number" name="current_lap" value={form.current_lap} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Total Laps</label>
          <input type="number" name="total_laps" value={form.total_laps} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Stint Length</label>
          <input type="number" name="stint_length" value={form.stint_length} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Compound</label>
          <select name="compound" value={form.compound} onChange={handleChange}>
            {COMPOUNDS.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Pace Delta 3 Lap</label>
          <input type="number" step="0.01" name="pace_delta_3lap" value={form.pace_delta_3lap} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Pace Delta 5 Lap</label>
          <input type="number" step="0.01" name="pace_delta_5lap" value={form.pace_delta_5lap} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Position</label>
          <input type="number" name="position" value={form.position} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Gap Ahead (s)</label>
          <input type="number" step="0.1" name="gap_ahead" value={form.gap_ahead} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Gap Behind (s)</label>
          <input type="number" step="0.1" name="gap_behind" value={form.gap_behind} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Pit Stop Count</label>
          <input type="number" name="pit_stop_count" value={form.pit_stop_count} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Track Temp (°C)</label>
          <input type="number" step="0.1" name="track_temp" value={form.track_temp} onChange={handleChange} />
        </div>
        <div className="form-group checkbox-row" style={{gridColumn: "span 2", flexDirection: "row", gap: "2rem", alignItems: "center", justifyContent: "flex-start"}}>
          <label style={{display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer"}}>
            <input type="checkbox" name="safety_car_active" checked={form.safety_car_active} onChange={handleChange} />
            Safety Car Active
          </label>
         <label style={{display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer"}}>
            <input type="checkbox" name="rain" checked={form.rain} onChange={handleChange} />
            Rain
         </label>
        </div>
      </div>

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? "Analyzing..." : "Predict Strategy"}
      </button>
    </form>
  );
}