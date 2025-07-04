from collections import defaultdict
import random

class Player:
    def __init__(self, cash=2000):
        self.cash = cash
        self.position = 0
        self.properties = []
        

    class Bancrupcy(Exception):
        """Exception raised for bankruptcy in the game."""
        def __init__(self):
            super().__init__("GAME OVER: Player has gone bankrupt! 😭💸")


    def move(self, steps, board_size=20):
        prev_position = self.position
        self.position = (self.position + steps) % board_size
        return prev_position, self.position
        
    def pay(self, amount):
        if amount > self.cash:
            raise self.Bancrupcy()
        self.cash -= amount

    def receive(self, amount):
        self.cash += amount
    
    def reset(self, start_cash=2000):
        self.cash = start_cash
        self.position = 0
        self.properties = []
        


class QLearningPlayer(Player):
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, train=False, start_cash=2000):
        self.q_table = defaultdict(float)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.train = train

        super().__init__(cash=start_cash)  


    class State:
        def __init__(self, property_price, cash, turns_left, properties):
            self.property_price = property_price
            self.cash = cash
            self.turns_left = turns_left
            self.properties = properties


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
        print(f"\tUpdating Q-value for state {state} and action '{action}': old value = {old_value}, new value = {new_value}")
        self.q_table[(state, action)] = new_value

    def buy_property(self, property_name, property_price, turns_left=250):
        if self.train:
            state = self.State( property_price, self.cash, turns_left, self.properties)
            action = self.choose_action(state, ["buy", "skip"])
            if action == "buy":
                try:
                    self.pay(property_price)
                    self.properties.append(property_name)
                    reward = 1
                    next_state = self.State(None, self.cash, turns_left -1, self.properties)
                    self.update(state, action, reward, next_state, ["buy", "skip"])

                except self.Bancrupcy:
                    punishment = -1
                    next_state = self.State(None, self.cash, turns_left - 1, self.properties)
                    self.update(state, action, punishment, next_state, ["buy", "skip"])
                    raise self.Bancrupcy()
            else:
                reward = 0.5
                next_state = self.State(None, self.cash, turns_left - 1, self.properties)
                self.update(state, action, reward, next_state, ["buy", "skip"])
        

class AlwaysBuyPlayer(Player):
    def __init__(self, cash=2000):
        super().__init__(cash)
          
    def buy_property(self, property_name, property_price, turns_left=None):
        self.pay(property_price)
        self.properties.append(property_name)


class NeverBuyPlayer(Player):
    def __init__(self, cash=2000):
        super().__init__(cash)
          
    def buy_property(self, property_name=None, property_price=None, turns_left=None):
        return