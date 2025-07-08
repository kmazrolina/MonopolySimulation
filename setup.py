from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="monopoly_simulation",
    version="0.1.0",
    author="Karolina Źróbek",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'monopoly-sim=monopoly_simulation.cli:app',
            'compare-reward-strategies=monopoly_simulation.cli:compare_reward_strategies',
            'compare-start-cash=monopoly_simulation.cli:compare_start_cash',
            'compare-players=monopoly_simulation.cli:compare_players',
        ],
    },
)
