import subprocess
import sys
import os

def compare_reward_strategies():
    script_path = os.path.join(os.path.dirname(__file__), 'experiments', 'compare_reward_strategies.py')
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])

def compare_start_cash():
    script_path = os.path.join(os.path.dirname(__file__), 'experiments', 'compare_start_cash.py')
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])

def compare_players():
    script_path = os.path.join(os.path.dirname(__file__), 'experiments', 'compare_players.py')
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])

def app():
    script_path = os.path.join(os.path.dirname(__file__), 'gui', 'app.py')
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])
    
    
    
