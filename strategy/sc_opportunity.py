import pandas as pd
import numpy as np


def score_sc_opportunity(
    safety_car_active: bool,
    gap_ahead: float,
    pit_stop_count: int,
    current_lap: int,
    total_laps: int
) -> float:
    
    # scoring the opportunity to pit under safety car
    # returns a value between 0 and 1
    # higher score = better time to pit under SC

    if not safety_car_active:
        return 0.0

    score = 0.5  # base score when SC is active

    # pitting under SC is more valuable when gap ahead is large
    if gap_ahead > 5.0:
        score += 0.2
    elif gap_ahead > 2.0:
        score += 0.1

    # early in the race — more laps to recover
    race_progress = current_lap / total_laps
    if race_progress < 0.5:
        score += 0.2
    elif race_progress < 0.7:
        score += 0.1

    if pit_stop_count >= 2:
        score -= 0.2

    return round(min(max(score, 0.0), 1.0), 3)


def add_sc_opportunity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["sc_opportunity"] = df.apply(
        lambda row: score_sc_opportunity(
            safety_car_active=bool(row["safety_car_active"]),
            gap_ahead=float(row["gap_ahead"]) if pd.notna(row["gap_ahead"]) else 0.0,
            pit_stop_count=int(row["pit_stop_count"]),
            current_lap=int(row["current_lap"]),
            total_laps=int(row["total_laps"])
        ),
        axis=1
    )

    return df


if __name__ == "__main__":
    # quick test — SC active scenario
    score = score_sc_opportunity(
        safety_car_active=True,
        gap_ahead=6.0,
        pit_stop_count=0,
        current_lap=20,
        total_laps=57
    )
    print(f"SC opportunity score: {score}")

    # no SC scenario
    score = score_sc_opportunity(
        safety_car_active=False,
        gap_ahead=2.0,
        pit_stop_count=1,
        current_lap=35,
        total_laps=57
    )
    print(f"No SC score: {score}")