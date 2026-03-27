import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INPUT_DIR = Path("data/real")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMPOUND_MAP = {"SOFT": 0, "MEDIUM": 1, "HARD": 2, "INTERMEDIATE": 3, "WET": 4}

def load_season(year: int) -> pd.DataFrame:
    path = INPUT_DIR / f"laps_{year}.csv"
    df = pd.read_csv(path)
    logger.info(f"Loaded {year}: {len(df)} rows")
    return df

# remove pit laps, deleted laps, convert lapTime to seconds
def clean_laps(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["LapTimeSeconds"] = pd.to_timedelta(df["LapTime"]).dt.total_seconds()

    df = df[df["PitInTime"].isna() & df["PitOutTime"].isna()]
    df = df[df["Deleted"].astype(str).str.lower() != "true"]
    df = df[df["LapTimeSeconds"].notna()]
    df = df[df["LapTimeSeconds"] > 60]
    df = df[df["LapTimeSeconds"] < 200]
    df = df[df["Compound"].isin(COMPOUND_MAP.keys())]

    logger.info(f"After cleaning: {len(df)} rows")
    return df

# pace degradation over last 3 and 5 laps per driver per race
def add_pace_deltas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["Year", "RoundNumber", "Driver", "LapNumber"])

    group = ["Year", "RoundNumber", "Driver"]

    df["pace_delta_3lap"] = (
        df.groupby(group)["LapTimeSeconds"]
        .transform(lambda x: x.diff().rolling(3).mean())
    )

    df["pace_delta_5lap"] = (
        df.groupby(group)["LapTimeSeconds"]
        .transform(lambda x: x.diff().rolling(5).mean())
    )

    return df

# gap to car ahead and behind based on cumulative lap times
def add_gap_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["Year", "RoundNumber", "LapNumber", "Position"])
    df = df.reset_index(drop=True)

    df["gap_ahead"] = np.nan
    df["gap_behind"] = np.nan

    for (year, round_num, lap), group in df.groupby(["Year", "RoundNumber", "LapNumber"]):
        sorted_group = group.sort_values("Position")
        gap_ahead = sorted_group["LapTimeSeconds"].diff()
        gap_behind = sorted_group["LapTimeSeconds"].diff(-1).abs()
        df.loc[sorted_group.index, "gap_ahead"] = gap_ahead.values
        df.loc[sorted_group.index, "gap_behind"] = gap_behind.values

    return df

# detect safety car and virtual safety car from TrackStatus
def add_safety_car(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # TrackStatus: 1=clear, 2=yellow, 4=SC, 5=red, 6=VSC
    df["safety_car_active"] = df["TrackStatus"].isin(["4", "6", 4, 6])
    return df

# count pit stops made so far per driver per race
def add_pit_stop_count(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["Year", "RoundNumber", "Driver", "LapNumber"])
    df["pit_stop_count"] = df.groupby(
        ["Year", "RoundNumber", "Driver"]
    )["Stint"].transform(lambda x: (x.diff() > 0).cumsum())
    return df

# add total lap count per race
def add_total_laps(df: pd.DataFrame) -> pd.DataFrame:
    total = df.groupby(["Year", "RoundNumber"])["LapNumber"].transform("max")
    df["total_laps"] = total
    return df

def encode_compound(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["compound_encoded"] = df["Compound"].map(COMPOUND_MAP)
    return df


# label = 1 if the driver pits within the next 3 laps.

def add_outcome_label(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df = df.sort_values(["Year", "RoundNumber", "Driver", "LapNumber"])
    df = df.reset_index(drop=True)
    df["label"] = 0

    for (year, round_num, driver), group in df.groupby(["Year", "RoundNumber", "Driver"]):
        stint_changes = group["Stint"].diff() > 0
        pit_laps_idx = group.index[stint_changes]

        for idx in pit_laps_idx:
            loc = group.index.get_loc(idx)
            start = max(0, loc - 15)
            pre_pit_indices = group.index[start:loc]
            df.loc[pre_pit_indices, "label"] = 1

    return df

# select and rename final feature columns
def build_feature_set(df: pd.DataFrame) -> pd.DataFrame:
    feature_cols = [
        "Year", "RoundNumber", "EventName", "Driver",
        "LapNumber", "total_laps", "Stint",
        "compound_encoded", "TyreLife",
        "pace_delta_3lap", "pace_delta_5lap",
        "Position", "gap_ahead", "gap_behind",
        "pit_stop_count", "safety_car_active",
        "TrackTemp", "Rainfall",
        "label"
    ]

    df = df[feature_cols].copy()
    df = df.rename(columns={
        "LapNumber": "current_lap",
        "Stint": "stint_number",
        "TyreLife": "stint_length",
        "compound_encoded": "compound",
        "TrackTemp": "track_temp",
        "Rainfall": "rain"
    })

    return df

def process_season(year: int) -> pd.DataFrame:
    df = load_season(year)
    df = clean_laps(df)
    df = add_pace_deltas(df)
    df = add_gap_features(df)
    df = add_safety_car(df)
    df = add_pit_stop_count(df)
    df = add_total_laps(df)
    df = encode_compound(df)
    df = add_outcome_label(df)
    df = build_feature_set(df)

    df = df.dropna(subset=["pace_delta_3lap", "pace_delta_5lap", "gap_ahead"])

    output_path = OUTPUT_DIR / f"features_{year}.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Features saved → {output_path} ({len(df)} rows, label=1: {df['label'].sum()})")
    return df


if __name__ == "__main__":
    for year in [2019, 2020, 2021, 2022, 2023, 2024]:
        process_season(year)