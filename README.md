# F1 Strategy Intelligence System

Demo

A machine learning system that analyzes real F1 telemetry data via the FastF1 API
and recommends optimal pit stop windows using a PyTorch multi-output model.

---

## Status

**All sprints complete** — live demo available

- [x] **Sprint 1** - Data pipeline + EDA 
- [x] **Sprint 2**  - PyTorch model + backtest
- [x] **Sprint 3**  - FastAPI + React dashboard
- [x] **Sprint 4**  - Deploy + documentation

## Live Demo

- **Dashboard**: [https://f1-strategy-intelligence.vercel.app](https://f1-strategy-intelligence.vercel.app)
- **API**: [https://f1-strategy-intelligence-production.up.railway.app/docs](https://f1-strategy-intelligence-production.up.railway.app/docs)

## Model Performance

Trained on 2019–2023 seasons, evaluated on 2024 season (held-out test set).


| Metric         | Result                                         |
| -------------- | ---------------------------------------------- |
| Test Recall    | 0.965                                          |
| Test Precision | 0.505                                          |
| Training Data  | ~76.000 laps (6 seasons)                       |
| Architecture   | PyTorch multi-output, shared encoder + 3 heads |


> High recall is prioritized — the model is designed to avoid missing pit windows
> rather than minimizing false positives.

## Project Structure

```

f1-strategy-intelligence/
├── assets/           # Demo gif
├── api/              # FastAPI backend
├── dashboard/        # React frontend
├── data/
│   ├── real/         # Raw race data (gitignored)
│   └── processed/    # Feature CSVs 
├── models/           # Saved PyTorch checkpoints
├── notebooks/        # EDA and experiments
├── real_data/        # FastF1 data pipeline
└── strategy/         # ML model + strategy engine

```

---

## This project is a continuation of

[F1 Pit Stop Predictor](https://github.com/emirhannkilic/pitstop-predictor) — V1 used a simulation-based dataset and a NumPy neural network. This V2 moves to real telemetry
data and a production-ready stack.

---

**Built by Emirhan Kılıç — Computer Engineering, 3rd year**