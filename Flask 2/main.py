import flask
from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify
from sqlalchemy import *
from random import randint


app = Flask(__name__)
conn_str = 'mysql://root:IMatornado$2023@/180final'
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'secret key'


# Home page
@app.route('/', methods=['GET'])
def homepage():
    return render_template('base.html')
@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        account = conn.execute(text("SELECT * FROM account WHERE username = :username or email = :username"), {'username': username})
        user_data = account.fetchone()

        if user_data:
            if user_data[6] == "admin":
                session['loggedin'] = True
                session['type'] = "admin"
                session['username'] = user_data[4]
                return render_template('my_account.html', loggedIn=session['loggedin'])
            
            elif user_data[6] == "vendor":
                session['loggedin'] = True
                session['type'] = "vendor"
            elif password == user_data[5]:
                session['loggedin'] = True
                session['username'] = user_data[4]
                session['Name'] = f"{user_data[1]} {user_data[2]}"
            else:
                msg = 'Wrong password'
        else:
            msg = 'User does not exist'
    else:
        msg = 'Method not allowed'

    # Render the login page if the login attempt failed or if the method was not POST
    return render_template('login.html')

# Login & logout
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         account = conn.execute(text(f"SELECT * FROM account WHERE username = :username or email = :username"), {'username': username})
#         user_data = account.fetchone()
        

#         if user_data:
#             if user_data[6] == "admin":
#                 session['loggedin'] = True
#                 session['type'] = "admin"
#             elif user_data[6] == "vendor":
#                 session['loggedin'] = True
#                 session['type'] = "vendor"
#             elif password == user_data[5]:
#                 session['loggedin'] = True
#                 session['username'] = user_data[4] 
#                 session['Name'] = f"{user_data[1]} {user_data[2]}"
#         else:
#             msg = 'Wrong username or password'
#     else:
#         msg = 'User does not exist'

#     return render_template('my_account.html')




#button in heading
@app.route('/signout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        session['type'] = 'none'
        return render_template('create_acc.html')
        
#ADMIN HOMe is it being used??!
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
        return render_template('my_account.html')
    
#CREATE ACCOUNT GET
@app.route('/create_acc', methods=['GET'])
def show_newacc():
    return render_template('create_acc.html')
#CREATE  ACCOUNT POST
@app.route('/create_acc', methods=['POST'])
def create_account():
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

@app.route('/create_products', methods=["GET"])
def new_products():
    if 'create_product_error' in session:
        prod_error = session['create_product_error']
    else:
        prod_error = null
    return render_template('add_product.html', prod_error = prod_error)
#Create Prodcuts

@app.route('/create_products', methods=['POST'])
def post_products():
    if 'type' in session :
        account = conn.execute(text("SELECT * FROM account WHERE type = :type"), {"type": session['type']})
        
        user_data = account.fetchone()
        print(user_data[-1])
        if user_data and (user_data[6] == 'Vendor' or user_data[6] == 'admin'):
                    title = request.form['title']
                    description = request.form['description']
                    warrenty_period = request.form['warrenty_period']
                    VendorID = request.form['VendorID']
                    category = request.form['category']
                    inventory = request.form['inventory']
                    if(title == "" or description == "" or category == ""):
                        session['create_product_error'] = 'Fields are empty!'
                        return render_template('add.product.html')
                    duplicate_product = conn.execute(text('SELECT * FROM product WHERE VendorID = :VendorID AND title = :title'), 
                                      {'VendorID': VendorID, 'title': title}).fetchall()
                    if len(duplicate_product) > 0:
                        session['create_product_error'] = 'This already exists!'
                        return render_template('add_product.html')
                        
                    else:
                        print("Not a duplicate")
                        conn.execute(text("INSERT INTO product (title, VendorID, description, warrenty_period, category, inventory) VALUES (:title, :VendorID, :description, :warrenty_period, :category, :inventory)"), 
              {'title': title, 'VendorID': VendorID, 'description': description, 'warrenty_period': warrenty_period, 'category': category, 'inventory': inventory})
                        return render_template('add_product.html')
                    
                    # product_select = conn.execute(text(f'select product_id from product where title = :title and VendorID = :VendorID'))
                    # conn.execute(text(f'Insert Into product_details ()from product where title = :title and VendorID = :VendorID'))
                    
        else:
            return 'Unauthorized access. You must be either a Vendor or an Admin to post products.'
    else:
        return 'Unauthorized access. Please log in first.'


#Edit has boat stuff, but shows on the page well
@app.route('/edit', methods=['GET','POST'])
def edit_products():
    if request.method == 'GET':
        edit_products = conn.execute(text('SELECT * FROM product')).fetchall()
        return render_template('edit_product.html', edit_products=edit_products)
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        sizes = ['S', 'M', 'L', 'XL', 'XXL', '3XL']
        conn.execute(text("UPDATE product_details SET title=:title, description=:description, images=:images, warrenty_period=:warrenty_period, category=:category, colors=:colors, sizes=:sizes, inventory=:inventory WHERE product_id=:product_id"), request.form)
        conn.commit()
        edit_products = conn.execute(text('SELECT * FROM product')).fetchall()
        return render_template('edit_product.html', edit_products=edit_products, sizes=sizes)
    

#delete products


@app.route('/delete_product', methods=["GET"])
def delete_return():
   if request.method == 'GET':
    username = session.get('username')  # Retrieve username from session
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': username})
    user_data = account.fetchone()
    
    if user_data:
        user_type = user_data[6] 
        if user_type == 'vendor' and username == user_data[1]: 
            edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username})
            return render_template('delete.html', edit_products=edit_products)
        elif user_type == 'admin':
            edit_products = conn.execute(text('SELECT * FROM product'))
            return render_template('delete.html', edit_products=edit_products)
    return "Unauthorized access"
   
@app.route('/delete_product', methods=["POST"])
def delete_return_post():
    if request.method == 'POST':
        username = session.get('username')  # Retrieve username from session
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': username})
    user_data = account.fetchone()
    
    if user_data:
        user_type = user_data[6] 
        if user_type == 'vendor' and username == user_data[1]: 
            edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username})
            # sear = conn.execute(text("SELECT * FROM product WHERE product_id = :product_id"), request.form).all()
            conn.execute(text("DELETE FROM product WHERE product_id = :product_id"), request.form)
            conn.commit()
            edit_products = conn.execute(text('SELECT * FROM product'))
            return render_template('delete.html', edit_products=edit_products)
        elif user_data[6] == 'admin':
            edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username})
            return render_template('delete.html', edit_products=edit_products)

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
        product_search = request.form['product_search']
        type = session[6]
        products = (text("SELECT * FROM account WHERE username LIKE :product_search and " ), {'product_search': f"%{product_search}%"})
        if product_search != products:
            return render_template("show_product.html", products=products)  
        # else: 
        #     products = conn.execute(text("SELECT * FROM product WHERE title LIKE :product_search or description LIKE :product_search"), {'product_search': f"%{product_search}%"})
        return render_template("show_product.html", products=products)
 

        # products = conn.execute(text("SELECT * FROM account WHERE account_id LIKE :product_search"), {'product_search': f"%{product_search}%"})
        # or description LIKE '%:product_search%' or description LIKE '%:product_search%'
       
        


if __name__ == '__main__':
    app.run(debug=True)

    