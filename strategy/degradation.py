import pandas as pd
import numpy as np
from pathlib import Path


def estimate_degradation_rate(stint_data: pd.DataFrame) -> float:
    
    # estimating pace degradation rate (seconds lost per lap) for a stint
    # using linear regression on lap times within the stint

    if len(stint_data) < 3:
        return 0.0
    laps = stint_data["current_lap"].values
    times = stint_data["pace_delta_3lap"].dropna().values
    if len(times) < 3:
        return 0.0
    coeffs = np.polyfit(range(len(times)), times, 1)
    return float(coeffs[0])

def estimate_remaining_stint(stint_length: int, compound: int, deg_rate: float) -> int:
    
    # estimating how many laps remain before tire performance cliff.
    # based on compound typical limits and current degradation rate.
    # typical max stint lengths per compound (conservative estimates)

    compound_limits = {
        0: 20,   # SOFT
        1: 35,   # MEDIUM
        2: 50,   # HARD
        3: 25,   # INTERMEDIATE
        4: 30,   # WET
    }

    max_stint = compound_limits.get(compound, 30)
    remaining = max_stint - stint_length

    # if degradation is high, reduce remaining estimate

    if deg_rate > 0.1:
        remaining = int(remaining * 0.7)
    elif deg_rate > 0.05:
        remaining = int(remaining * 0.85)

    return max(0, remaining)


def add_degradation_features(df: pd.DataFrame) -> pd.DataFrame:
    
    # adding degradation rate and estimated remaining laps to feature dataframe

    df = df.copy()
    df["deg_rate"] = 0.0
    df["estimated_remaining"] = 0

    for (year, round_num, driver), group in df.groupby(["Year", "RoundNumber", "Driver"]):
        for stint_num in group["stint_number"].unique():
            stint = group[group["stint_number"] == stint_num]
            deg_rate = estimate_degradation_rate(stint)
            compound = stint["compound"].iloc[0]

            df.loc[stint.index, "deg_rate"] = deg_rate
            df.loc[stint.index, "estimated_remaining"] = stint["stint_length"].apply(
                lambda sl: estimate_remaining_stint(int(sl), compound, deg_rate)
            )

    return df


if __name__ == "__main__":
    import pandas as pd
    from pathlib import Path

    df = pd.read_csv(Path("data/processed/features_2023.csv"))
    df = add_degradation_features(df)
    print(df[["Driver", "current_lap", "stint_length", "compound", "deg_rate", "estimated_remaining"]].head(20))