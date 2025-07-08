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
    def __init__(self, alpha=0.1, gamma=0.8, epsilon=0.1, reward_strategy='mixed', start_cash=2000):
        self.q_table = defaultdict(float)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.reward_strategy = reward_strategy.lower()
        self.eval = False  
        self.last_action = None
        self.last_state = None
        
        self.init_rewards()
        
        super().__init__(cash=start_cash)  

    def init_rewards(self):
        # Balanced rewards & punishments
        self.reward_buy = 50
        self.reward_skip = 30
        self.reward_win = 5000
        self.punishment_lose = -5000

    def get_q(self, state, action):
        return self.q_table[(state, action)]

    def choose_action(self, state, actions):
        if random.random() < self.epsilon:
            return random.choice(actions)
        else:
            q_values = [self.get_q(state, a) for a in actions]
            max_q = max(q_values)
            best_actions = [a for a, q in zip(actions, q_values) if q == max_q]
            return random.choice(best_actions)

    def update(self, state, action, reward, next_state, next_actions):
        max_q_next = max([self.get_q(next_state, a) for a in next_actions], default=0)
        old_value = self.q_table[(state, action)]
        new_value = old_value + self.alpha * (reward + self.gamma * max_q_next - old_value)
        self.q_table[(state, action)] = new_value

    def buy_property(self, property, turns_played=0):
        state = (self.cash, len(self.properties))
        action = self.choose_action(state, ["buy", "skip"])
        self.last_action = action
        self.last_state = state
        
        if action == "buy":
            self.pay(property.price)
            self.properties.append(property)
            
            if not self.eval and self.reward_strategy != 'sparse':
                reward = self.reward_buy
                
                # Soft penalties for low cash to avoid bankruptcy
                if self.cash < 500:
                    reward -= 100
                if self.cash < 100:
                    reward -= 500
                
                next_state = (self.cash, len(self.properties))
                self.update(state, action, reward, next_state, ["buy", "skip"])

        else:
            if not self.eval and self.reward_strategy != 'sparse':
                reward = self.reward_skip
                next_state = (self.cash, len(self.properties))
                self.update(state, action, reward, next_state, ["buy", "skip"])
        
        return action == "buy"

    def win(self):
        if not self.eval and self.reward_strategy != 'dense':
            reward = self.reward_win + self.cash  # reward both winning and remaining cash
            state = (self.cash, len(self.properties))
            self.update(self.last_state, self.last_action, reward, state, ["buy", "skip"])

    def lose(self):
        if not self.eval and self.reward_strategy != 'dense':
            punishment = self.punishment_lose
            state = (self.cash, len(self.properties))
            self.update(self.last_state, self.last_action, punishment, state, ["buy", "skip"])

    def eval_mode(self):
        self.eval = True
        self.epsilon = 0  # pure exploitation
        

class AlwaysBuyPlayer(Player):
    def __init__(self, cash=2000):
        super().__init__(cash)
          
    def buy_property(self, property, turns_played=None):
        self.pay(property.price)
        self.properties.append(property)
        return True


class NeverBuyPlayer(Player):
    def __init__(self, cash=2000):
        super().__init__(cash)
          
    def buy_property(self, property, turns_played=None):
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