class Order:
    def __init__(self, order_id, customer):
        self.order_id = order_id
        self.customer = customer
        self.items = []

    def add_item(self, item_name, item_price):
        self.items.append((item_name, item_price))

    def total(self):
        return sum(price for item_name, price in self.items)