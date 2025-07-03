

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

    def buy_property(self, property_name, property_price):
        self.pay(property_price)
        self.properties.append(property_name)
            