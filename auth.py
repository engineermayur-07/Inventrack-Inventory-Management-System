
import sqlite3


 
 
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

def sell_product(email=None,product_name=None):
    try:
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()

    except Exception as e:
        return False