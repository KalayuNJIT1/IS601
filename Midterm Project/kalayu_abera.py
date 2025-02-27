# this is my midterm project
#Kalayu Abera

#json file was imported
import json

#name passed as the first positional argument
with open ("example_orders.json") as f:
    json_data = json.load(f)

# dictionary created for order
new_dict = {}
for order in json_data:
    phone_number = order["phone"]
    name = order["name"]
    new_dict[phone_number] = name

# json file created for customer
with open("customers.json", 'w') as f:
    json.dump(new_dict, f, indent=2)
    
# another dictionary created 
new_dict2 = {}
for order in json_data:

    c_items = order["items"]
    #number of times it has been ordered
    for item in c_items:
        c_price = item["price"]
        c_name = item["name"]
        orders = 1
        if c_name in new_dict2:
           orders = new_dict2[c_name]["orders"]
           orders += 1
        new_dict2[c_name] = {
            "price": c_price,
            "orders": orders,
        }

# new json file created items
with open("items.json", 'w') as f:
    json.dump(new_dict2,f, indent=2)