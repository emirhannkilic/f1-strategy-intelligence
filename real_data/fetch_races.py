import fastf1
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


CACHE_DIR = Path(".fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

OUTPUT_DIR = Path("data/real")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEASONS = [2019, 2020, 2021, 2022, 2023, 2024]


def fetch_race_laps(year: int, round_number: int) -> pd.DataFrame | None:
    try:
        session = fastf1.get_session(year, round_number, "R")
        session.load(laps=True, telemetry=False, weather=True, messages=False)

        laps = session.laps.copy()
        laps["Year"] = year
        laps["RoundNumber"] = round_number
        laps["EventName"] = session.event["EventName"]

        # average weather data to each lap
        if session.weather_data is not None and len(session.weather_data) > 0:
            laps["TrackTemp"] = session.weather_data["TrackTemp"].mean()
            laps["Rainfall"] = session.weather_data["Rainfall"].any()
        else:
            laps["TrackTemp"] = None
            laps["Rainfall"] = False

        logger.info(f"OK {year} R{round_number} ({session.event['EventName']}) — {len(laps)} laps")
        return laps

    except Exception as e:
        logger.warning(f"FAILED {year} R{round_number}: {e}")
        return None


def fetch_season(year: int) -> pd.DataFrame:
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    races = schedule[schedule["EventFormat"] == "conventional"]

    all_laps = []
    for _, event in races.iterrows():
        df = fetch_race_laps(year, int(event["RoundNumber"]))
        if df is not None:
            all_laps.append(df)

    if not all_laps:
        return pd.DataFrame()

    season_df = pd.concat(all_laps, ignore_index=True)
    output_path = OUTPUT_DIR / f"laps_{year}.csv"
    season_df.to_csv(output_path, index=False)
    logger.info(f"Season {year} saved → {output_path} ({len(season_df)} rows)")
    return season_df


if __name__ == "__main__":
    fetch_season(2023)