class Field:
    def __init__(self, field_type):
        self.field_type = field_type

class StartField(Field):
    def __init__(self, cash_amount=200):
        self.cash_amount = cash_amount
        super().__init__("Start")

class TaxField(Field):
    def __init__(self,tax_amount):
        self.tax_amount = tax_amount
        super().__init__("Tax")

class ChanceField(Field):
    def __init__(self, chance_event):
        self.chance_event = chance_event
        super().__init__("Chance")

class PropertyField(Field):
    def __init__(self, name, price, rent):
        self.name = name
        self.price = price
        self.rent = rent
        self.is_owned = False
        super().__init__( "Property")

