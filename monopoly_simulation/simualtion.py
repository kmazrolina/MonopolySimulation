import argparse
import os
import random
from typing import List, Dict, Any

from config import validate
from player import Player
from board import Board


class SimulationConfig:
    def __init__(
        self,
        config_path: str,
    ):
        self.load_config(config_path)

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file '{config_path}' does not exist.")
        
        config = validate.validate_config(config_path)

        self.board_size=config["board_size"]
        self.chance_fields=config["chance_fields"]
        self.chance_events=config.get("chance_events", [])
        self.die_faces=config["die_faces"]
        self.max_turns=config["max_turns"]
        self.property_fields=config["property_fields"]
        self.property_price=config.get("property_price", 100)
        self.property_rent=config.get("property_rent", 10)
        self.start_cash=config["start_cash"]
        self.tax_fields=config["tax_fields"]
        self.tax_amount=config.get("tax_amount", 50)
        


class Simulation:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.current_turn = 0
        self.board = Board(self.config)  # Initialize the board with the given configuration 
        self.player = Player(self.config.start_cash) #this is a single player game

    def die_roll(self):
        return random.randint(1, self.config.die_faces)

    def run(self):
        print(self.config.max_turns)
        while self.current_turn < self.config.max_turns:

            print(f"Running turn {self.current_turn + 1}")
            try:

                steps = self.die_roll()
                prev_position, new_position = self.player.move(steps, self.config.board_size)
                print(f"Player moved from {prev_position} to {new_position}")

                if prev_position > new_position:
                    print("Player has passed the start field, receiving cash.")
                    self.player.receive(self.config.start_cash) 
                
                field = self.board.get_field(new_position)
                print(f"Player landed on {field.field_type} field")
                
                if field.field_type == "Tax":
                    print(f"Player pays tax of {field.tax_amount}")
                    self.player.pay(field.tax_amount)
                
                elif field.field_type == "Chance":
                    chance_event = field.chance_event
                    print(f"Chance event: {chance_event["description"]}")
                    
                    if chance_event["action"] == "receive":
                        print(f"Player receives {chance_event["amount"]}")
                        self.player.receive(chance_event["amount"])
                    
                    elif chance_event["action"] == "pay":
                        print(f"Player must pay {chance_event["amount"]}")
                        self.player.pay(chance_event["amount"])
                    
                    elif chance_event["action"] == "move":
                        print(f"Player moves {chance_event["amount"]} steps")
                        self.player.move(chance_event["amount"], self.config.board_size)
                    
                    elif chance_event["action"] == "skip":
                        print("Player skips the next turn")
                        self.current_turn += 1
                        print(f"Running turn {self.current_turn + 1}") # simulate skipping the next turn
                        print("Skipping...")
                        
                elif field.field_type == "Property":
                    if field.owner is None:
                        print(f"Player buys property {field.name} for {field.price}")
                        self.player.buy_property(field.name, field.price)
                    else:
                        print(f"Player pays rent of {field.rent}")
                        self.player.pay(field.rent)

            except Player.Bancrupcy as e:
                print(e)
                return

            self.current_turn += 1
        print(f"🏆🎉 Player has won the game! (by lasting for {self.config.max_turns} without going bancrupt)")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Monopoly simulation.")
    parser.add_argument("--config_path", type=str, default=os.path.join("config", "default_config.yaml"), help="Path to the configuration file.")
    
    args = parser.parse_args()
    

    config = SimulationConfig(args.config_path)
    simulation = Simulation(config)
    simulation.run()
    
    