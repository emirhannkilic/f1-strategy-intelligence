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

import pandas as pd
from pathlib import Path

import shap

explainer = shap.Explainer(
    lambda x: torch.sigmoid(model(torch.FloatTensor(x))[0]).detach().numpy(),
    shap.maskers.Independent(np.zeros((1, 13)))
)

app = FastAPI(
    title="F1 Strategy Intelligence API",
    description="Real-time pit stop strategy recommendations using FastF1 telemetry data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://f1-strategy-intelligence.vercel.app",
        "http://localhost:5173"
    ],
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

@app.get("/race-analysis/{year}/{round_number}")
def race_analysis(year: int, round_number: int):
    try:

        df = pd.read_csv(Path("data/processed") / f"features_{year}.csv")
        race = df[df["RoundNumber"] == round_number]

        if race.empty:
            raise HTTPException(status_code=404, detail="Race not found")

        # available drivers
        drivers = race["Driver"].unique().tolist()
        event_name = race["EventName"].iloc[0]
        total_laps = int(race["total_laps"].iloc[0])

        return {
            "year": year,
            "round_number": round_number,
            "event_name": event_name,
            "total_laps": total_laps,
            "drivers": drivers
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data for year {year}")


@app.get("/driver-laps/{year}/{round_number}/{driver}")
def driver_laps(year: int, round_number: int, driver: str):
    try:
        import pandas as pd
        from pathlib import Path

        df = pd.read_csv(Path("data/processed") / f"features_{year}.csv")
        race = df[(df["RoundNumber"] == round_number) & (df["Driver"] == driver)]

        if race.empty:
            raise HTTPException(status_code=404, detail="Driver not found")

        # running predictions for all laps

        laps = []
        for _, row in race.iterrows():
            features = np.array([[
                row["current_lap"], row["total_laps"], row["stint_length"],
                row["compound"], row["pace_delta_3lap"], row["pace_delta_5lap"],
                row["Position"], row["gap_ahead"],
                row["gap_behind"] if pd.notna(row["gap_behind"]) else 0.0,
                row["pit_stop_count"], int(row["safety_car_active"]),
                row["track_temp"], int(row["rain"])
            ]])

            features_scaled = scaler.transform(features)
            x = torch.FloatTensor(features_scaled)

            with torch.no_grad():
                pit_logit, _, _ = model(x)
                pit_prob = torch.sigmoid(pit_logit).item()

            laps.append({
                "lap": int(row["current_lap"]),
                "stint_length": int(row["stint_length"]),
                "compound": int(row["compound"]),
                "pit_probability": round(pit_prob, 3),
                "actual_pit": int(row["label"]),
                "position": int(row["Position"]) if pd.notna(row["Position"]) else None,
            })

        return {
            "driver": driver,
            "event_name": race["EventName"].iloc[0],
            "laps": laps
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data for year {year}")

@app.get("/compare-strategies/{year}/{round_number}/{driver}")
def compare_strategies(year: int, round_number: int, driver: str):
    try:
        df = pd.read_csv(Path("data/processed") / f"features_{year}.csv")
        race = df[(df["RoundNumber"] == round_number) & (df["Driver"] == driver)]

        if race.empty:
            raise HTTPException(status_code=404, detail="Driver not found")

        actual_pits = []
        model_pits = []

        for _, row in race.iterrows():
            features = np.array([[
                row["current_lap"], row["total_laps"], row["stint_length"],
                row["compound"], row["pace_delta_3lap"], row["pace_delta_5lap"],
                row["Position"], row["gap_ahead"],
                row["gap_behind"] if pd.notna(row["gap_behind"]) else 0.0,
                row["pit_stop_count"], int(row["safety_car_active"]),
                row["track_temp"], int(row["rain"])
            ]])

            features_scaled = scaler.transform(features)
            x = torch.FloatTensor(features_scaled)

            with torch.no_grad():
                pit_logit, _, _ = model(x)
                pit_prob = torch.sigmoid(pit_logit).item()

            if row["label"] == 1:
                actual_pits.append(int(row["current_lap"]))

            if pit_prob > 0.20:
                model_pits.append(int(row["current_lap"]))

        # deduplicate consecutive laps into pit windows
        def to_windows(laps):
            if not laps:
                return []
            windows = []
            start = laps[0]
            prev = laps[0]
            for lap in laps[1:]:
                if lap > prev + 1:
                    windows.append({"start": start, "end": prev})
                    start = lap
                prev = lap
            windows.append({"start": start, "end": prev})
            return windows

        return {
            "driver": driver,
            "event_name": race["EventName"].iloc[0],
            "actual_pit_windows": to_windows(sorted(set(actual_pits))),
            "model_pit_windows": to_windows(sorted(set(model_pits))),
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data for year {year}")

@app.post("/explain")
def explain(lap: LapInput):
    try:
        features = np.array([[
            lap.current_lap, lap.total_laps, lap.stint_length,
            lap.compound, lap.pace_delta_3lap, lap.pace_delta_5lap,
            lap.position, lap.gap_ahead, lap.gap_behind,
            lap.pit_stop_count, int(lap.safety_car_active),
            lap.track_temp, int(lap.rain)
        ]])

        features_scaled = scaler.transform(features)
        shap_values = explainer(features_scaled)

        feature_names = [
            "current_lap", "total_laps", "stint_length", "compound",
            "pace_delta_3lap", "pace_delta_5lap", "position",
            "gap_ahead", "gap_behind", "pit_stop_count",
            "safety_car_active", "track_temp", "rain"
        ]

        importance = [
            {
                "feature": name,
                "shap_value": round(float(shap_values.values[0][i]), 4)
            }
            for i, name in enumerate(feature_names)
        ]

        importance.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        return {"feature_importance": importance}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))