```markdown
# F1 Strategy Intelligence System

Real Formula 1 telemetry data → Race strategy recommendations

A machine learning system that analyzes real F1 telemetry data via the FastF1 API
and recommends optimal pit stop windows using a PyTorch multi-output model.

---

## Status

In active development — Sprint 1 in progress

- [ ] **Sprint 1** - Data pipeline + EDA 
- [ ] **Sprint 2** - PyTorch model + backtest
- [ ] **Sprint 3** - FastAPI + React dashboard
- [ ] **Sprint 4** - Deploy + documentation 

---

## Project Structure


f1-strategy-intelligence/
├── api/              # FastAPI backend
├── dashboard/        # React frontend
├── data/
│   ├── real/         # Raw race data (gitignored)
│   └── processed/    # Feature CSVs (gitignored)
├── models/           # Saved PyTorch checkpoints (gitignored)
├── notebooks/        # EDA and experiments
├── real_data/        # FastF1 data pipeline
├── strategy/         # ML model + strategy engine
└── tests/            # Unit tests   



---

## This project is a continuation of

[F1 Pit Stop Predictor](https://github.com/emirhannkilic/pitstop-predictor) — V1 used
a simulation-based dataset and a NumPy neural network. This V2 moves to real telemetry
data and a production-ready stack.

---

*Built by Emirhan Kılıç — Computer Engineering, 3rd year*
```