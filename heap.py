import heapq
import datetime

 
user_heaps = {}   # Dictionary to store the heaps of then users with key = email

def clear_heap(email):
    """Resets the in-memory cache for a specific user."""
    global user_heaps
    user_heaps[email] = []



def push_batch(email, item_id, product_name, batch_no, quantity, expiry_date_str):
    """
    Converts the expiry string into a date object and pushes it onto 
    the specific user's private Min-Heap.
    """
    global user_heaps
    if email not in user_heaps:
        user_heaps[email] = []
        
    expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    
    
    heap_element = (expiry_date, item_id, product_name, batch_no, quantity)
    
    heapq.heappush(user_heaps[email], heap_element)



def get_nearest_expiry(email, product_name):
    """
    Searches the logged-in user's private heap to find their absolute oldest 
    batch matching the requested product name.
    """
    global user_heaps
    if email not in user_heaps or not user_heaps[email]:
        return None
        
    matching_batches = []
    
     
    for element in user_heaps[email]:
        if element[2].lower() == product_name.lower():
            matching_batches.append(element)
            
    if not matching_batches:
        return None
        
    return min(matching_batches, key=lambda x: x[0])



def load_from_db(email):
    """
    Query SQLite on server startup, pull active items for this specific user,
    and build their unique memory Min-Heap structure.
    """
    import sqlite3
    clear_heap(email)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, batch_no, quantity, expiry_date FROM inventory WHERE user_email=?", (email,))
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        push_batch(
            email=email,
            item_id=row[0],
            product_name=row[1],
            batch_no=row[2],
            quantity=row[3],
            expiry_date_str=row[4]
        )
    print(f" Successfully cached {len(user_heaps[email])} batches into the Min-Heap for {email}.")