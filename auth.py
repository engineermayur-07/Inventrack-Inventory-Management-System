
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
        
def add_batch(email=None,product_name=None,batch_no=None,quantity=None,expiry_date=None):
    try:
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        cursor.execute("INSERT INTO inventory(user_email,product_name,batch_no,quantity,expiry_date) Values(?,?,?)",(email,product_name,batch_no,quantity,expiry_date))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def sell_product(email=None,product_name=None,quantity=None):
    try:
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        batch=nearest_expiry(email,product_name)
        if batch:
            if(batch[4]<quantity):
                quantity=quantity-batch[4]
                cursor.execute("DELETE FROM inventory WHERE user_email=? AND batch_no=? AND product_name=?",(email,batch[3],product_name))
            batch=nearest_expiry(email,product_name)
            cursor.execute("UPDATE inventory SET quantity=quantity-? WHERE user_email=? AND batch_no=? AND product_name=?",(quantity,email,batch[3],product_name))
            conn.commit()
            conn.close()
            return True
        else:
            return False
    except Exception as e:
        return False

def nearest_expiry(emmail=None,product_name=None):
    try:
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE user_email=? AND product_name=? ORDER BY expiry_date ASC",(email,product_name))
        batch=cursor.fetchone()
        conn.close()
        return batch

    except Exception as e:
        return None

def get_expiring_stocks(email=None):
    try:
        today_date=datetime.date.today()
        expiry_date=today_date+datetime.timedelta(days=30)
        month=int(expiry_date.month())
        day=int(expiry_date.day())
        year=int(expiry_date.year())

        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE user_email=? AND int(expiry_date.split('-')[0])<=?,int(expiry_date.split('-')[1])<=?,int(expiry_date.split('-')[2])<=?",(email,day,month,year))
        stocks=cursor.fetchall()
        conn.close()
        return stocks
    except Exception as e:
        return None
    
