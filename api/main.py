import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import torch
import pickle
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import LapInput, PitPrediction
from strategy.model_pytorch import F1StrategyModel
from strategy.pit_window import recommend_pit_window
from strategy.sc_opportunity import score_sc_opportunity
from strategy.degradation import estimate_remaining_stint

app = FastAPI(
    title="F1 Strategy Intelligence API",
    description="Real-time pit stop strategy recommendations using FastF1 telemetry data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_DIR = Path("models")

model = F1StrategyModel(input_dim=13)
model.load_state_dict(torch.load(MODELS_DIR / "best_model.pt", map_location="cpu"))
model.eval()

with open(MODELS_DIR / "scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

FEATURE_ORDER = [
    "current_lap", "total_laps", "stint_length", "compound",
    "pace_delta_3lap", "pace_delta_5lap", "position",
    "gap_ahead", "gap_behind", "pit_stop_count",
    "safety_car_active", "track_temp", "rain"
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PitPrediction)
def predict(lap: LapInput):
    try:
        features = np.array([[
            lap.current_lap,
            lap.total_laps,
            lap.stint_length,
            lap.compound,
            lap.pace_delta_3lap,
            lap.pace_delta_5lap,
            lap.position,
            lap.gap_ahead,
            lap.gap_behind,
            lap.pit_stop_count,
            int(lap.safety_car_active),
            lap.track_temp,
            int(lap.rain)
        ]])

        features_scaled = scaler.transform(features)
        x = torch.FloatTensor(features_scaled)

        with torch.no_grad():
            pit_logit, _, _ = model(x)
            pit_prob = torch.sigmoid(pit_logit).item()

        estimated_remaining = estimate_remaining_stint(
            stint_length=lap.stint_length,
            compound=lap.compound,
            deg_rate=lap.pace_delta_3lap
        )

        window = recommend_pit_window(
            current_lap=lap.current_lap,
            total_laps=lap.total_laps,
            pit_probability=pit_prob,
            estimated_remaining=estimated_remaining
        )

        sc_score = score_sc_opportunity(
            safety_car_active=lap.safety_car_active,
            gap_ahead=lap.gap_ahead,
            pit_stop_count=lap.pit_stop_count,
            current_lap=lap.current_lap,
            total_laps=lap.total_laps
        )

        return PitPrediction(
            recommend_pit=window["recommend_pit"],
            pit_probability=round(pit_prob, 3),
            window_start=window["window_start"],
            window_end=window["window_end"],
            sc_opportunity=sc_score,
            confidence=window["confidence"] if window["recommend_pit"] else 0.0
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))