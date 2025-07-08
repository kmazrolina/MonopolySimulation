import time
import streamlit as st


from simualtion import Simulation
from player import AlwaysBuyPlayer, NeverBuyPlayer, QLearningPlayer
from gui.board_display import render_html_board_with_game
from gui.statistics import display_cumulative_stats, update_win_loose_stats, get_owned_properties


def run_simulations(num_games=100):
    """
    Runs multiple simulations and updates the same Streamlit widget instead of creating new ones.
    """

    # Layout for displaying game stats
    win_loose_col1, win_loose_col2 =  st.columns(2)
    
    if st.session_state.game_preview:
        with win_loose_col1:
            game_no = st.empty()
            turn = st.empty()
            player_cash = st.empty()
            player_properties = st.empty()
            avg_turns_bancrupt = st.empty()
            qlearning_phase = st.empty()
            win_loose_rate = st.empty()
        with win_loose_col2:
            sim_board = st.empty()
    else:
        with win_loose_col1:
            game_no = st.empty()
            turn = st.empty()
            player_cash = st.empty()
            player_properties = st.empty()
            avg_turns_bancrupt = st.empty()
            qlearning_phase = st.empty()
        with win_loose_col2:
            win_loose_rate = st.empty()
        
    
    simulation = st.session_state.simulation # Get the simulation from session state
        
    # Print initial game number    
    game_no.write(f"Running game 0/{num_games}...")
    if st.session_state.simulation_config.player_type.lower() == "qlearning":
        qlearning_phase.write(f"🤖 QLearning Phase: Training")
    

    # Running games
    for i in range(num_games):
        
        if st.session_state.game_preview:
            game_no.write(f"Game No: {i+1}")
        else:
            if i % 10 == 0:
                game_no.write(f"Running game {i}/{num_games}...")
                
        # Turn qLearning player into eval mode if the game is not in training phase
        if st.session_state.simulation_config.player_type.lower() == "qlearning":
            if i > st.session_state.simulation_config.train_test_ratio * num_games \
                and st.session_state.eval_started_game is None:
                simulation.player.eval_mode = True
                st.session_state.eval_started_game = i
                qlearning_phase.write(f"🤖 QLearning Phase: Evaluation")
                
        
        simulation.run() # Runs fast and adds all events to the queue

        # Events are read from the queue
        # and displayed in the Streamlit app
        while True:
            
            # check if the simlation event is available
            turn_outcome = simulation.turn_outcomes_queue.popleft()
            
            
            if turn_outcome:

                if st.session_state.game_preview:
                    turn.write(f"Turn: {turn_outcome["turn"] + 1}")
                    player_cash.write(f"💰 Player Cash: {turn_outcome['player_cash']} $")
                    

                            
                st.session_state.player_cash_stats.loc[len(st.session_state.player_cash_stats)] = {
                    "Simulation Title": st.session_state.simulation_title,
                    "Game No": i,
                    "Turn": turn_outcome["turn"],
                    "Player Cash": turn_outcome["player_cash"]
                }
                
                # Check if the turn outcome is a rent payment
                if turn_outcome["event"] == "Rent Payment":
                    st.session_state.property_reveue_stats.loc[len(st.session_state.property_reveue_stats)] = {
                        "Simulation Title": st.session_state.simulation_title,
                        "Game No": i,
                        "Property Name": turn_outcome["description"],
                        "Revenue": turn_outcome["amount"]
                    }
                    
                    
                elif turn_outcome["event"] == "Property Purchase":
                    
                    st.session_state.property_owned_stats.loc[len(st.session_state.property_owned_stats)] = {
                        "Simulation Title": st.session_state.simulation_title,
                        "Game No": i,
                        "Property Name": turn_outcome["description"],
                        "Turn": turn_outcome["turn"],
                        "Price": turn_outcome["amount"]
                    }
                    
                    if st.session_state.game_preview:
                        owned_properties =get_owned_properties(simulation_title=st.session_state.simulation_title, game_no=i)
                        player_properties.write(f"🏠 Player Properties: {len(owned_properties)}")
                
                    
                if st.session_state.game_preview:
                    sim_board.html( render_html_board_with_game(
                        board=simulation.board,
                        simulation_title=st.session_state.simulation_title,
                        game_no=i,
                        turn_outcome=turn_outcome
                    ))
                    
            
                
                # Check if the game has ended
                if turn_outcome["end_game_status"] is not None:
                    st.session_state.game_stats.loc[len(st.session_state.game_stats)]={
                        "Simulation Title": st.session_state.simulation_title,
                        "Game No": i,
                        "Turns Played": turn_outcome["turn"],
                        "Player Cash": turn_outcome["player_cash"],
                        "End Game Status": turn_outcome["end_game_status"],
                        "Description": turn_outcome["description"]
                    }
                    break
            if st.session_state.game_preview:
                # Wait for the specified speed before processing the next turn
                time.sleep(st.session_state.speed)
            
        # Reset the simulation for the next game
        simulation.reset()

        # Update WIN / LOOSE stats dynamically
        if st.session_state.game_preview:
            update_win_loose_stats(
                st.session_state.game_stats, 
                win_loose_rate, 
                avg_turns_bancrupt
            )
        
        
    
    # Print final game number    
    game_no.write(f"Running game {num_games}/{num_games}...")
          
    # After all games are done, display the final stats
    st.write("### Game Statistics Across Simulations")
    if not st.session_state.game_preview:
        update_win_loose_stats(
            st.session_state.game_stats, 
            win_loose_rate, 
            avg_turns_bancrupt
        )
        if st.session_state.simulation_config.player_type.lower() == "qlearning":
            training_phinished = st.session_state.eval_started_game
            if training_phinished is not None:
                qlearning_phase.write(f"🤖 QLearning Training Finished at Game No {training_phinished}")
    

    
    
    
def display_simulation_runtime_info():
    """
    Displays the simulation runtime with board and player position.
    """
    # First display info about all simulations that were run
    st.write("### Run History")
    st.write(st.session_state.run_history)
    
    # Display the current simulation title
    st.write("#### Current Simulation: ", st.session_state.simulation_title)
    
    
    # Display the player type
    st.write("Player Type: ", st.session_state.simulation_config.player_type)



def initialize_simulation():
    config = st.session_state.simulation_config
    

    # Create a player
    config.player_type = config.player_type.lower().replace(" ", "_")
    print(f"Creating player of type: {config.player_type}")
    if config.player_type == "always_buy":
        player = AlwaysBuyPlayer(config.start_cash) 
    elif config.player_type == "never_buy":
        player = NeverBuyPlayer(config.start_cash)
    elif config.player_type == "qlearning":
        player = QLearningPlayer(
            alpha=config.alpha,
            gamma= config.gamma, 
            epsilon=config.epsilon,
            start_cash=config.start_cash,
            reward_strategy=config.reward_strategy,
        )
        
    # Initialize the simulation with the config and player
    st.session_state.simulation = Simulation(
        config=config,
        player=player
    )

    

def render_simulation_display():
    """
    Prepares layout for simulation runtime and statistics.
    Runs multiple simulations according to the configuration
    """
    if st.button("↺ Run new simulation"):
        st.session_state.show_form = True
        st.rerun()
        return
    
    
    display_simulation_runtime_info()
    
    initialize_simulation()
    
    run_simulations(st.session_state.simulation_config.num_games)
    
    display_cumulative_stats()

    




