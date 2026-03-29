import pandas as pd
import numpy as np


def recommend_pit_window(
    current_lap: int,
    total_laps: int,
    pit_probability: float,
    estimated_remaining: int,
    threshold: float = 0.20
) -> dict:

    # recommend a pit window based on model output and degradation estimate
    # returns window_start, window_end and confidence
    
    if pit_probability < threshold:
        return {
            "recommend_pit": False,
            "window_start": None,
            "window_end": None,
            "confidence": pit_probability
        }

    # window starts now and ends based on estimated remaining laps
    window_start = current_lap
    window_end = min(current_lap + estimated_remaining, total_laps - 5)
    window_end = max(window_start + 1, window_end)

    return {
        "recommend_pit": True,
        "window_start": int(window_start),
        "window_end": int(window_end),
        "confidence": round(float(pit_probability), 3)
    }


def apply_pit_windows(df: pd.DataFrame, threshold: float = 0.20) -> pd.DataFrame:
    
    # applying pit window recommendations to a full race dataframe
    # requires pit_probability and estimated_remaining columns

    df = df.copy()
    df["recommend_pit"] = False
    df["window_start"] = None
    df["window_end"] = None

    for idx, row in df.iterrows():
        if "pit_probability" not in df.columns:
            break

        result = recommend_pit_window(
            current_lap=row["current_lap"],
            total_laps=row["total_laps"],
            pit_probability=row["pit_probability"],
            estimated_remaining=int(row.get("estimated_remaining", 5)),
            threshold=threshold
        )

        df.loc[idx, "recommend_pit"] = result["recommend_pit"]
        df.loc[idx, "window_start"] = result["window_start"]
        df.loc[idx, "window_end"] = result["window_end"]

    return df


if __name__ == "__main__":
    # quick test
    result = recommend_pit_window(
        current_lap=15,
        total_laps=57,
        pit_probability=0.75,
        estimated_remaining=8
    )
    print(result)