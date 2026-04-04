import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ReferenceLine,
    ResponsiveContainer,
    Legend,
  } from "recharts";
  
  const COMPOUND_COLORS = {
    0: "#e74c3c",  // SOFT - red
    1: "#f39c12",  // MEDIUM - yellow
    2: "#95a5a6",  // HARD - grey
    3: "#27ae60",  // INTERMEDIATE - green
    4: "#2980b9",  // WET - blue
  };
  
  const COMPOUND_NAMES = {
    0: "SOFT",
    1: "MEDIUM",
    2: "HARD",
    3: "INT",
    4: "WET",
  };
  
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
  
    const d = payload[0]?.payload;
    return (
      <div className="chart-tooltip">
        <p className="tooltip-lap">LAP {label}</p>
        <p>Pit Prob: <strong>{(d.pit_probability * 100).toFixed(1)}%</strong></p>
        <p>Compound: <strong style={{ color: COMPOUND_COLORS[d.compound] }}>{COMPOUND_NAMES[d.compound]}</strong></p>
        <p>Position: <strong>{d.position}</strong></p>
        {d.actual_pit === 1 && <p className="tooltip-pit">PIT WINDOW</p>}
      </div>
    );
  };
  
  export default function LapChart({ laps }) {
    if (!laps || laps.length === 0) return null;
  
    const pitLaps = laps.filter((l) => l.actual_pit === 1).map((l) => l.lap);
  
    return (
      <div className="lap-chart">
        <p className="chart-label">PIT PROBABILITY BY LAP</p>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={laps} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis
              dataKey="lap"
              stroke="#444"
              tick={{ fill: "#666", fontFamily: "DM Mono", fontSize: 11 }}
              label={{ value: "Lap", position: "insideBottomRight", fill: "#444", fontSize: 11 }}
            />
            <YAxis
              domain={[0, 1]}
              stroke="#444"
              tick={{ fill: "#666", fontFamily: "DM Mono", fontSize: 11 }}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            {pitLaps.map((lap) => (
              <ReferenceLine key={lap} x={lap} stroke="#e10600" strokeDasharray="3 3" strokeOpacity={0.4} />
            ))}
            <ReferenceLine y={0.20} stroke="#666" strokeDasharray="4 4" label={{ value: "threshold", fill: "#444", fontSize: 10 }} />
            <Line
              type="monotone"
              dataKey="pit_probability"
              stroke="#e10600"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#e10600" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }