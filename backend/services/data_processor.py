import pandas as pd
import numpy as np
import os
import random
from typing import List, Dict, Optional
from pathlib import Path

class DataProcessor:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "barber"
        self.cache = {}
        
    def get_available_races(self) -> List[str]:
        """Get list of available races"""
        races = []
        # Check for R1/R2 pattern files
        for file in self.data_dir.glob("R*_barber_*.csv"):
            race_id = file.stem.split("_")[0]  # R1 or R2
            if race_id not in races:
                races.append(race_id)
        # Also check for Race 1/Race 2 pattern files
        for file in self.data_dir.glob("*Race*_Anonymized.CSV"):
            if "Race 1" in file.name and "R1" not in races:
                races.append("R1")
            elif "Race 2" in file.name and "R2" not in races:
                races.append("R2")
        # If no races found, return default
        if not races:
            return ["R1", "R2"]
        return sorted(races)
    
    def get_drivers(self, race_id: str) -> List[Dict]:
        """Get list of drivers for a race"""
        # Map R1/R2 to Race 1/Race 2 for file names
        race_name_map = {
            "R1": "Race 1",
            "R2": "Race 2",
            "Race 1": "Race 1",
            "Race 2": "Race 2"
        }
        race_name = race_name_map.get(race_id, race_id)
        
        # Try different file name patterns
        possible_files = [
            self.data_dir / f"03_Provisional Results_{race_name}_Anonymized.CSV",
            self.data_dir / f"03_Provisional Results_{race_id}_Anonymized.CSV",
            self.data_dir / f"03_Results GR Cup {race_name} Official_Anonymized.CSV",
            self.data_dir / f"03_Results GR Cup {race_id} Official_Anonymized.CSV",
            self.data_dir / f"05_Results by Class GR Cup {race_name} Official_Anonymized.CSV",
            self.data_dir / f"05_Results by Class GR Cup {race_id} Official_Anonymized.CSV",
        ]
        
        results_file = None
        for file in possible_files:
            if file.exists():
                results_file = file
                print(f"Found drivers file: {file}")
                break
        
        if not results_file:
            print(f"No drivers file found for {race_id}, using fallback data")
            # Return sample data for testing
            return [
                {"id": "13", "number": "13", "vehicle": "Toyota GR86", "class": "Am", "position": 1, "best_lap": 97.428, "total_time": "45:15.035"},
                {"id": "22", "number": "22", "vehicle": "Toyota GR86", "class": "Am", "position": 2, "best_lap": 97.746, "total_time": "45:17.775"},
                {"id": "72", "number": "72", "vehicle": "Toyota GR86", "class": "Am", "position": 3, "best_lap": 97.737, "total_time": "45:25.690"},
                {"id": "55", "number": "55", "vehicle": "Toyota GR86", "class": "Am", "position": 4, "best_lap": 98.094, "total_time": "45:26.144"},
                {"id": "2", "number": "2", "vehicle": "Toyota GR86", "class": "Am", "position": 5, "best_lap": 98.326, "total_time": "45:29.124"},
            ]
        
        try:
            df = pd.read_csv(results_file, sep=";")
            drivers = []
            for _, row in df.iterrows():
                drivers.append({
                    "id": str(row["NUMBER"]),
                    "number": str(row["NUMBER"]),
                    "vehicle": row.get("VEHICLE", "Toyota GR86"),
                    "class": row.get("CLASS", "Am"),
                    "position": int(row["POSITION"]),
                    "best_lap": self._parse_lap_time(row.get("FL_TIME", "0:00.000")),
                    "total_time": row.get("TOTAL_TIME", "")
                })
            print(f"Loaded {len(drivers)} drivers from {results_file}")
            return drivers
        except Exception as e:
            print(f"Error reading drivers file: {e}")
            import traceback
            traceback.print_exc()
            # Return sample data
            return [
                {"id": "13", "number": "13", "vehicle": "Toyota GR86", "class": "Am", "position": 1, "best_lap": 97.428, "total_time": "45:15.035"},
                {"id": "22", "number": "22", "vehicle": "Toyota GR86", "class": "Am", "position": 2, "best_lap": 97.746, "total_time": "45:17.775"},
                {"id": "72", "number": "72", "vehicle": "Toyota GR86", "class": "Am", "position": 3, "best_lap": 97.737, "total_time": "45:25.690"},
            ]
    
    def get_driver_laps(self, race_id: str, driver_id: str) -> List[Dict]:
        """Get lap times for a driver"""
        # Map R1/R2 to Race 1/Race 2 for file names
        race_name_map = {
            "R1": "Race 1",
            "R2": "Race 2",
            "Race 1": "Race 1",
            "Race 2": "Race 2"
        }
        race_name = race_name_map.get(race_id, race_id)
        
        # Try different file name patterns
        possible_files = [
            self.data_dir / f"99_Best 10 Laps By Driver_{race_name}_Anonymized.CSV",
            self.data_dir / f"99_Best 10 Laps By Driver_{race_id}_Anonymized.CSV",
        ]
        
        best_laps_file = None
        for file in possible_files:
            if file.exists():
                best_laps_file = file
                print(f"Found laps file: {file}")
                break
        
        if not best_laps_file:
            print(f"No laps file found for {race_id}, using fallback data for driver {driver_id}")
            # Return fallback lap data
            base_time = 97.0 + (int(driver_id) % 10) * 0.5
            laps = []
            for i in range(1, 11):
                lap_time = base_time + (i * 0.1) + (random.random() - 0.5) * 0.5
                laps.append({
                    "lap_number": i,
                    "time": lap_time,
                    "time_formatted": self._format_lap_time_from_seconds(lap_time)
                })
            return sorted(laps, key=lambda x: x["time"])
        
        try:
            df = pd.read_csv(best_laps_file, sep=";")
            print(f"Reading laps file: {best_laps_file}, looking for driver {driver_id}")
            print(f"Available driver numbers: {df['NUMBER'].unique()[:10]}")
            
            driver_data = df[df["NUMBER"] == int(driver_id)]
            
            if driver_data.empty:
                print(f"Driver {driver_id} not found in laps file. Available: {sorted(df['NUMBER'].unique())[:10]}")
                # Return fallback lap data
                base_time = 97.0 + (int(driver_id) % 10) * 0.5
                laps = []
                for i in range(1, 11):
                    lap_time = base_time + (i * 0.1) + (random.random() - 0.5) * 0.5
                    laps.append({
                        "lap_number": i,
                        "time": lap_time,
                        "time_formatted": self._format_lap_time_from_seconds(lap_time)
                    })
                return sorted(laps, key=lambda x: x["time"])
            
            row = driver_data.iloc[0]
            laps = []
            
            for i in range(1, 11):
                lap_time_str = row.get(f"BESTLAP_{i}", "")
                lap_num = row.get(f"BESTLAP_{i}_LAPNUM", 0)
                
                # Check if lap time exists and is valid
                if pd.notna(lap_time_str) and lap_time_str:
                    lap_time_str = str(lap_time_str).strip()
                    if lap_time_str and lap_time_str != 'nan':
                        time_seconds = self._parse_lap_time(lap_time_str)
                        if time_seconds > 0:
                            lap_number = int(lap_num) if pd.notna(lap_num) and lap_num != '' else i
                            laps.append({
                                "lap_number": lap_number,
                                "time": time_seconds,
                                "time_formatted": lap_time_str
                            })
            
            if laps:
                best_time = min([l['time'] for l in laps])
                print(f"✓ Found {len(laps)} REAL laps for driver {driver_id}, best: {best_time:.3f}s ({self._format_lap_time_from_seconds(best_time)})")
                return sorted(laps, key=lambda x: x["time"])
            else:
                print(f"✗ No valid laps parsed for driver {driver_id} from file")
                return []
        except Exception as e:
            print(f"Error reading laps file: {e}")
            # Return fallback data
            base_time = 97.0 + (int(driver_id) % 10) * 0.5
            laps = []
            for i in range(1, 11):
                lap_time = base_time + (i * 0.1)
                laps.append({
                    "lap_number": i,
                    "time": lap_time,
                    "time_formatted": self._format_lap_time_from_seconds(lap_time)
                })
            return sorted(laps, key=lambda x: x["time"])
    
    def get_telemetry(
        self, 
        race_id: str, 
        driver_id: str, 
        lap: Optional[int] = None,
        sample_rate: int = 10
    ) -> List[Dict]:
        """Get telemetry data for a driver"""
        telemetry_file = self.data_dir / f"{race_id}_barber_telemetry_data.csv"
        
        if not telemetry_file.exists():
            return []
        
        # For large files, we'll sample or use chunking
        try:
            # Read in chunks for large files
            chunk_size = 100000
            chunks = []
            max_chunks = 5  # Limit to prevent memory issues
            
            for i, chunk in enumerate(pd.read_csv(telemetry_file, chunksize=chunk_size, low_memory=False)):
                if i >= max_chunks:
                    break
                
                # Filter by vehicle_id if available
                vehicle_col = None
                for col in ["vehicle_id", "vehicle_number", "original_vehicle_id"]:
                    if col in chunk.columns:
                        vehicle_col = col
                        break
                
                if vehicle_col:
                    # Try to match driver ID
                    chunk = chunk[chunk[vehicle_col].astype(str).str.contains(str(driver_id), na=False)]
                
                if lap is not None and "lap" in chunk.columns:
                    chunk = chunk[chunk["lap"] == lap]
                
                if len(chunk) > 0:
                    chunks.append(chunk)
            
            if not chunks:
                return []
            
            df = pd.concat(chunks, ignore_index=True)
            
            # Sample data
            if len(df) > 10000:
                df = df.iloc[::sample_rate]
            
            # Map columns to our schema (try different column name variations)
            telemetry = []
            for _, row in df.iterrows():
                point = {
                    "timestamp": self._safe_get(row, "timestamp", self._safe_get(row, "meta_time", 0)),
                    "speed": self._safe_get(row, "Speed", 0),
                    "gear": int(self._safe_get(row, "Gear", 0)),
                    "rpm": self._safe_get(row, "nmot", 0),
                    "throttle": self._safe_get(row, "ath", 0),
                    "brake_front": self._safe_get(row, "pbrake_f", 0),
                    "brake_rear": self._safe_get(row, "pbrake_r", 0),
                    "acc_x": self._safe_get(row, "accx_can", 0),
                    "acc_y": self._safe_get(row, "accy_can", 0),
                    "steering_angle": self._safe_get(row, "Steering_Angle", 0),
                    "lat": self._safe_get(row, "VBOX_Lat_Min", 0) or self._safe_get(row, "VBOX_Lat", 0),
                    "lon": self._safe_get(row, "VBOX_Long_Minutes", 0) or self._safe_get(row, "VBOX_Long", 0),
                    "lap_distance": self._safe_get(row, "Laptrigger_lapdist_dls", 0)
                }
                telemetry.append(point)
            
            return telemetry[:5000]  # Limit response size
            
        except Exception as e:
            print(f"Error reading telemetry: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_lap_times(self, race_id: str) -> pd.DataFrame:
        """Get all lap times for a race"""
        lap_time_file = self.data_dir / f"{race_id}_barber_lap_time.csv"
        if not lap_time_file.exists():
            return pd.DataFrame()
        
        return pd.read_csv(lap_time_file)
    
    def get_race_results(self, race_id: str) -> pd.DataFrame:
        """Get race results"""
        # Map R1/R2 to Race 1/Race 2 for file names
        race_name_map = {
            "R1": "Race 1",
            "R2": "Race 2",
            "Race 1": "Race 1",
            "Race 2": "Race 2"
        }
        race_name = race_name_map.get(race_id, race_id)
        
        # Try different file name patterns
        possible_files = [
            self.data_dir / f"03_Provisional Results_{race_name}_Anonymized.CSV",
            self.data_dir / f"03_Provisional Results_{race_id}_Anonymized.CSV",
            self.data_dir / f"03_Results GR Cup {race_name} Official_Anonymized.CSV",
            self.data_dir / f"03_Results GR Cup {race_id} Official_Anonymized.CSV",
        ]
        
        results_file = None
        for file in possible_files:
            if file.exists():
                results_file = file
                print(f"Found race results file: {file}")
                break
        
        if not results_file:
            print(f"No race results file found for {race_id}")
            return pd.DataFrame()
        
        try:
            return pd.read_csv(results_file, sep=";")
        except Exception as e:
            print(f"Error reading race results file: {e}")
            return pd.DataFrame()
    
    def _parse_lap_time(self, time_str: str) -> float:
        """Parse lap time string (e.g., '1:37.428') to seconds"""
        try:
            if not time_str or pd.isna(time_str):
                return 0.0
            time_str = str(time_str).strip()
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = float(parts[1])
                    result = minutes * 60 + seconds
                    return result
            # Try direct float conversion
            return float(time_str)
        except Exception as e:
            print(f"Error parsing lap time '{time_str}': {e}")
            return 0.0
    
    def _format_lap_time_from_seconds(self, seconds: float) -> str:
        """Format seconds to lap time string (e.g., '1:37.428')"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}:{secs:06.3f}"
    
    def _safe_get(self, row: pd.Series, key: str, default: any) -> any:
        """Safely get value from pandas row"""
        try:
            value = row.get(key, default)
            if pd.isna(value):
                return default
            return float(value) if isinstance(value, (int, float)) else value
        except:
            return default

