import pandas as pd
import streamlit as st

from monopoly_simulation.gui.statistics import (
    display_game_stats, 
    display_property_revenue_stats, 
    display_cash_stats, 
    display_property_ownership
)


def create_game_stats_df(turn_outcomes):
    """
    Create a DataFrame summarizing game statistics from turn outcomes.
    """
    df = pd.DataFrame(turn_outcomes)
    df = df.groupby(['simulation_title', 'game_no'], as_index=False)\
      .agg({
          'turn': 'max',                         # Highest turn number → turns played
          'player_cash': 'last',                  # Last known cash
          'end_game_status': lambda x: x.dropna().iloc[-1] if x.dropna().any() else None  # Last non-null status
      })\
      .rename(columns={
          'simulation_title': 'Simulation Title',
          'game_no': 'Game No',
          'turn': 'Turns Played',
          'player_cash': 'Player Cash',
          'end_game_status': 'End Game Status'
      })
    return df
    
    
def create_property_revenue_stats_df(turn_outcomes):
    """
    Creates a DataFrame summarizing property revenue from turn outcomes.
    """
    df = pd.DataFrame(turn_outcomes)
    property_revenue_df = df[df['event'] == 'Rent Payment']

    # Create summarized DataFrame
    property_revenue_df = (
        property_revenue_df
        .groupby(['simulation_title', 'game_no', 'description'], as_index=False)['amount']
        .sum()
        .rename(columns={
            'simulation_title': 'Simulation Title',
            'game_no': 'Game No',
            'description': 'Property Name',
            'amount': 'Revenue'
        })
    )
    return property_revenue_df

    
def create_property_ownership_stats_df(turn_outcomes):
    """
    Creates a DataFrame summarizing property ownership from turn outcomes.
    """
    df = pd.DataFrame(turn_outcomes)
    purchase_df = df[df['event'] == 'Property Purchase']

    # Create the summary DataFrame
    property_owned_df = purchase_df.rename(columns={
        'simulation_title': 'Simulation Title',
        'game_no': 'Game No',
        'description': 'Property Name',
        'turn': 'Turn',
        'amount': 'Price'
    })[["Simulation Title", "Game No", "Property Name", "Turn", "Price"]]
    
    return property_owned_df


def create_player_cash_stats_df(turn_outcomes):
    """
    Creates a DataFrame summarizing player cash from turn outcomes.
    """
    df = pd.DataFrame(turn_outcomes)
    player_cash_df = df[["simulation_title", "game_no", "turn", "player_cash"]].rename(columns={
        'simulation_title': 'Simulation Title',
        'game_no': 'Game No',
        'turn': 'Turn',
        'player_cash': 'Player Cash'
    })
    
    return player_cash_df



def combine_results(simulations):
    """
    Combines results from multiple simulations into a single DataFrame for each type of statistic.
    Each simulation should have a dictionary with keys: "game_stats_df", "property_revenue_df", "property_owned_df", and "player_cash_df".
    
    """
    game_stats_df = pd.concat([sim["game_stats_df"] for sim in simulations if sim["game_stats_df"] is not None])
    property_revenue_df = pd.concat([sim["property_revenue_df"] for sim in simulations if sim["property_revenue_df"] is not None])
    property_owned_df = pd.concat([sim["property_owned_df"] for sim in simulations if sim["property_owned_df"] is not None])
    player_cash_df = pd.concat([sim["player_cash_df"] for sim in simulations if sim["player_cash_df"] is not None])

    return game_stats_df, property_revenue_df, property_owned_df, player_cash_df



