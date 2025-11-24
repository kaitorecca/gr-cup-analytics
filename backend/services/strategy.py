import pandas as pd
import numpy as np
from typing import List, Dict
from services.data_processor import DataProcessor
from models.schemas import PitStopStrategy

class StrategyService:
    def __init__(self, data_processor: DataProcessor):
        self.data_processor = data_processor
    
    def calculate_pit_stop_strategy(
        self,
        race_id: str,
        current_lap: int,
        total_laps: int,
        tire_degradation_rate: float = 0.02
    ) -> Dict:
        """Calculate optimal pit stop strategy"""
        
        # Get average lap times from race data
        results = self.data_processor.get_race_results(race_id)
        avg_lap_time = 100.0  # Default
        
        if not results.empty:
            # Estimate average lap time from best laps
            best_laps = []
            for _, row in results.iterrows():
                fl_time = row.get("FL_TIME", "")
                if fl_time:
                    lap_sec = self.data_processor._parse_lap_time(fl_time)
                    best_laps.append(lap_sec)
            
            if best_laps:
                # Average lap is typically 2-3 seconds slower than best lap
                avg_lap_time = np.mean(best_laps) + 2.5
        
        remaining_laps = total_laps - current_lap
        
        # Calculate tire degradation
        degradation = {}
        for lap in range(current_lap, total_laps + 1):
            laps_on_tires = lap - current_lap
            degradation[str(lap)] = tire_degradation_rate * laps_on_tires
        
        # Strategy options
        strategies = []
        
        # No pit stop
        no_pit_time = self._calculate_total_time(
            remaining_laps, avg_lap_time, tire_degradation_rate, 0
        )
        strategies.append({
            "type": "no_pit",
            "total_time": no_pit_time,
            "pit_laps": []
        })
        
        # One pit stop (mid-race)
        mid_lap = current_lap + remaining_laps // 2
        one_pit_time = self._calculate_total_time(
            remaining_laps, avg_lap_time, tire_degradation_rate, 1, mid_lap - current_lap
        )
        strategies.append({
            "type": "one_pit",
            "total_time": one_pit_time,
            "pit_laps": [mid_lap]
        })
        
        # Two pit stops (if long race)
        if remaining_laps > 20:
            pit1 = current_lap + remaining_laps // 3
            pit2 = current_lap + 2 * remaining_laps // 3
            two_pit_time = self._calculate_total_time(
                remaining_laps, avg_lap_time, tire_degradation_rate, 2,
                [pit1 - current_lap, pit2 - current_lap]
            )
            strategies.append({
                "type": "two_pit",
                "total_time": two_pit_time,
                "pit_laps": [pit1, pit2]
            })
        
        # Find best strategy
        best_strategy = min(strategies, key=lambda x: x["total_time"])
        
        # Calculate time gain/loss
        time_loss = best_strategy["total_time"] - no_pit_time
        pit_stop_time = 30.0  # Assume 30 seconds for pit stop
        time_gain = (no_pit_time - best_strategy["total_time"]) - (len(best_strategy["pit_laps"]) * pit_stop_time)
        
        reasoning = self._generate_reasoning(
            best_strategy, remaining_laps, tire_degradation_rate, time_gain
        )
        
        return {
            "recommended_laps": best_strategy["pit_laps"],
            "tire_degradation": degradation,
            "time_loss": time_loss,
            "time_gain": time_gain,
            "strategy_type": best_strategy["type"],
            "reasoning": reasoning,
            "all_strategies": strategies
        }
    
    def _calculate_total_time(
        self,
        laps: int,
        base_lap_time: float,
        degradation_rate: float,
        pit_stops: int,
        pit_lap: int = None
    ) -> float:
        """Calculate total time for a strategy"""
        total_time = 0.0
        pit_stop_time = 30.0  # 30 seconds per pit stop
        
        if pit_stops == 0:
            # No pit stops - all laps with degradation
            for lap in range(laps):
                lap_time = base_lap_time * (1 + degradation_rate * lap)
                total_time += lap_time
        elif pit_stops == 1 and pit_lap is not None:
            # One pit stop
            for lap in range(laps):
                if lap < pit_lap:
                    lap_time = base_lap_time * (1 + degradation_rate * lap)
                else:
                    # Fresh tires after pit
                    laps_on_new_tires = lap - pit_lap
                    lap_time = base_lap_time * (1 + degradation_rate * laps_on_new_tires)
                total_time += lap_time
            total_time += pit_stop_time
        elif pit_stops == 2 and isinstance(pit_lap, list):
            # Two pit stops
            pit1, pit2 = pit_lap
            for lap in range(laps):
                if lap < pit1:
                    lap_time = base_lap_time * (1 + degradation_rate * lap)
                elif lap < pit2:
                    laps_on_tires = lap - pit1
                    lap_time = base_lap_time * (1 + degradation_rate * laps_on_tires)
                else:
                    laps_on_tires = lap - pit2
                    lap_time = base_lap_time * (1 + degradation_rate * laps_on_tires)
                total_time += lap_time
            total_time += pit_stop_time * 2
        
        return total_time
    
    def _generate_reasoning(
        self,
        strategy: Dict,
        remaining_laps: int,
        degradation_rate: float,
        time_gain: float
    ) -> str:
        """Generate human-readable reasoning for strategy"""
        if strategy["type"] == "no_pit":
            return f"No pit stop recommended. Remaining {remaining_laps} laps manageable on current tires. Tire degradation ({degradation_rate*100:.1f}% per lap) is acceptable."
        
        elif strategy["type"] == "one_pit":
            pit_lap = strategy["pit_laps"][0]
            if time_gain > 0:
                return f"One pit stop at lap {pit_lap} recommended. Fresh tires will provide {abs(time_gain):.1f}s advantage over staying out, accounting for {30:.0f}s pit stop time."
            else:
                return f"One pit stop at lap {pit_lap} considered, but time loss of {abs(time_gain):.1f}s suggests staying out may be better unless tires are critical."
        
        elif strategy["type"] == "two_pit":
            pit1, pit2 = strategy["pit_laps"]
            return f"Two pit stops recommended at laps {pit1} and {pit2}. With {remaining_laps} laps remaining and {degradation_rate*100:.1f}% degradation per lap, fresh tires will maintain optimal pace."
        
        return "Strategy analysis complete."

