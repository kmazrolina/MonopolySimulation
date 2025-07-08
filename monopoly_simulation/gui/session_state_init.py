import streamlit as st
import pandas as pd


def init_session_state():
    """
    Initialize session state variables if they do not exist.
    """

    if 'simulation_config' not in st.session_state:
        st.session_state.simulation_config = None
    
    if 'simulation' not in st.session_state:
        st.session_state.simulation = None

    if 'game_preview' not in st.session_state:
        st.session_state.game_preview = False
    
    if 'run_history' not in st.session_state:
        st.session_state.run_history = pd.DataFrame(columns=[
            "Simulation Title", 
            "Player Type", 
            "Start Cash", 
            "Num Games",
            "Reward Strategy", 
            "Alpha", 
            "Gamma", 
            "Epsilon",
            ], index=None)

    if 'game_stats' not in st.session_state:
        st.session_state.game_stats = pd.DataFrame(columns=["Simulation Title", "Game No", "Turns Played", "Player Cash", "End Game Status"])

    if 'property_reveue_stats' not in st.session_state:
        st.session_state.property_reveue_stats = pd.DataFrame(columns=["Simulation Title", "Game No", "Property Name","Revenue"])
        
    if 'property_owned_stats' not in st.session_state:
        st.session_state.property_owned_stats = pd.DataFrame(columns=["Simulation Title", "Game No", "Property Name","Turn", "Price"])

    if 'player_cash_stats' not in st.session_state:
        st.session_state.player_cash_stats = pd.DataFrame(columns=["Simulation Title", "Game No", "Turn", "Player Cash"])

    if 'simulation_title' not in st.session_state:
        st.session_state.simulation_title = ""

    if 'num_simulations' not in st.session_state:
        st.session_state.num_simulations = 0
        
    if 'show_form' not in st.session_state:
        st.session_state.show_form = True
        
    if 'speed' not in st.session_state:
        st.session_state.speed = 0.7
        
    st.session_state.eval_started_game = None
