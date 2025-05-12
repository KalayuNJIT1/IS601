import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

class Item(BaseModel):
    name: str
    price: float

class Customer(BaseModel):
    id: int
    name: str
    phone: str

class CustomerCreate(BaseModel):
    name: str
    phone: str

class Order(BaseModel):
    id:int
    timestamp:int
    name: str
    phone: str
    notes: str
    items : List[Item]
    
class ItemCreate(BaseModel):
    name:str
    price: float
    
class OrderCreate(BaseModel):
    name: str
    phone: str
    notes: str
    items : List[ItemCreate]

class OrderItem(BaseModel):
    name: str
    price: float
   

def get_db_connection():
    conn = sqlite3.connect("db.sqlite")
    conn.row_factory = sqlite3.Row
    return conn
#connection = sqlite3.connect("db.sqlite")
#cursor = connection.cursor()

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM items WHERE id=?;", (item_id,))
    item = result.fetchone()
    if item == None:
        raise HTTPException (status_code=404, detail= "item not found")
    return {
        "id": item[0],
        "name": item[1],
        "price" : item[2],
    }
    
    
@app.get("/customers/{customer_id}")
async def read_item(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM customers WHERE id=?;", (customer_id,))
    customer = result.fetchone()
    if customer == None:
        raise HTTPException (status_code=404, detail= "customer not found")
    return {
        "id": customer[0],
        "name": customer[1],
        "phone" : customer[2],
     }
    
@app.post("/items/")
async def create_item(item: Item):
    conn = get_db_connection()
    cursor = conn.cursor()
    name = item.name
    price = item.price
    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?);", (name, price))
    conn.commit()
    return {
        "id": cursor.lastrowid,
        "name": name,
        "price" : price,
    }

    
@app.post("/customers/")
async def create_customer(customer: Customer):
    conn = get_db_connection()
    cursor = conn.cursor()
    name = customer.name
    phone = customer.phone
    cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?);", (name, phone))
    conn.commit()
    return {
        "id": cursor.lastrowid,
        "name": name,
        "phone": phone,
    }

@app.delete("/items/{item_id}")
async def delete_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?;", (item_id,))
    conn.commit()
    if cursor.rowcount != 1:
        raise HTTPException (status_code=404, detail="item not found")
    return


@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id=?;", (customer_id,))
    conn.commit()
    if cursor.rowcount != 1:
        raise HTTPException (status_code=404, detail="item not found")
    return
        
@app.put("/items/{item_id}")
async def update_item(item_id, item: Item):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name=?, price=? WHERE id=?;", (item.name, item.price, item_id))
    conn.commit()
    return{
        "id": item_id,
        "name": item.name,
        "price": item.price,
    }
  
@app.put("/customers/{customer_id}")
async def update_customer(customer_id, customer: Customer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET name=?, phone=? WHERE id=?;", (customer.name, customer.phone, customer_id))
    conn.commit()
    return{
        "id": customer_id,
        "name": customer.name,
        "phone": customer.phone,
    
    }

@app.delete("/orders/{order_id}")
async def delete_customer(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id=?;", (order_id,))
    conn.commit()
    if cursor.rowcount != 1:
        raise HTTPException (status_code=404, detail="order not found")
    return

# Update order
@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, order_update: OrderCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if the order exists
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Find or create customer
    cursor.execute("SELECT id FROM customers WHERE name=? AND phone=?", (order_update.name, order_update.phone))
    customer = cursor.fetchone()
    if customer:
        cust_id = customer[0]
    else:
        cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (order_update.name, order_update.phone))
        cust_id = cursor.lastrowid

    # Update order with new customer ID and notes
    cursor.execute("UPDATE orders SET cust_id = ?, notes = ? WHERE id = ?", (cust_id, order_update.notes, order_id))

    # Remove existing items
    cursor.execute("DELETE FROM item_list WHERE order_id = ?", (order_id,))

    # Insert updated items
    for item in order_update.items:
        cursor.execute("SELECT id FROM items WHERE name=? AND price=?", (item.name, item.price))
        item_record = cursor.fetchone()
        if item_record:
            item_id = item_record[0]
        else:
            cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", (item.name, item.price))
            item_id = cursor.lastrowid
        cursor.execute("INSERT INTO item_list (order_id, item_id) VALUES (?, ?)", (order_id, item_id))

    conn.commit()

    # Retrieve updated order details
    cursor.execute("""
        SELECT orders.id, orders.timestamp, customers.name, customers.phone, orders.notes 
        FROM orders
        JOIN customers ON orders.cust_id = customers.id
        WHERE orders.id = ?
    """, (order_id,))
    updated_order = cursor.fetchone()
    
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")

    cursor.execute("""
        SELECT items.name, items.price
        FROM item_list
        JOIN items ON item_list.item_id = items.id
        WHERE item_list.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()

    order_items = [{"name": item[0], "price": item[1]} for item in items]

    return {
        "id": updated_order[0],
        "timestamp": updated_order[1],
        "name": updated_order[2],
        "phone": updated_order[3],
        "notes": updated_order[4],
        "items": order_items
    }

    
# get orders
@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get the order and customer
    cursor.execute("""
        SELECT orders.id, orders.timestamp, customers.name, customers.phone, orders.notes 
        FROM orders
        JOIN customers ON orders.cust_id = customers.id
        WHERE orders.id = ?
    """, (order_id,))
    order = cursor.fetchone()

    if order is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    # Get the items for the order
    cursor.execute("""
        SELECT items.name, items.price
        FROM item_list
        JOIN items ON item_list.item_id = items.id
        WHERE item_list.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()

    conn.close()

    order_items = [{"name": item["name"], "price": item["price"]} for item in items]

    return {
        "id": order["id"],
        "timestamp": order["timestamp"],
        "name": order["name"],
        "phone": order["phone"],
        "notes": order["notes"],
        "items": order_items
    }

@app.post("/order", response_model=Order)
async def create_order(order: OrderCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find or create customer
    cursor.execute("SELECT id FROM customers WHERE name=? AND phone=?", (order.name, order.phone))
    customer = cursor.fetchone()

    if customer:
        cust_id = customer["id"]
    else:
        cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?);", (order.name, order.phone))
        cust_id = cursor.lastrowid

    # Insert into orders table
    cursor.execute("INSERT INTO orders (cust_id, notes) VALUES (?, ?);", (cust_id, order.notes))
    order_id = cursor.lastrowid

    # Retrieve timestamp
    cursor.execute("SELECT timestamp FROM orders WHERE id=?;", (order_id,))
    row = cursor.fetchone()
    timestamp = row["timestamp"] if row else None

    # Insert items (create if not found)
    item_objs = []
    for item in order.items:
        cursor.execute("SELECT id FROM items WHERE name=? AND price=?", (item.name, item.price))
        item_row = cursor.fetchone()

        if item_row:
            item_id = item_row["id"]
        else:
            cursor.execute("INSERT INTO items (name, price) VALUES (?, ?);", (item.name, item.price))
            item_id = cursor.lastrowid

        cursor.execute("INSERT INTO item_list (order_id, item_id) VALUES (?, ?);", (order_id, item_id))
        item_objs.append({"name": item.name, "price": item.price})

    conn.commit()
    conn.close()

    return {
        "id": order_id,
        "timestamp": timestamp,
        "name": order.name,
        "phone": order.phone,
        "notes": order.notes,
        "items": item_objs
    }