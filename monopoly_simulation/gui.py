import time
import streamlit as st
import pandas as pd
import plotly.express as px

from simualtion import Simulation, SimulationConfig
from player import AlwaysBuyPlayer, NeverBuyPlayer, QLearningPlayer



def config_form(sim_id):
    """
    Load the configuration form for a specific simulation tab.
    """
    with st.form(f"config_form_{sim_id}"):
        st.write("Input your simulation configuration")
        sim_title = st.text_input("Simulation title", st.session_state.tab_names[sim_id])
        player_type = st.selectbox(
            "Player type",
            ["Always Buy", "Never Buy", "QLearning"],
            index=0,
        )
        start_cash = st.number_input(
            "Starting cash for a player",
            value=2000,
            step=100,
        )
        num_games = st.number_input(
            "Number of games to run",
            value=100,
        )

        submitted = st.form_submit_button("Save")
        if submitted:
            st.session_state.tab_names[sim_id] = sim_title
            st.session_state.show_form[sim_id] = False

            st.session_state.simulation_config = {
                "title": sim_title,
                "player_type": player_type,
                "start_cash": start_cash,
                "num_games": num_games,
            }
            st.rerun()




def run_simulations(sim_id, num_games=100):
    """
    Runs multiple simulations and updates the same Streamlit widget instead of creating new ones.
    """
    simulation = st.session_state.simulations[sim_id]
    
    # Init widgets

    
    # Win loose stats
    win_loose_col1, win_loose_col2 =  st.columns(2)
    with win_loose_col1:
        game_no = st.empty()
        turn = st.empty()
        player_cash = st.empty()
        avg_turns_bancrupt = st.empty()
    with win_loose_col2:
        win_loose_rate = st.empty()
    


    game_stats = pd.DataFrame(columns=["Game No", "Turns Played", "Player Cash", "End Game Status"])
    property_stats = pd.DataFrame(columns=["Property Name", "Revenue"])
    
    for i in range(num_games):
        simulation.run()
        game_no.write(f"Game No: {i+1}")
        while True:
            if simulation.turn_outcomes_queue:
                turn_outcome = simulation.turn_outcomes_queue.popleft()
                if turn_outcome:
        
                    turn.write(f"Turn: {turn_outcome["turn"] + 1}")
                    player_cash.write(f"💰 Player Cash: {turn_outcome['player_cash']} $")
                    if turn_outcome["event"] == "Rent Payment":
                        property_stats.loc[len(property_stats)] = {
                            "Property Name": turn_outcome["description"],
                            "Revenue": turn_outcome["amount"]
                        }
                    
                    if turn_outcome["end_game_status"] is not None:
                        game_stats.loc[len(game_stats)]={
                            "Game No": i + 1,
                            "Turns Played": turn_outcome["turn"],
                            "Player Cash": turn_outcome["player_cash"],
                            "End Game Status": turn_outcome["end_game_status"],
                            "Description": turn_outcome["description"]
                        }
                        break

                    
        simulation.reset()

        # Update WIN / LOOSE stats dynamically
        num_wins = len(game_stats[game_stats['End Game Status'] == 'Win'])
        num_losses = len(game_stats[game_stats['End Game Status'] == 'Bancrupcy'])
        
        pie_data = pd.DataFrame({
            'Outcome': ['Wins', 'Bankruptcies'],
            'Count': [num_wins, num_losses]
        })

        fig = px.pie(
            pie_data,
            names='Outcome',
            values='Count',
            color_discrete_sequence=[ '#e74c3c', '#2ecc71'],
            title='🏆 Wins vs 💀 Bankruptcies',
            
        )
        fig.update_layout(template='plotly_dark')
        win_loose_rate.plotly_chart(fig)

        avg_turns_bancrupt_value = game_stats[game_stats['End Game Status'] == 'Bancrupcy']['Turns Played'].mean()
        if pd.isna(avg_turns_bancrupt_value):
            avg_turns_bancrupt_value = 0.0
        
        avg_turns_bancrupt.write(
            f"""Average turns before bankruptcy:
            {avg_turns_bancrupt_value:.2f}"""
            )


    

    # Display property stats
    agg_prop_stats = property_stats.groupby("Property Name", as_index=False)["Revenue"].sum()
    agg_prop_stats = agg_prop_stats.sort_values("Property Name")

    fig = px.bar(
        agg_prop_stats,
        x="Property Name",
        y="Revenue",
        title="Total Revenue by Property",
        template="plotly_dark",  # Dark theme
        labels={"Revenue": "Total Revenue", "Property Name": "Property"}
    )

    st.plotly_chart(fig)


    # Display full game stats
    game_stats

    if st.button("Rerun"):
        st.session_state.stats[sim_id] = {}
        st.rerun()


def simulation_display(sim_id):
    """
    Runs simulation games and results.
    """
    
    
    player_type = st.session_state.simulation_config.get('player_type', 'QLearning')
    num_games = st.session_state.simulation_config.get('num_games', 100)
    start_cash = st.session_state.simulation_config.get('start_cash', 2000)

    col1, col2, col3 = st.columns(3, border=True)
    with col1:
        st.write(f"Player type: {player_type}")
    with col2:
        st.write(f"Starting cash: {start_cash}")
    with col3:
        st.write(f"Number of games: {num_games}")


    # Create simulation config
    st.session_state.simulation_configs[sim_id] = SimulationConfig()
    st.session_state.simulation_configs[sim_id].player_type = player_type.lower().replace(" ", "_")
    st.session_state.simulation_configs[sim_id].start_cash = start_cash
    config = st.session_state.simulation_configs[sim_id]  
    

    if config.player_type == "always_buy":
        player = AlwaysBuyPlayer(config.start_cash) 
    elif config.player_type == "never_buy":
        player = NeverBuyPlayer(config.start_cash)
    else:
        player = QLearningPlayer(
            alpha=0.1, 
            gamma=0.9, 
            epsilon=0.1, 
            start_cash=config.start_cash,
            train=config.train_agent
        )
    st.session_state.simulations[sim_id] = Simulation(
        config=config,
        player=player
    )


    run_simulations(sim_id, num_games)


        
        



def init_session_state():
    """
    Initialize session state variables if they do not exist.
    """
    if 'tab_names' not in st.session_state:
        st.session_state.tab_names = ["My First Simulation"]

    if 'show_form' not in st.session_state:
        st.session_state.show_form = [True for _ in st.session_state.tab_names]
    
    if 'simulation_configs' not in st.session_state:
        st.session_state.simulation_configs = [None for _ in st.session_state.tab_names]
    
    if 'simulations' not in st.session_state:
        st.session_state.simulations = [None for _ in st.session_state.tab_names]

    if 'stats' not in st.session_state:
        st.session_state.stats = [{} for _ in st.session_state.tab_names]
    




if __name__ == "__main__":
    st.set_page_config(
        page_title="Monopoly Simulation",
        page_icon=":money_with_wings:",
        
    )
    st.title("Monopoly Simulation")

    # Initialize session state 
    init_session_state()

    # Create tabs dynamically based on tab_names
    tabs_widget = st.tabs(st.session_state.tab_names)

    # Loop over tabs and render content
    for i, tab in enumerate(tabs_widget):
        with tab:
            # Ensure the show_form list is long enough
            if i >= len(st.session_state.show_form):
                st.session_state.show_form.append(True)

            if st.session_state.show_form[i]:
                config_form(i)
            else:
                simulation_display(i)