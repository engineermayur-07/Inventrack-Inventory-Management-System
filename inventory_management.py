import sqlite3
import datetime
from heap import *
from auth import *
from datetime import datetime


def add_batch(email=None, product_name=None, batch_no=None, quantity=None, expiry_date=None):
    """
    Adds the product batch to the database. Ensures unique batch Id.
    """

    conn = sqlite3.connect('database.db')
    try:
        product_name = product_name.upper().strip()
        expiry_date  = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute(" SELECT * FROM inventory WHERE batch_no = ?  ", (batch_no))
        is_batchno_available = cursor.fetchone()

        if(is_batchno_available) :
            return False

        cursor.execute(
            "INSERT INTO inventory(user_email, product_name, batch_no, quantity, expiry_date) VALUES(?,?,?,?,?)",
            (email, product_name, batch_no, quantity, expiry_date)
        )
        conn.commit()
        conn.close()
        load_from_db(email)  # Update the user's heap after adding a new batch
        return True
    except Exception:
        conn.close()
        return False



def sell_product(email=None, product_name=None, quantity=None):
    """
    Gets the early expiring batch. Deletes the batch if quantity is more than
    the quantity in the batch and then updates the quantity of next expiring batch
    by subtract from quantity. Else update the quantity of expiring batch.
    re 
    """
    try:
        product_name = product_name.upper().strip()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        remaining = quantity

        while remaining > 0:
            batch = get_nearest_expiry( email, product_name)
            if not batch:
                conn.close()
                return False

            today = datetime.date.today()
            today = today.strftime("%Y-/%m-/%d")
            if batch[5] < today :
                return False

            if batch[4] <= remaining:
                remaining = remaining - batch[4]
                cursor.execute(
                    "DELETE FROM inventory WHERE user_email=? AND batch_no=? AND product_name=?",
                    (email, batch[3], product_name)
                )
                conn.commit()
                load_from_db(email)  # Update the user's heap after deleting a batch
            else:
                cursor.execute(
                    "UPDATE inventory SET quantity=quantity-? WHERE user_email=? AND batch_no=? AND product_name=?",
                    (remaining, email, batch[3], product_name)
                )
                conn.commit()
                remaining = 0

        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.commit()
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
