import argparse
import os
import random
from typing import List, Dict, Any
from collections import deque
import time

from monopoly_simulation.config import validate
from monopoly_simulation.player import Player, QLearningPlayer, create_player_from_type
from monopoly_simulation.board import Board



class SimulationConfig:
    def __init__(
        self,
        config_path: str=os.path.join("monopoly_simulation", "config", "default_config.yaml")
    ):
        self.load_config(config_path)

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file '{config_path}' does not exist.")
        
        config = validate.validate_config(config_path)

        self.alpha=config.get("alpha", 0.1)
        self.gamma=config.get("gamma", 0.9)
        self.epsilon=config.get("epsilon", 0.1)
        self.reward_strategy=config.get("reward_strategy", "sparse")
        self.board_size=config["board_size"]
        self.chance_fields=config["chance_fields"]
        self.chance_events=config.get("chance_events", [])
        self.die_faces=config["die_faces"]
        self.max_turns=config["max_turns"]
        self.player_type=config["player_type"]
        self.property_fields=config["property_fields"]
        self.property_price=config.get("property_price", 100)
        self.property_rent=config.get("property_rent", 10)
        self.start_cash=config["start_cash"]
        self.start_passing_cash=config.get("start_passing_cash", 200)
        self.tax_fields=config["tax_fields"]
        self.tax_amount=config.get("tax_amount", 50)
        self.train_agent=config.get("train_agent", False)
        self.train_test_ratio=config.get("train_test_ratio", 0.8)


class Simulation:
    def __init__(self, config: SimulationConfig, player: Player):
        self.config = config
        self.current_turn = 0
        self.board = Board(self.config) 
        self.player = player
        self.turn_outcomes_queue = deque() 
        

    def reset(self):
        self.current_turn = 0
        self.board = Board(self.config) 
        self.player.reset(self.config.start_cash)

    def die_roll(self):
        return random.randint(1, self.config.die_faces)

    def play_chance_event(self, chance_event: Dict[str, Any]):
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
            if self.current_turn != self.config.max_turns -1:
                self.current_turn += 1
            print(f"------->Running turn {self.current_turn}") # simulate skipping the next turn
            print("Skipping...")



    def run(self):
    
        while self.current_turn <= self.config.max_turns:
            
            turn_outcome = {
                "turn": self.current_turn,
                "player_position": self.player.position, #where player stepped on the board
                "player_cash": self.player.cash,
                "properties_owned": self.player.properties,
                "event": None,  # chance event, tax, property purchase or rent payment
                "description": None,  # description of the event
                "amount": None,  # amount of cash involved in the event
                "end_game_status": None, # win or bancrupt
                
            }
            
            if self.current_turn < self.config.max_turns:

                print(f"------->Running turn {self.current_turn + 1}")

                try:
                    

                    steps = self.die_roll()
                    
                    prev_position, new_position = self.player.move(steps, self.config.board_size)
                    print(f"Player moved from {prev_position} to {new_position}")
                    turn_outcome["player_position"] = new_position

                    if prev_position > new_position:
                        print("Player has passed the start field, receiving cash.")
                        self.player.receive(self.config.start_passing_cash)

                    
                    field = self.board.get_field(new_position)
                    print(f"Player landed on {field.field_type} field")
                    
                    if field.field_type == "Start":
                        print("Player is on the Start field")
                        
                        turn_outcome["event"] = "Start"
                        turn_outcome["description"] = "Received cash from Start field"
                        turn_outcome["amount"] = self.config.start_passing_cash
                    
                    elif field.field_type == "Tax":
                        print(f"Player pays tax of {field.tax_amount}")
                        self.player.pay(field.tax_amount)

                        turn_outcome["event"] = "Tax"
                        turn_outcome["description"] = f"Paid tax"
                        turn_outcome["amount"] = -field.tax_amount
                    
                    elif field.field_type == "Chance":
                        chance_event = field.chance_event
                        self.play_chance_event(chance_event)

                        turn_outcome["event"] = "Chance"
                        turn_outcome["description"] = chance_event["description"]
                        turn_outcome["amount"] = chance_event["amount"]

                                    
                    elif field.field_type == "Property":
                        if not field.is_owned:
                            print(f"Player buys property {field.name} for {field.price}")
                            bought = self.player.buy_property(field, self.current_turn )

                            if bought:
                                field.is_owned = True  
                                self.board.set_field(new_position, field)  # Update the board with the new property state

                                turn_outcome["event"] = "Property Purchase"
                                turn_outcome["description"] = field.name
                                turn_outcome["amount"] = -field.price
                            else:
                                print(f"Player skipped buying property {field.name}")
                                turn_outcome["event"] = "Buy Skip"
                                turn_outcome["description"] = field.name
                                turn_outcome["amount"] = 0
                        else:
                            print(f"Player pays rent of {field.rent}")
                            self.player.pay(field.rent)

                            turn_outcome["event"] = "Rent Payment"
                            turn_outcome["description"] = field.name
                            turn_outcome["amount"] = -field.rent

                except Player.Bankrupcy as e:
                    print(e)
                    
                    if isinstance(self.player, QLearningPlayer):
                        self.player.lose()

                    turn_outcome["end_game_status"] = "Bankrupcy"
                    turn_outcome["event"] = "Game Over"
                    turn_outcome["description"] = "Player has gone bancrupt"
                    self.turn_outcomes_queue.append(turn_outcome) 

                    return
                
                self.turn_outcomes_queue.append(turn_outcome) 
                self.current_turn += 1

            else:
                if isinstance(self.player, QLearningPlayer):
                    self.player.win()
                
                turn_outcome["end_game_status"] = "Win"
                turn_outcome["event"] = "Win"
                turn_outcome["description"] = f"🏆🎉 Player has won the game! (by lasting for {self.config.max_turns} turns without going bancrupt)"
                self.turn_outcomes_queue.append(turn_outcome) 
                print(turn_outcome["description"])
                return



def config_and_run_multiple_simulations(
        num_simulations: int, 
        player_type: str, 
        start_cash: int,
        max_turns: int,
        default_config_path: str=os.path.join("config", "default_config.yaml")
        ) -> List[dict]:
    

    if not os.path.exists(default_config_path):
        raise FileNotFoundError(f"Default configuration file '{default_config_path}' does not exist.")

    config = SimulationConfig(default_config_path)
    config.player_type = player_type
    config.start_cash = start_cash
    config.max_turns = max_turns

    
    player = create_player_from_type(
        player_type=config.player_type, 
        start_cash=config.start_cash, 
        alpha=config.alpha, 
        gamma=config.gamma, 
        epsilon=config.epsilon, 
        reward_strategy=config.reward_strategy
        )
    simulation = Simulation(config, player)
    

    for i in range(num_simulations):
        print(f"\n\nRunning simulation {i + 1}/{num_simulations}\n")
        simulation.run()
        simulation.reset()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Monopoly simulation.")
    parser.add_argument("--config_path", type=str, default=os.path.join("config", "default_config.yaml"), help="Path to the configuration file.")
    parser.add_argument("--num_simulations", type=int, default=1, help="Number of simulations to run.")
    parser.add_argument("--player_type", type=str, choices=["always_buy", "never_buy", "qlearning"], default="qlearning", help="Type of player to simulate.")
    parser.add_argument("--start_cash", type=int, default=2000, help="Starting cash for the player.")
    parser.add_argument("--max_turns", type=int, default=250, help="Maximum number of turns per game.")
    
    args = parser.parse_args()
    

    if not os.path.exists(args.config_path):
        raise FileNotFoundError(f"Configuration file '{args.config_path}' does not exist.")
    
    start = time.time()
    config_and_run_multiple_simulations(
        num_simulations=args.num_simulations,
        player_type=args.player_type,  # optionally change to "never_buy" or "qlearning" 
        start_cash=args.start_cash,
        max_turns=args.max_turns,
        default_config_path=args.config_path,
    )
    print(f"Simulation completed in {time.time() - start:.2f} seconds.")
    
