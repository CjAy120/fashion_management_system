import sqlite3
import hashlib


def connect():
    return sqlite3.connect("fashion.db", timeout=5)

def hash_password(password: str) -> str:
    return hashlib.sha512(password.encode()).hexdigest()

def register_user(fullname, email, password):
    try:
        with connect() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",
                (fullname, email, hash_password(password))
            )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print("Error:", e)
        return False

def verify_user(userid, password):
    try:
        with connect() as db:
            cursor = db.cursor()
            query = "SELECT * FROM users WHERE (email=? OR fullname=?) AND password=?"
            values = (userid, userid, hash_password(password))
            cursor.execute(query, values)
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "fullname": row[1], "email": row[2]}
            return None
    except Exception as e:
        print("Error:", e)
        return None

def add_staff(name, contact, payment_status):
    try:
        with connect() as db:
            cursor = db.cursor()
            query = "INSERT INTO staff (staff_fullname, staff_contact, payment_status) VALUES (?, ?, ?)"
            values = (name, contact, payment_status)
            cursor.execute(query, values)
        return True
    except Exception as  e:
        print("Error:", e)
        return False

def add_customer(name,address,contact,gender):
    try:
        with connect() as db:
            cursor = db.cursor()
            query = "INSERT INTO customer (customer_fullname, contact, address, gender) VALUES (?, ?, ?, ?)"
            values = (name, contact, address, gender)
            cursor.execute(query, values)
        return True
    except Exception as e:
        print("Error", e)
        return False

def add_product(productName, description, brand, price, gender):
    try:
        with connect() as db:
            cursor = db.cursor()
            query = "INSERT INTO products (product_name, description, brand, product_price, gender) VALUES (?,?,?,?,?)"
            values = (productName, description, brand, price, gender)
            cursor.execute(query, values)
        return True
    except Exception as e:
        print("Error:", e)
        return False

def get_orders():
    try:
        with connect() as db:
            cursor = db.cursor()

            query = """
            SELECT 
                o.order_Id,
                p.product_name,
                c.customer_fullname,
                o.quantity,
                o.orderDate,
                o.status
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            JOIN customer c ON o.customer_id = c.customer_id
            """

            cursor.execute(query)
            return cursor.fetchall()

    except Exception as e:
        print("Error:", e)
        return []

def get_customer_names():
    try:
        with connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT customer_fullname FROM customer")
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print("Error:", e)
        return []

def get_product_names():
    try:
        with connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT product_name FROM products")
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print("Error:", e)
        return []

def get_customer_id_by_name(name):
    try:
        with connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT customer_id FROM customer WHERE customer_fullname=?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        print("Error:", e)
        return None

def get_product_id_by_name(name):
    try:
        with connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT product_id FROM products WHERE product_name=?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        print("Error:", e)
        return None

def add_orders(product_id, customer_id, quantity, date, status):
    try:
        with connect() as db:
            cursor = db.cursor()
            query = "INSERT INTO orders (product_id, customer_id, quantity, orderDate, status) VALUES (?,?,?,?,?)"
            values = (product_id, customer_id, quantity, date, status)
            cursor.execute(query, values)
        return True
    except Exception as e:
        print("Error:", e)
        return False

def get_staff_count():
    conn = sqlite3.connect("fashion.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM staff")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def get_customer_count():
    conn = sqlite3.connect("fashion.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customer")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def get_product_count():
    conn = sqlite3.connect("fashion.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def get_order_count():
    conn = sqlite3.connect("fashion.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]

    conn.close()
    return count
