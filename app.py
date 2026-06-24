from flask import Flask, render_template, session, request, redirect, url_for
from auth import *
from database_setup import init_db
import datetime
from heap import *

app = Flask(__name__)
app.secret_key = 'inventory_mayur_developer_2026'

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


@app.after_request
def clear_browser_cache(response):
    """
    Forces the browser to destroy its local history cache for this app.
    This stops the user from using back/forward arrows to view logged-out pages.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

    
if __name__ == '__main__':
    app.run(debug=True)
