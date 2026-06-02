from flask import Flask, render_template, session, request, redirect, url_for
from auth import *
from database_setup import init_db

app = Flask(__name__)
app.secret_key = 'inventory_mayur_developer_2026'

 
init_db()

@app.route('/')
def home():
     
    if session.get('email'):
        return render_template('dashboard.html')
    else:
         
        return render_template('landing_page.html')
  
@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'GET':
        return render_template('login.html')  
     
    if request.method == 'POST':
         
        email = request.form.get('email')
        password = request.form.get('password')

         
        is_valid_user = login(email= email, password= password)

        if is_valid_user:
             
            session['email'] = email
            return redirect(url_for('home'))  
        else:
             
            return "Invalid email or password. Please go back and try again.", 401

@app.route('/add_batch',methods=['GET','POST'])
def add_batchs():
    if not session.get('email'):
        return render_template('landing_page.html')
    
    if request.method=='GET':
        return render_template('add.html')
    if request.method=='POST':
        email=session.get('email')
        batch_no=request.form.get('batch_no')
        product_name=request.form.get('product_name')
        quantity=int(request.form.get('quantity'))
        expiry_date=request.form.get('expiry_date')
        is_true=add_batch(email,product_name,batch_no,quantity,expiry_date)
        stock=get_expiring_stocks(email=email)
        if is_true:
            return redirect(url_for('home'))
        else:
            return "Error adding batch. Please go back and try again.", 500

@app.route('/sell_product', methods=['GET', 'POST'])
def sell_product_route():
    if not session.get('email'):
        return render_template('landing_page.html')
    
    if request.method=='GET':
        return render_template('sell.html')
    if request.method=='POST':
        email=session.get('email')
        product_name=request.form.get('product_name')
        quantity=int(request.form.get('quantity'))
        is_true=sell_product(email=email,product_name=product_name,quantity=quantity)
        if is_true:
            return redirect(url_for('home'))
        else:
            return "Error selling product. Please go back and try again.", 500    

@app.route('/get_expiring_stock')
def get_expiring_stock_route():
    if not session.get('email'):
        return render_template('landing_page.html')

    email = session.get('email')
    expiring_items = get_expiring_stocks(email=email)
    return render_template('dashboard.html', expiring_items=expiring_items)

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)