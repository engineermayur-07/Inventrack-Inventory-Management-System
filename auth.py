import sqlite3
import datetime

def login(email=None, password=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return bool(user)

def nearest_expiry(email=None, product_name=None):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM inventory WHERE user_email=? AND product_name=? ORDER BY expiry_date ASC",
            (email, product_name)
        )
        batch = cursor.fetchone()
        conn.close()
        return batch
    except Exception:
        conn.close()
        return None

def add_batch(email=None, product_name=None, batch_no=None, quantity=None, expiry_date=None):
    try:
        product_name = product_name.upper().strip()
        expiry_date  = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory(user_email, product_name, batch_no, quantity, expiry_date) VALUES(?,?,?,?,?)",
            (email, product_name, batch_no, quantity, expiry_date)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def sell_product(email=None, product_name=None, quantity=None):
    try:
        product_name = product_name.upper().strip()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        remaining = quantity

        while remaining > 0:
            batch = nearest_expiry(email, product_name)
            if not batch:
                conn.close()
                return False

            if batch[4] <= remaining:
                remaining -= batch[4]
                cursor.execute(
                    "DELETE FROM inventory WHERE user_email=? AND batch_no=? AND product_name=?",
                    (email, batch[3], product_name)
                )
                conn.commit()
            else:
                cursor.execute(
                    "UPDATE inventory SET quantity=quantity-? WHERE user_email=? AND batch_no=? AND product_name=?",
                    (remaining, email, batch[3], product_name)
                )
                conn.commit()
                remaining = 0

        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def get_all_inventory(email=None):
    """Returns all inventory rows for the user, ordered by expiry date ascending."""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM inventory WHERE user_email=? ORDER BY expiry_date ASC",
            (email,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        conn.close()
        print(f"Error in get_all_inventory: {e}")
        return []

def get_expiring_stocks(email=None):
    """Returns inventory items expiring within 30 days."""
    try:
        today          = datetime.date.today()
        thirty_days    = today + datetime.timedelta(days=30)
        max_date_str   = thirty_days.strftime('%Y-%m-%d')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM inventory WHERE user_email=? AND expiry_date <= ? ORDER BY expiry_date ASC",
            (email, max_date_str)
        )
        stocks = cursor.fetchall()
        conn.close()
        return stocks
    except Exception as e:
        conn.close()
        print(f"Error in get_expiring_stocks: {e}")
        return []
