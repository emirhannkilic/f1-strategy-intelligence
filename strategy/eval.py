import torch
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import recall_score, precision_score, classification_report
import pickle
import logging

from model_pytorch import F1StrategyModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
MODELS_DIR = Path("models")

FEATURE_COLS = [
    "current_lap", "total_laps", "stint_length", "compound",
    "pace_delta_3lap", "pace_delta_5lap", "Position",
    "gap_ahead", "gap_behind", "pit_stop_count",
    "safety_car_active", "track_temp", "rain"
]

THRESHOLD = 0.20


def load_model_and_scaler():
    model = F1StrategyModel(input_dim=13)
    model.load_state_dict(torch.load(MODELS_DIR / "best_model.pt"))
    model.eval()

    with open(MODELS_DIR / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    return model, scaler


def predict(model, scaler, df: pd.DataFrame):
    df = df.copy()
    df["gap_behind"] = df["gap_behind"].fillna(df["gap_behind"].median())
    df["safety_car_active"] = df["safety_car_active"].astype(int)
    df["rain"] = df["rain"].astype(int)

    X = scaler.transform(df[FEATURE_COLS].values)
    X_tensor = torch.FloatTensor(X)

    with torch.no_grad():
        pit_prob, _, _ = model(X_tensor)
        probs = torch.sigmoid(pit_prob.squeeze()).numpy()

    df["pit_probability"] = probs
    df["predicted_pit"] = (probs > THRESHOLD).astype(int)
    return df


def evaluate_season(year: int = 2024):
    model, scaler = load_model_and_scaler()
    df = pd.read_csv(PROCESSED_DIR / f"features_{year}.csv")

    df = predict(model, scaler, df)

    recall = recall_score(df["label"], df["predicted_pit"], zero_division=0)
    precision = precision_score(df["label"], df["predicted_pit"], zero_division=0)

    logger.info(f"--- {year} Season Evaluation ---")
    logger.info(f"Recall: {recall:.3f} | Precision: {precision:.3f}")
    logger.info(f"\n{classification_report(df['label'], df['predicted_pit'], zero_division=0)}")

    return df


def backtest_race(df: pd.DataFrame, event_name: str):
    # comparing model pit suggestions vs actual pit stops for a single race
    race = df[df["EventName"] == event_name].copy()

    if race.empty:
        logger.warning(f"Race not found: {event_name}")
        return

    logger.info(f"\n--- Backtest: {event_name} ---")

    for driver in race["Driver"].unique():
        d = race[race["Driver"] == driver].sort_values("current_lap")

        actual_pits = d[d["label"] == 1]["current_lap"].tolist()
        model_pits = d[d["predicted_pit"] == 1]["current_lap"].tolist()

        if actual_pits or model_pits:
            logger.info(
                f"{driver:4s} | Actual pit laps: {actual_pits[:3]} | "
                f"Model suggested: {model_pits[:3]}"
            )


if __name__ == "__main__":
    df = evaluate_season(2024)

    # backtest a specific race
    backtest_race(df, "Bahrain Grand Prix")