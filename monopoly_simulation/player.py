from collections import defaultdict
import random

class Player:
    def __init__(self, cash=2000):
        self.cash = cash
        self.position = 0
        self.properties = []
        

    class Bankrupcy(Exception):
        """Exception raised for bankruptcy in the game."""
        def __init__(self):
            super().__init__("GAME OVER: Player has gone bankrupt! 😭💸")


    def move(self, steps, board_size=20):
        prev_position = self.position
        self.position = (self.position + steps) % board_size
        return prev_position, self.position
        
    def pay(self, amount):
        if amount > self.cash:
            raise self.Bankrupcy()
        self.cash -= amount

    def receive(self, amount):
        self.cash += amount
    
    def reset(self, start_cash=2000):
        self.cash = start_cash
        self.position = 0
        self.properties = []
        


class QLearningPlayer(Player):
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, reward_strategy='mixed', start_cash=2000):
        self.q_table = defaultdict(float)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.reward_strategy = reward_strategy.lower()
        self.eval = False  
        
        self.init_rewards()
        
        super().__init__(cash=start_cash)  

    def init_rewards(self):
        if self.reward_strategy == 'dense':
            self.reward_buy_factor = 1
            self.reward_skip_factor = 0.5
            
            self.reward_win_factor = None
            self.punishment_lose = -1000
            
        elif self.reward_strategy == 'sparse':
            self.reward_buy_factor = None
            self.reward_skip_factor = None

            self.reward_win_factor = 100
            self.punishment_lose = -1000
        else:
            self.reward_buy_factor = 1
            self.reward_skip_factor = 0.5
            
            self.reward_win_factor = 100
            self.punishment_lose = -1000
            
    class State:
        def __init__(self, property_price, cash, turns_left, properties):
            self.property_price = property_price
            self.cash = cash
            self.turns_left = turns_left
            self.properties = properties


    def get_q(self, state, action):
        return self.q_table[(state, action)]

    def choose_action(self, state, actions):
        """
        Chooses an action based on the epsilon-greedy strategy.
        With probability epsilon, a random action is chosen.
        With probability 1 - epsilon, the action with the highest Q-value is chosen.
        """
        if random.random() < self.epsilon:
            return random.choice(actions)
        else:
            q_values = [self.get_q(state, a) for a in actions]
            max_q = max(q_values)
            best_actions = [a for a, q in zip(actions, q_values) if q == max_q]
            return random.choice(best_actions)

    def update(self, state, action, reward, next_state, next_actions):
        """
        Updates the Q-value for a given state-action pair using the Q-learning update rule.
        The update rule is:
        Q(s, a) = Q(s, a) + α * (r + γ * max_a' Q(s', a') - Q(s, a))
        where:
        - Q(s, a) is the current Q-value for state s and action a
        - α is the learning rate    
        - r is the reward received after taking action a in state s
        - γ is the discount factor
        - max_a' Q(s', a') is the maximum Q-value for the next state s' over all possible actions a'
        - Q(s', a') is the Q-value for the next state s' and action a'
        
        """
        max_q_next = max([self.get_q(next_state, a) for a in next_actions], default=0)
        old_value = self.q_table[(state, action)]
        new_value = old_value + self.alpha * (reward + self.gamma * max_q_next - old_value)
        
        print(f"\tUpdating Q-value for state {state} and action '{action}': old value = {old_value}, new value = {new_value}")
        self.q_table[(state, action)] = new_value


    def buy_property(self, property, turns_left=250):
        """
        This method is called when the player decides to buy a property.
        It updates the player's cash, properties, and Q-table.
        """

        state = self.State( property.price, self.cash, turns_left, len(self.properties))
        action = self.choose_action(state, ["buy", "skip"])
        
        if action == "buy":
            try:
                self.pay(property.price)
                self.properties.append(property)
                
                should_update = True if not self.eval and self.reward_strategy != 'sparse' else False
                
                if should_update:
                    reward = self.reward_buy_factor * property.price 
                    next_state = self.State(None, self.cash, turns_left -1, len(self.properties))
                    self.update(state, action, reward, next_state, ["buy", "skip"])

            except self.Bankrupcy:

                if not self.eval:
                    punishment = self.punishment_lose
                    next_state = self.State(None, self.cash, turns_left - 1, self.properties)
                    self.update(state, action, punishment, next_state, ["buy", "skip"])
                
                raise self.Bankrupcy()
            
        else:
            # Skipping the buy
            should_update = True if not self.eval and self.reward_strategy != 'sparse' else False
            if should_update:
                reward = self.reward_skip_factor * property.price
                next_state = self.State(None, self.cash, turns_left - 1, self.properties)
                self.update(state, action, reward, next_state, ["buy", "skip"])
        
        return action == "buy"
                
        
    def win(self):
        """
        This method is called when the player wins the game.
        It can be used to update the Q-table or perform any other actions needed upon winning.
        """
        should_update = True if not self.eval and self.reward_strategy != 'dense' else False
        if should_update:
            state = self.State( None, self.cash, 0, self.properties)
            reward = self.reward_win_factor * self.cash + sum([prop.price for prop in self.properties])  
            for action in ["buy", "skip"]:
                self.update(state, action, reward, state, ["buy", "skip"])
                
    def lose(self):
        """
        This method is called when the player loses the game.
        It can be used to update the Q-table or perform any other actions needed upon losing.
        """
        if not self.eval:
            state = self.State( None, self.cash, 0, self.properties)
            punishment = self.punishment_lose
            for action in ["buy", "skip"]:
                self.update(state, action, punishment, state, ["buy", "skip"])
    
    def eval_mode(self):
        """
        Sets the player to evaluation mode.
        In this mode, the player will not update the Q-table.
        """
        self.eval = True
        self.epsilon = 1
        

class AlwaysBuyPlayer(Player):
    def __init__(self, cash=2000):
        super().__init__(cash)
          
    def buy_property(self, property, turns_left=None):
        self.pay(property.price)
        self.properties.append(property)
        return True


class NeverBuyPlayer(Player):
    def __init__(self, cash=2000):
        super().__init__(cash)
          
    def buy_property(self, property, turns_left=None):
        return False
    
    
def create_player_from_type(player_type, start_cash=2000, **kwargs):
    """
    Factory function to create a player instance based on the player type.
    """
    if player_type == "always_buy":
        return AlwaysBuyPlayer(cash=start_cash)
    elif player_type == "never_buy":
        return NeverBuyPlayer(cash=start_cash)
    elif player_type == "qlearning":
        return QLearningPlayer(start_cash=start_cash, **kwargs)
    else:
        raise ValueError(f"Unknown player type: {player_type}")