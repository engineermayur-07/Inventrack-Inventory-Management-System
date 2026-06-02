
import sqlite3
import datetime
 
def login(email=None,password=None):
      
    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()
    cursor.execute(" SELECT * FROM user WHERE email=? AND password=?",(email,password))
    user=cursor.fetchone()
    if(user):
        return True
    else :
        return False

def nearest_expiry(email=None,product_name=None):
    try:
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE user_email=? AND product_name=? ORDER BY expiry_date ASC",(email,product_name))
        batch=cursor.fetchone()
        conn.close()
        return batch

    except Exception as e:
        conn.close()
        return None

def add_batch(email=None,product_name=None,batch_no=None,quantity=None,expiry_date=None):
    try:
        expiry_date=datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        cursor.execute("INSERT INTO inventory(user_email,product_name,batch_no,quantity,expiry_date) Values(?,?,?,?,?)",(email,product_name,batch_no,quantity,expiry_date))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def sell_product(email=None,product_name=None,quantity=None):
    try:
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        quantities=quantity
        while quantities>0:
            batch=nearest_expiry(email,product_name)
            if batch:
                print(f"Batch found: {batch}")
                if(batch[4]<=quantities):
                    quantities=quantities-batch[4]
                    print(f"Quantity : {quantities}")
                    cursor.execute("DELETE FROM inventory WHERE user_email=? AND batch_no=? AND product_name=?",(email,batch[3],product_name))
                    conn.commit()
                    continue
                print(f"Quantity : {quantities}")
                cursor.execute("UPDATE inventory SET quantity=quantity-? WHERE user_email=? AND batch_no=? AND product_name=?",(quantities,email,batch[3],product_name))
                conn.commit()
                conn.close()
                quantities=0
                return True
            else:
                conn.close()
                return False
        return True
    except Exception as e:
        conn.close()
        return False




def get_expiring_stocks(email=None):
    try:
         
        today_date = datetime.date.today()
        thirty_days_later = today_date + datetime.timedelta(days=30)
        max_date_str = thirty_days_later.strftime('%Y-%m-%d')

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
        return None
    
 