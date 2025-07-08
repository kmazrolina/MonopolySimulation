import random
import randomname

from monopoly_simulation.fields import StartField, TaxField, ChanceField, PropertyField

class Board:
    def __init__(self, config):
        self.config = config
        self.fields = [None] * self.config.board_size
        self.initialize_board(
            self.config.tax_fields, 
            self.config.chance_fields,
            self.config.property_fields
            )
        

    def initialize_board(self, tax_fields=0, chance_fields=0, property_fields=0):

        position = 0

        # At the start of the board, we always have one StartField
        self.fields[0] = StartField(cash_amount=self.config.start_cash)
        position += 1
        
        for _ in range(tax_fields):
            self.fields[position] = TaxField(tax_amount=self.config.tax_amount) 
            position += 1

        for _ in range(chance_fields):
            self.fields[position] = ChanceField(chance_event=random.choice(self.config.chance_events))  
            position += 1

        property_names = [
            randomname.get_name(
                noun=( 'geography', 'houses', 'buildings', 'fast_food'), 
                seed=seed
                ).replace("-", " ").title() for seed in range(property_fields)]
        for property_name in property_names:
            property_price = self.config.property_price
            property_rent = self.config.property_rent
            self.fields[position] = PropertyField(property_name, property_price, property_rent)
            position += 1

        #Shuffling the fields except the first one (StartField)
        self.fields[1:] = random.sample(self.fields[1:], len(self.fields[1:]))

        
    def get_field(self, index):
        if 0 <= index < self.config.board_size:
            return self.fields[index]
        else:
            raise IndexError("Index out of bounds for board fields.")
        
    def set_field(self, index, field):
        if 0 <= index < self.config.board_size:
            self.fields[index] = field
        else:
            raise IndexError("Index out of bounds for board fields.")