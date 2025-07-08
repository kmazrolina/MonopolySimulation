import time
import random
import streamlit as st
import pandas as pd
import plotly.express as px

def get_random_color_seq(color_sequence=px.colors.qualitative.Antique):
    random_colors = random.sample(color_sequence, len(color_sequence))
    return random_colors

def get_owned_properties(simulation_title, game_no):
    """
    Get the properties owned by the player in a specific simulation and game number.
    """
    owned_properties = st.session_state.property_owned_stats[
        (st.session_state.property_owned_stats["Simulation Title"] == simulation_title) &
        (st.session_state.property_owned_stats["Game No"] == game_no)
    ]["Property Name"].unique()
    
    return owned_properties


def update_win_loose_stats(game_stats, win_loose_rate, avg_turns_bancrupt):
    num_wins = len(game_stats[game_stats['End Game Status'] == 'Win'])
    num_losses = len(game_stats[game_stats['End Game Status'] == 'Bankrupcy'])

    # Pie Chart: Wins vs Bankruptcies
    pie_data = pd.DataFrame({
        'Outcome': ['Wins', 'Bankruptcies'],
        'Count': [num_wins, num_losses]
    })

    fig_pie = px.pie(
        pie_data,
        names='Outcome',
        values='Count',
        title='Wins vs Bankruptcies',
        color_discrete_sequence=get_random_color_seq(),
        width=200
    )
    fig_pie.update_layout(template='plotly_dark')
    win_loose_rate.plotly_chart(fig_pie, key=f'win_loose_rate_{time.time()}')

    # Calculate overall average turns before bankruptcy
    avg_turns_bancrupt_value = game_stats.loc[game_stats['End Game Status'] == 'Bankrupcy', 'Turns Played'].mean()
    if pd.isna(avg_turns_bancrupt_value):
        avg_turns_bancrupt_value = 0.0

    avg_turns_bancrupt.write(
        f"""🕒 Average turns before bankruptcy:
        {int(avg_turns_bancrupt_value)}"""
    )

    
def display_game_stats():
    game_stats = st.session_state.game_stats.copy()

    if game_stats.empty:
        st.info("No simulation data available.")
        return

    # Filter bankruptcies
    bankruptcies = game_stats[game_stats["End Game Status"] == "Bankrupcy"]

    #  Average Turns Before Bankruptcy Chart
    if not bankruptcies.empty:
        avg_turns = bankruptcies.groupby("Simulation Title")["Turns Played"].mean().reset_index()
        avg_turns = avg_turns.sort_values("Turns Played", ascending=False)

        fig_avg_turns = px.bar(
            avg_turns,
            x="Simulation Title",
            y="Turns Played",
            title="Average Turns Before Bankruptcy",
            color="Simulation Title",
            color_discrete_sequence=get_random_color_seq(),
            text=avg_turns["Turns Played"].round(1),
            template="plotly_dark"
        )
        fig_avg_turns.update_traces(marker_line_width=1.5, textposition="outside")
        st.plotly_chart(fig_avg_turns, use_container_width=True)


    # Wins vs Bankruptcies Chart
    win_loss_counts = game_stats.groupby(["Simulation Title", "End Game Status"]).size().reset_index(name='Count')

    if win_loss_counts.empty:
        st.info("No win/loss outcomes recorded yet.")
        return

    pivot_data = win_loss_counts.pivot(index='Simulation Title', columns='End Game Status', values='Count').fillna(0).reset_index()

    # Dynamically detect present outcome types (Win, Bancrupcy, others)
    outcome_columns = [col for col in pivot_data.columns if col != "Simulation Title"]

    if not outcome_columns:
        st.info("No outcomes to display.")
        return

    melted = pivot_data.melt(id_vars=["Simulation Title"], value_vars=outcome_columns,
                             var_name="Outcome", value_name="Count")

    fig_outcomes = px.bar(
        melted,
        x="Simulation Title",
        y="Count",
        color="Outcome",
        color_discrete_sequence=get_random_color_seq(),
        barmode="group",
        title="Wins vs Bankruptcies per Simulation",
        template="plotly_dark",
    )
    fig_outcomes.update_traces(
        marker_line_width=1.5,
    )
    st.plotly_chart(fig_outcomes, use_container_width=True)



def display_property_revenue_stats():
    
    # Revenue by Property
    agg_prop_stats = st.session_state.property_reveue_stats.groupby(["Simulation Title", "Property Name"], as_index=False)["Revenue"].count()
    agg_prop_stats = agg_prop_stats.sort_values("Property Name")

    fig = px.bar(
        agg_prop_stats,
        x="Property Name",
        y="Revenue",
        color="Simulation Title",
        color_discrete_sequence=get_random_color_seq(),
        title="Freqency of Rent Collection by Property ",
        template="plotly_dark",  # Dark theme
        labels={"Revenue": "Rent Collected (times)", "Property Name": "Property"}
    )


    st.plotly_chart(fig, key=f'agg_prop_stats_{time.time()}')
    
    
    
    
    
def display_cash_stats():
    # Group by BOTH Simulation Title and Turn
    agg_player_cash = (
        st.session_state.player_cash_stats
        .groupby(["Simulation Title", "Turn"], as_index=False)["Player Cash"]
        .mean()
    )
    
    agg_player_cash = agg_player_cash.sort_values(["Simulation Title", "Turn"])

    fig = px.line(
        agg_player_cash,
        x="Turn",
        y="Player Cash",
        color="Simulation Title", 
        color_discrete_sequence=get_random_color_seq(),
        title="Average Player Cash Over Turns",
        template="plotly_dark",
        labels={"Player Cash": "Average Player Cash", "Turn": "Turn", "Simulation Title": "Simulation"}
    )

    st.plotly_chart(fig, key=f'agg_player_cash_{time.time()}')
    
    return agg_player_cash
    
def display_property_ownership():
    # Check if data is available
    if st.session_state.property_owned_stats.empty:
        st.info("No property ownership outcomes recorded yet.")
        return

    # Group by Simulation Title and Game No to count properties owned per game
    property_counts = (
        st.session_state.property_owned_stats
        .groupby(["Simulation Title", "Game No"], as_index=False)["Property Name"]
        .count()
        .rename(columns={"Property Name": "Properties Owned"})
    )

    # Average over games per Simulation
    avg_property_counts = (
        property_counts
        .groupby("Simulation Title", as_index=False)["Properties Owned"]
        .mean()
    )

    # Plot
    fig_outcomes = px.bar(
        avg_property_counts,
        x="Simulation Title",
        y="Properties Owned",
        color="Simulation Title",
        color_discrete_sequence=get_random_color_seq(),
        barmode="group",
        title="Average Properties Owned per Simulation",
        template="plotly_dark",
        labels={"Properties Owned": "Avg. Properties Owned"}
    )

    fig_outcomes.update_traces(marker_line_width=1.5)
    st.plotly_chart(fig_outcomes, use_container_width=True)

    

def display_cumulative_stats():
    
    # Display game stats
    display_game_stats()
     
    # Display property stats
    display_property_revenue_stats()
    
    # Display player cash and properoty worth stats
    display_cash_stats()
    
    display_property_ownership()