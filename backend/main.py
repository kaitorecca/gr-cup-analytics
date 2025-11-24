from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import datetime
import os

from services.data_processor import DataProcessor
from services.analytics import AnalyticsService
from services.strategy import StrategyService
from models.schemas import (
    LapAnalysis, DriverComparison, PitStopStrategy,
    TelemetryPoint, RaceInsight, SectionAnalysis
)

app = FastAPI(title="GR Cup Analytics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_processor = DataProcessor()
analytics_service = AnalyticsService(data_processor)
strategy_service = StrategyService(data_processor)

@app.get("/")
async def root():
    return {"message": "GR Cup Analytics API", "version": "1.0.0"}

@app.get("/api/races")
async def get_races():
    """Get list of available races"""
    races = data_processor.get_available_races()
    return {"races": races}

@app.get("/api/race/{race_id}/drivers")
async def get_drivers(race_id: str):
    """Get list of drivers for a specific race"""
    drivers = data_processor.get_drivers(race_id)
    return {"drivers": drivers}

@app.get("/api/race/{race_id}/driver/{driver_id}/laps")
async def get_driver_laps(race_id: str, driver_id: str):
    """Get lap times for a specific driver"""
    try:
        laps = data_processor.get_driver_laps(race_id, driver_id)
        return {"laps": laps}
    except Exception as e:
        print(f"Error getting driver laps: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/race/{race_id}/driver/{driver_id}/telemetry")
async def get_driver_telemetry(
    race_id: str, 
    driver_id: str, 
    lap: Optional[int] = None,
    sample_rate: int = 10
):
    """Get telemetry data for a driver (optionally filtered by lap)"""
    try:
        telemetry = data_processor.get_telemetry(
            race_id, driver_id, lap, sample_rate
        )
        return {"telemetry": telemetry}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/race/{race_id}/driver/{driver_id}/analysis")
async def get_driver_analysis(race_id: str, driver_id: str):
    """Get comprehensive analysis for a driver"""
    try:
        analysis = analytics_service.analyze_driver(race_id, driver_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/race/{race_id}/driver/{driver_id}/racing-line")
async def get_racing_line(race_id: str, driver_id: str):
    """Get racing line analysis and optimization suggestions"""
    try:
        racing_line = analytics_service.analyze_racing_line(race_id, driver_id)
        return racing_line
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/race/{race_id}/comparison")
async def compare_drivers(
    race_id: str, 
    driver_ids: str  # Comma-separated driver IDs
):
    """Compare multiple drivers"""
    try:
        driver_list = [d.strip() for d in driver_ids.split(",")]
        comparison = analytics_service.compare_drivers(race_id, driver_list)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/race/{race_id}/strategy/pit-stop")
async def calculate_pit_stop_strategy(
    race_id: str,
    current_lap: int,
    total_laps: int,
    tire_degradation_rate: float = 0.02
):
    """Calculate optimal pit stop strategy"""
    try:
        strategy = strategy_service.calculate_pit_stop_strategy(
            race_id, current_lap, total_laps, tire_degradation_rate
        )
        return strategy
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/race/{race_id}/insights")
async def get_race_insights(race_id: str):
    """Get key insights from the race"""
    try:
        insights = analytics_service.get_race_insights(race_id)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

