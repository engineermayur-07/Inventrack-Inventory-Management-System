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

@app.route('/add_batch')
def add_batch():
    if not session.get('email'):
        return render_template('landing_page.html')
    
    if request.method=='GET':
        return render_template(add.html)
    if request.method=='POST':
        batch_no=request.form.get('batch_no')
        product_name=request.form.get('product_name')
        quantity=request.form.get('quantity')
        expiry_date=request.form.get('expiry_date')
        


if __name__ == '__main__':
    app.run(debug=True)