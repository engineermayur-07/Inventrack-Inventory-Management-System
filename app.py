from flask import  *
from auth import *
from database_setup import init_db
import datetime
from heap import *
import sqlite3  
from inventory_management import *
from sms import *
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-fallback-key')
 

init_db()

@app.after_request
def add_header(response):
    """
    Forces the user's browser to download a fresh copy of the page 
    from the server instead of reading a dead snapshot from the local cache.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



def get_expiry_context():
    """Returns today's date strings used for expiry comparison in templates."""
    today = datetime.date.today()
    warn_date    = today + datetime.timedelta(days=10)    
    caution_date = today + datetime.timedelta(days=30)    
    return {
        'today_date'        : today.strftime('%Y-%m-%d'),
        'expiry_warn_date'  : warn_date.strftime('%Y-%m-%d'),
        'expiry_caution_date': caution_date.strftime('%Y-%m-%d'),
    }


@app.route('/')
def home():
    if session.get('email'):
        email         = session.get('email')
        load_from_db(email)
        inventory     = get_all_inventory(email=email)    
        expiring_items = get_expiring_stocks(email=email)
        ctx           = get_expiry_context()
        return render_template(
            'dashboard.html',
            inventory      = inventory,
            expiring_items = expiring_items,
            **ctx
        )
    return render_template('landing_page.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        
        print("In register function")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = ?",(email,))
        is_already_registered = cursor.fetchall()
        if( is_already_registered ) :
            flash("Email already registered.\n Go to log in.",'danger')
            conn.commit()
            conn.close()

        else : 
            otp = generate_otp()
            
            
            session['temp_user'] = {
                'email': email,
                'password': password,
                'name': name,
                'otp': otp,
                'mobile' : mobile
            }
            
            if send_otp_email(email, otp, name):
                flash("An OTP has been sent to your email. Please verify. Check your spam folder. Our emails are usually in spam folder.", "info")
                return redirect(url_for('verify_otp_page'))

            else:
                flash("Error sending OTP email. Please try again.", "danger")
            
    return render_template('register.html')



@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    
    print("in verify otp function")
    if 'temp_user' not in session:
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_entered_otp = request.form.get('otp')
        temp_data = session['temp_user']
        
         
        if user_entered_otp == temp_data['otp']:
             
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO user (email, password, name, mobile) VALUES (?, ?, ?, ?)", 
                    (temp_data['email'], temp_data['password'], temp_data['name'], temp_data['mobile'])
                )
                conn.commit()
                conn.close()
            

                is_registered = send_registration_alert(temp_data['name'], temp_data['email'])
                 

                flash("Registration successful! You can now log in.", "success")
                session.pop('temp_user', None)

                return redirect(url_for('login_route'))
            except Exception as e:
                flash("Database error occurred, contact developer", "danger")
                print(e)
        else:
             
            flash("Invalid OTP code. Please look closely and try again.", "danger")
            
    return render_template('verify_otp.html')



@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'GET':
        return render_template('login.html')

    email    = request.form.get('email')
    password = request.form.get('password')

    if login(email=email, password=password):
        session['email'] = email
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Invalid email or password. Please try again.")



@app.route('/add_batch', methods=['GET', 'POST'])
def add_batchs():
    if not session.get('email'):
        return redirect(url_for('login_route'))

    if request.method == 'GET':
        return render_template('add.html')

    email        = session.get('email')
    batch_no     = request.form.get('batch_no')
    product_name = request.form.get('product_name')
    quantity     = int(request.form.get('quantity'))
    expiry_date  = request.form.get('expiry_date')

    if add_batch(email, product_name, batch_no, quantity, expiry_date):
        return redirect(url_for('home'))
    return render_template('error_add.html', error = "Error adding batch. Ensure you enter unique batch id/no. Please go back and try again.")


@app.route('/sell_product', methods=['GET', 'POST'])
def sell_product_route():
    if not session.get('email'):
        return redirect(url_for('login_route'))

    if request.method == 'GET':
        return render_template('sell.html')

    email        = session.get('email')
    product_name = request.form.get('product_name')
    quantity     = int(request.form.get('quantity'))

    if sell_product(email=email, product_name=product_name, quantity=quantity):
        return redirect(url_for('home'))
    return render_template('error_sell.html', error = "Error selling batch. Please go back and try again.")


@app.route('/get_expiring_stock')
def get_expiring_stock_route():
    if not session.get('email'):
        return redirect(url_for('login_route'))

    email          = session.get('email')
    inventory      = get_all_inventory(email=email)
    expiring_items = get_expiring_stocks(email=email)
    ctx            = get_expiry_context()
    return render_template(
        'dashboard.html',
        inventory      = inventory,
        expiring_items = expiring_items,
        **ctx
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


 

if __name__ == '__main__':
    app.run(debug=True)
