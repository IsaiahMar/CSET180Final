import flask
from flask import Flask, render_template, request, redirect, url_for, abort, session
from sqlalchemy import create_engine, text
from random import randint

app = Flask(__name__)
conn_str = 'mysql://root:Cookiebear1@/180final'
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'secret key'


# Home page
@app.route('/', methods=['GET'])
def homepage():
    return render_template('base.html')


# Login & logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        account = conn.execute(text(f"SELECT * FROM account WHERE username = :username or email = :username"), {'username': username})
        user_data = account.fetchone()
       

        if user_data:
            if user_data[6] == "admin":
                session['loggedin'] = True
                session['type'] = "admin"
                session['username'] = user_data[4]
                return render_template('my_account.html')
            elif user_data[6] == "vendor":
                session['loggedin'] = True
                session['type'] = "vendor"
                session['username'] = user_data[4]
                return render_template('my_account.html')
            elif password == user_data['password']:
                session['loggedin'] = True
                session['username'] = user_data['username']
                session['Name'] = f"{user_data['first']} {user_data['last']}"
                return render_template('my_account.html')
            else:
                msg = 'Wrong username or password'
                return render_template('my_account.html')
        else:
            msg = 'User does not exist'
            return render_template('my_account.html')
    else:
       return render_template('my_account.html')



#button in heading
@app.route('/signout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        session['type'] = 'none'
        return render_template('create_acc.html')
        

@app.route('/admin_home')
def admin_home():
    if session.get('loggedin') and session.get('type') == "Admin":
        return "Welcome Admin!"
    else:
        return redirect(url_for('login'))

#accounts page
@app.route('/my_account', methods= ['get', 'post'])
def my_account_page():
    if 'username' in session:
        return render_template('my_account.html', username = session['username'])
    else:
        return render_template('create_acc.html')
    
@app.route('/create_acc', methods=['GET'])
def show_newacc():
    return render_template('create_acc.html')
#create/ register account 
@app.route('/create_acc', methods=['POST'])
def create_account():
    if request.method == 'POST':
        first = request.form.get('first').lower()
        last = request.form.get('last').lower()
        username = request.form.get('username').lower()
        password = request.form.get('password').lower()
        email = request.form.get('email').lower()
        type = request.form.get('type').lower()
        conn.execute(text(
            'INSERT INTO account (first, last, username, password, email,type) VALUES (:first, :last, :username, :password, :email, :type)'),
                     {'first': first, 'last': last, 'username': username, 'password': password , 'email': email, 'type': type})
        conn.commit()
        return render_template("create_acc.html")
    else:
        return render_template('create_acc.html')


#Create Prodcuts

@app.route('/create_products', methods=['GET', 'POST'])
def post_products():
    if 'type' in session :
        account = conn.execute(text("SELECT * FROM account WHERE type = :type"), {"type": session['type']})
        user_data = account.fetchone()
        if user_data and (user_data[6] == 'vendor' or user_data[6] == 'admin'):
                if request.method == 'POST':
                    title = request.form['title']
                    description = request.form['description']
                    images = request.form['images']
                    warrenty_period = request.form['warrenty_period']
                    category = request.form['category']
                    colors = request.form['colors']
                    sizes = request.form['sizes']
                    inventory = request.form['inventory']
                    
                    conn.execute(text("INSERT INTO product (title, description, images, warrenty_period, category, colors, sizes, inventory) VALUES (:title, :description, :images, :warrenty_period, :category, :colors, :sizes, :inventory)"), 
                                {'title': title, 'description': description, 'images': images, 'warrenty_period': warrenty_period, 'category': category, 'colors': colors, 'sizes': sizes, 'inventory': inventory})
                    conn.commit()
                    return render_template('add_product.html')
                else:
                    return render_template('add_product.html')
        else:
            return 'Unauthorized access. You must be either a Vendor or an Admin to post products.'
    else:
        return 'Unauthorized access. Please log in first.'

# @app.route('/my_account', methods=['GET', 'POST'])
# def my_account_page():
#     if 'Username' in session:  # Change 'username' to 'Username'
#         return render_template('my_account.html', username=session['Username'])
#     else:
#         return redirect(url_for('login'))


#Edit has boat stuff, but shows on the page well
@app.route('/edit', methods=['GET','POST'])
def edit_products():
    if request.method == 'GET':
        edit_products = conn.execute(text('select * from product'))
        return render_template('edit_product.html', edit_products = edit_products)
    if request.method == 'POST':
        product_id = request.form['product_id']
        upd = conn.execute(text("select * from product where product_id = :product_id"), request.form).all()
        conn.execute(text("update product set title=:title, description=:description, images=:images, warrenty_period=:warrenty_period,  category=:category, colors=:colors, sizes=:sizes, inventory=:inventory where product_id=:product_id"), request.form)
        conn.commit()
        if not upd:
            return render_template('edit_product.html', search_info="Does not exist")
        edit_products = conn.execute(text('select * from product'))
        return render_template('edit_product.html', edit_products = edit_products)

#delete products


@app.route('/delete_product', methods=["POST", "GET"])
def delete_return():
     if request.method == 'GET':
            edit_products = conn.execute(text('select * from product'))
            return render_template('delete.html', edit_products = edit_products)
     if request.method == 'POST':
        sear = conn.execute(text("select * from product where product_id = :product_id"), request.form).all()
        conn.execute(text("delete from product where product_id = :product_id"), request.form)
        conn.commit()
        edit_products = conn.execute(text('select * from product'))
        return render_template('delete.html', edit_products = edit_products)
     return render_template('delete.html')

#display products
@app.route('/show_product', methods=["POST", "GET"])
def show_product_page():
        if request.method == 'GET':
            products = conn.execute(text('select * from product'))
            return render_template('show_product.html', products = products)
            # if request.method == 'POST':



# search
@app.route('/search', methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        product = conn.execute(text("select * from product where productid = :product_search"), request.form)
        return render_template("search.html", product=product)
        


if __name__ == '__main__':
    app.run(debug=True)

    