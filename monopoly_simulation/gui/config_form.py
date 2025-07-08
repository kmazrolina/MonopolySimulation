import streamlit as st
from simualtion import SimulationConfig  # your own class
from datetime import datetime

def render_config_form():
    # Ensure session_state keys exist
   
    with st.container():
        st.write("## Input your simulation configuration")
        
        sim_id = st.session_state.get('simulation_id', 1)

        sim_title = st.text_input("Simulation title", value=f"Simulation {sim_id}")
        start_cash = st.number_input("Starting cash for a player", value=2000, step=100)
        num_games = st.number_input("Number of games to run", value=100)
        max_turns = st.number_input("Number of turns per game", value=250, step=1)

        player_type = st.selectbox(
            "Player type",
            ["Always Buy", "Never Buy", "QLearning"]
        )

        # QLearning parameters (inside the form)
        alpha = gamma = epsilon = reward_strategy = None

        if player_type == "QLearning":
            st.write("#### QLearning parameters")
            alpha = st.slider("Learning rate (α)", 0.01, 1.0, 0.1, 0.01, key=f"alpha")
            gamma = st.slider("Discount factor (γ)", 0.01, 1.0, 0.9, 0.01, key=f"gamma")
            epsilon = st.slider("Exploration rate (ε)", 0.01, 1.0, 0.1, 0.01, key=f"epsilon")
            reward_strategy = st.selectbox(
                "Reward strategy",
                ["Sparse", "Dense", "Mixed"],
                index=0,
                help="""Sparse: Only wins or loses are rewarded or punished.
Dense: Successful property buys are rewarded more and a small reward for skipping a buy (saving cash).
Mixed: Combination of sparse and dense rewarding.""",
                key=f"reward"
            )

        game_preview = st.checkbox("Game preview", value=False, help="If checked, the game will be displayed in the dashboard the simulation. \
            This will slow down the execution, not recommanded for running more than one simulation")
        
        saved = st.button("Save")

        if saved:
            
            # Save simulation configuration
            sim_config = SimulationConfig()
            sim_config.player_type = player_type
            sim_config.start_cash = start_cash
            sim_config.num_games = num_games
            sim_config.max_turns = max_turns

            if player_type == "QLearning":
                sim_config.alpha = alpha
                sim_config.gamma = gamma
                sim_config.epsilon = epsilon
                sim_config.reward_strategy = reward_strategy.lower()
                
            st.session_state.run_history.loc[len(st.session_state.run_history)] = {
                "Simulation Title": sim_title,
                "Player Type": player_type,
                "Start Cash": start_cash,
                "Num Games": num_games,
                "Reward Strategy": reward_strategy if player_type == "QLearning" else None,
                "Alpha": alpha if player_type == "QLearning" else None,
                "Gamma": gamma if player_type == "QLearning" else None,
                "Epsilon": epsilon if player_type == "QLearning" else None,
            }
        
            st.session_state.simulation_config = sim_config
            st.session_state.simulation_id = sim_id + 1
            st.session_state.simulation_title = sim_title
            
            st.session_state.game_preview = game_preview

            st.session_state.show_form = False
            st.rerun()

            

            
