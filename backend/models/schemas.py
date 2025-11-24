from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TelemetryPoint(BaseModel):
    timestamp: float
    speed: float
    gear: int
    rpm: float
    throttle: float
    brake_front: float
    brake_rear: float
    acc_x: float
    acc_y: float
    steering_angle: float
    lat: float
    lon: float
    lap_distance: float

class LapTime(BaseModel):
    lap_number: int
    time: float
    timestamp: datetime

class SectionAnalysis(BaseModel):
    section: str
    time: float
    speed_avg: float
    speed_max: float
    throttle_avg: float
    brake_avg: float

class LapAnalysis(BaseModel):
    lap_number: int
    time: float
    best_time: bool
    sections: List[SectionAnalysis]
    telemetry_points: Optional[List[TelemetryPoint]] = None

class DriverComparison(BaseModel):
    driver_id: str
    best_lap_time: float
    avg_lap_time: float
    consistency: float
    top_speed: float
    sector_times: Dict[str, float]

class PitStopStrategy(BaseModel):
    recommended_laps: List[int]
    tire_degradation: Dict[str, float]
    time_loss: float
    time_gain: float
    strategy_type: str
    reasoning: str

class RacingLinePoint(BaseModel):
    lat: float
    lon: float
    speed: float
    optimal: bool
    suggestion: Optional[str] = None

class RacingLineAnalysis(BaseModel):
    current_line: List[RacingLinePoint]
    optimal_line: List[RacingLinePoint]
    improvements: List[str]
    time_potential: float

class RaceInsight(BaseModel):
    type: str
    title: str
    description: str
    impact: str
    lap: Optional[int] = None
    driver: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

