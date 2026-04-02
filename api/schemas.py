from pydantic import BaseModel
from typing import Optional


class LapInput(BaseModel):
    current_lap: int
    total_laps: int
    stint_length: int
    compound: int           # 0=SOFT, 1=MEDIUM, 2=HARD, 3=INT, 4=WET
    pace_delta_3lap: float
    pace_delta_5lap: float
    position: int
    gap_ahead: float
    gap_behind: float
    pit_stop_count: int
    safety_car_active: bool
    track_temp: float
    rain: bool


class PitPrediction(BaseModel):
    recommend_pit: bool
    pit_probability: float
    window_start: Optional[int]
    window_end: Optional[int]
    sc_opportunity: float
    confidence: float