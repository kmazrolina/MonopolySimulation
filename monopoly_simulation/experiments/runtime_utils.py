import os
import time
import concurrent.futures
import pandas as pd

from monopoly_simulation.simualtion import Simulation, SimulationConfig
from monopoly_simulation.experiments.stat_utils import (
    create_game_stats_df,
    create_property_revenue_stats_df,
    create_property_ownership_stats_df,
    create_player_cash_stats_df
)

def load_config_and_validate(default_config_path):
    if not os.path.exists(default_config_path):
        raise FileNotFoundError(f"Default configuration file '{default_config_path}' does not exist.")
    return SimulationConfig(default_config_path)

def run_multiple_simulations_with_report(
    num_games: int,
    simulation: Simulation,
    simulation_title: str = f"Simulation_{time.time()}"):
    
    report = []
    for i in range(num_games):
        print(f"\n\nRunning simulation {i + 1}/{num_games}\n")
        simulation.run()
        
        # Collecting game run info

        while simulation.turn_outcomes_queue:
            turn_outcome = simulation.turn_outcomes_queue.popleft()
            
            # Collecting the outcome for the report
            report.append({
                "simulation_title": simulation_title,
                "game_no": i,
                **turn_outcome
            })
        
        
        # Resetting the simulation for the next run
        simulation.reset()
    
    return pd.DataFrame(
        report, 
        columns=[
            "simulation_title",
            "game_no",
            "turn",
            "player_position",
            "player_cash",
            "properties_owned",
            "event",
            "description",
            "amount",
            "end_game_status"]
        )
    



def process_simulation(sim, num_games):
    simulation = sim["simulation"]
    simulation_title = sim["title"]

    turn_outcomes = run_multiple_simulations_with_report(
        num_games=num_games,
        simulation=simulation,
        simulation_title=simulation_title,
    )

    return {
        **sim,
        "game_stats_df": create_game_stats_df(turn_outcomes),
        "property_revenue_df": create_property_revenue_stats_df(turn_outcomes),
        "property_owned_df": create_property_ownership_stats_df(turn_outcomes),
        "player_cash_df": create_player_cash_stats_df(turn_outcomes),
    }

def run_and_collect_results(simulations, num_games):
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_simulation, sim, num_games) for sim in simulations]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    return results
