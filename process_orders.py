import json
import sys

def process_orders(input_file):
    # Step 1: Read the orders from the input file
    with open(input_file, 'r') as file:
        orders = json.load(file)
    
    # Step 2: Initialize dictionaries to hold customer and item data
    customers = {}
    items = {}
    
    # Step 3: Process each order and collect necessary details
    for order in orders:
        # Extract customer details
        phone = order['phone']
        customer_name = order['customer_name']
        customers[phone] = customer_name
        
        # Extract item details and update the items dictionary
        item_name = order['item']
        price = order['price']
        
        if item_name not in items:
            items[item_name] = {'price': price, 'orders': 0}
        items[item_name]['orders'] += 1
    
    # Step 4: Write the customers data to customers.json
    with open('customers.json', 'w') as customers_file:
        json.dump(customers, customers_file, indent=4)
    
    # Step 5: Write the items data to items.json
    with open('items.json', 'w') as items_file:
        json.dump(items, items_file, indent=4)

if __name__ == "__main__":
    # Get the input file from the first positional argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <orders_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_orders(input_file)
