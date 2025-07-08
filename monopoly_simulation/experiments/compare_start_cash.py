import os
import argparse
import pandas as pd


from monopoly_simulation.player import create_player_from_type
from monopoly_simulation.simualtion import Simulation
from monopoly_simulation.experiments.stat_utils import *
from monopoly_simulation.experiments.runtime_utils import *



def parse_arguments():
    parser = argparse.ArgumentParser(description="Run Monopoly simulations with different starting cash amounts.")
    parser.add_argument("--start_cash_options", type=int, nargs="+", default=[1000, 1500, 2000],
                        help="Starting cash amount for the player (default: [1000, 1500, 2000])")
    parser.add_argument("--num_games", type=int, default=10000,
                        help="Number of games to simulate (default: 10000)")
    parser.add_argument("--max_turns", type=int, default=250,
                        help="Maximum number of turns per game (default: 250)")
    parser.add_argument("--player_type", type=str, default="always_buy",
                        choices=["always_buy", "never_buy", "qlearning"],
                        help="Type of player to simulate (default: always_buy)")
    return parser.parse_args()


def setup_simulations(config, args):
    simulations = []
    info_df = pd.DataFrame(columns=[
        "Simulation Title", "Player Type", "Start Cash", "Num Games",
        "Reward Strategy", "Alpha", "Gamma", "Epsilon"
    ])

    for start_cash in args.start_cash_options:
        config.start_cash = start_cash
        print(f"Running simulation with start cash: {start_cash}")

        player = create_player_from_type(
            player_type=config.player_type,
            start_cash=config.start_cash,
            alpha=config.alpha,
            gamma=config.gamma,
            epsilon=config.epsilon,
            reward_strategy=config.reward_strategy
        )

        simulation = Simulation(config, player)
        simulations.append({
            "title": f"Start Cash: {start_cash}",
            "simulation": simulation,
            "game_stats_df": None
        })

        info_df.loc[len(info_df)] = {
            "Simulation Title": f"Start Cash: {start_cash}",
            "Player Type": config.player_type,
            "Start Cash": start_cash,
            "Num Games": args.num_games,
            "Reward Strategy": config.reward_strategy if config.player_type == "qlearning" else None,
            "Alpha": config.alpha if config.player_type == "qlearning" else None,
            "Gamma": config.gamma if config.player_type == "qlearning" else None,
            "Epsilon": config.epsilon if config.player_type == "qlearning" else None,
        }

    return simulations, info_df


def main():
    args = parse_arguments()

    default_config_path = os.path.join("monopoly_simulation", "config", "default_config.yaml")
    config = load_config_and_validate(default_config_path)

    config.player_type = args.player_type
    config.max_turns = args.max_turns

    simulations, simulations_info_df = setup_simulations(config, args)
    
    st.set_page_config(page_title="Start Cash Comparison Report", page_icon=":money_with_wings:")
    st.title("Start Cash Comparison Report")

    running_info = st.empty()
    running_info.info(f"Running {args.num_games} games for player type: **{args.player_type}** and **starting cash amounts: {args.start_cash_options}**...")

    
    simulations = run_and_collect_results(simulations, args.num_games)

    game_stats_df, property_revenue_df, property_owned_df, player_cash_df = combine_results(simulations)

    running_info.success(f"Simulations completed. Total games played: {len(game_stats_df)}")
    
    st.write(simulations_info_df)
    display_game_stats(game_stats_df)
    display_cash_stats(player_cash_df)
    display_property_revenue_stats(property_revenue_df)
    display_property_ownership(property_owned_df)

if __name__ == "__main__":
    main()

    

    