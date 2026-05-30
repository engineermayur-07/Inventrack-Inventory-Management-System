import sqlite3
def init_db():
    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXt NOT NULL,
        batch_no TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        expiry_date TEXT NOT NULL,
        )
    ''')