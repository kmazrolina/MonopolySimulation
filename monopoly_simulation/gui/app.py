"""
Main entry point for the Monopoly Simulation application.
This script initializes the Streamlit app, sets up session state, and creates tabs for different simulations
"""

import streamlit as st

from monopoly_simulation.gui.session_state_init import init_session_state
from monopoly_simulation.gui.config_form import render_config_form
from monopoly_simulation.gui.runtime import render_simulation_display


def main():
    st.set_page_config(
        page_title="Monopoly Simulation",
        page_icon=":money_with_wings:",
    
    )
    st.title("Monopoly Simulation")

    # Initialize session state variables
    init_session_state()

    if st.session_state.show_form:
        render_config_form()
    else:
        render_simulation_display()

if __name__ == "__main__":
    main()
    
    
