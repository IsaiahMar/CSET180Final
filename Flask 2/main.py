import flask
from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify, flash
from sqlalchemy import *
from random import randint
from datetime import datetime, date
import time
import werkzeug 
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
conn_str = 'mysql://root:Cookiebear1@/180final'
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'secret key'

# Home page
@app.route('/', methods=['GET'])
def homepage():
    return render_template('home.html')

@app.route('/create_acc', methods=['POST'])
def create_account():
    first = request.form.get('first').lower()
    last = request.form.get('last').lower()
    username = request.form.get('username').lower()
    password = request.form.get('password')
    password_hash = generate_password_hash(password)
    email = request.form.get('email').lower()
    type = request.form.get('type').lower()
    
    conn.execute(text('INSERT INTO account (first, last, username, password, email, type) VALUES (:first, :last, :username, :password, :email, :type)'),
                 {'first': first, 'last': last, 'username': username, 'password': password_hash, 'email': email, 'type': type})
    conn.commit()
    return render_template("create_acc.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    account = conn.execute(text("SELECT * FROM account WHERE username = :username or email = :username"), {'username': username})
    user_data = account.fetchone()
    
    if user_data and check_password_hash(user_data[5], password):
        session['loggedin'] = True
        session['account_id'] = user_data[0]

        session['username'] = user_data[4]
        session['first'] = user_data[1]
        session['last'] = user_data[2]
        session['email'] = user_data[3]
        session['type'] = user_data[6]
        return render_template('home.html')  # Redirect to home page after successful login
    
    elif user_data and username == user_data[3] and password == user_data[5]:
        if user_data[6] == "admin":
            session['loggedin'] = True
            session['type'] = "admin"
            session['username'] = user_data[4]
            session['first'] = user_data[1]
            session['last'] = user_data[2]
            session ['email'] = user_data[3]
        elif user_data[6] == "vendor":
            session['loggedin'] = True
            session['type'] = "vendor"
            session['username'] = user_data[4]
            session['first'] = user_data[1]
            session['last'] = user_data[2]
            session ['email'] = user_data[3]
        elif user_data[6] == "customer":
            session['loggedin'] = True
            session['username'] = user_data[4] 
            session['type'] = "customer"
            session['username'] = user_data[4]
            session['first'] = user_data[1]
            session['last'] = user_data[2]
            session ['email'] = user_data[3]
    
    else:
        msg = 'Wrong username or password'
    return render_template('my_account.html', loggedin = True, account = account)


#button in heading
@app.route('/signout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        session['type'] = 'none'
        return render_template('create_acc.html')
    


#accounts page
@app.route('/my_account', methods= ['get', 'post'])
def my_account_page():
    if 'username' in session:
        username = session['username']
        account = conn.execute(text(f"SELECT * FROM account WHERE username = :username or email = :username"), {'username': username})
        user_data = account.fetchone()
        session['username'] = user_data[4]
        info = conn.execute(text('select * from account where username = username')), {'username': username}
        return render_template('my_account.html', info = info)
    else:
        return render_template('my_account.html')
    


#create product
@app.route('/create_products', methods=["GET"])
def new_products():
    return render_template('add_product.html')

@app.route('/create_products', methods=['POST'])
def post_products():
    if 'type' in session:
        account = conn.execute(text("SELECT * FROM account WHERE type = :type"), {"type": session['type']})
        user_data = account.fetchone()

        if user_data and (user_data[6] == 'vendor' or user_data[6] == 'admin'):
            title = request.form.get('title')
            description = request.form.get('description')
            warrenty_period = request.form.get('warrenty_period')
            category = request.form.get('category')
            inventory = request.form.get('inventory')
            username = session['username']

            result = conn.execute(text("INSERT INTO product (title, username, description, warranty_period, category, inventory) VALUES (:title, :username, :description, :warranty_period, :category, :inventory)"), 
                        {'title': title, 'description': description, 'warranty_period': warrenty_period, 'category' : category,  'username': username, 'inventory': inventory})
            result = conn.execute(text("SELECT LAST_INSERT_ID()"))
            product_id = result.fetchone()[0]
            conn.commit()     

            # Insert sizes into database
            sizes_input = request.form.get('sizes')
            sizes = [size.strip() for size in sizes_input.split(',')]
            for size in sizes:
                conn.execute(text('INSERT INTO size (product_id, size) VALUES (:product_id, :size)'), {'product_id': product_id, 'size': size})
                conn.commit()     

            # Insert colors into database
            colors_input = request.form.get('colors')
            colors = [color.strip() for color in colors_input.split(',')]
            for color in colors:
                conn.execute(text('INSERT INTO color (product_id, color) VALUES (:product_id, :color)'), {'product_id': product_id, 'color': color})
                conn.commit()     

            # Insert images into database
            images_input = request.form.get('images')
            images = [image.strip() for image in images_input.split(',')]
            for image in images:
                conn.execute(text('INSERT INTO image (product_id, image) VALUES (:product_id, :image)'), {'product_id': product_id, 'image': image})
                conn.commit() 

            #insert price into database
            current_price = request.form.get('price')
            conn.execute(text('INSERT INTO price (current_price, product_id) VALUES (:current_price, :product_id)'), {'current_price': current_price, 'product_id' :product_id})
            conn.commit()       

            return render_template('add_product.html')
        else:
            return 'Unauthorized access. You must be either a Vendor or an Admin to post products.'
    else:
        return 'Unauthorized access. Please log in first.'



#Edit has boat stuff, but shows on the page well
@app.route('/edit', methods=['GET', 'POST'])
def edit_products():
    if request.method == 'GET':
        if 'type' in session:
            if session['type'] == 'admin':
                edit_products = conn.execute(text('SELECT * FROM product')).fetchall()
                sizes = conn.execute(text('SELECT * FROM size')).fetchall()
                price = conn.execute(text('SELECT * FROM price')).fetchone()
                sizes = conn.execute(text('SELECT * FROM size')).fetchall()
                colors = conn.execute(text('SELECT * FROM color')).fetchall()
                images = conn.execute(text('SELECT * FROM image')).fetchall()
        
            elif session['type'] == 'vendor':
                username = session['username']
                edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username}).fetchall()
                sizes = conn.execute(text('SELECT * FROM size')).fetchall()
                price = conn.execute(text('SELECT * FROM price')).fetchone()
                sizes = conn.execute(text('SELECT * FROM size')).fetchall()
                colors = conn.execute(text('SELECT * FROM color')).fetchall()
                images = conn.execute(text('SELECT * FROM image')).fetchall()
        
            else:
                return 'Unauthorized access'

            return render_template('edit_product.html', edit_products=edit_products, sizes=sizes, colors=colors, images=images, price=price)

    elif request.method == 'POST':
        if 'type' in session:
            account = conn.execute(text("SELECT * FROM account WHERE type = :type"), {"type": session['type']})
            user_data = account.fetchone()

            if user_data and (user_data[6] == 'vendor' or user_data[6] == 'admin'):
                # Singular inputs
                product_id = request.form.get('product_id')
                title = request.form.get('title')
                description = request.form.get('description')
                warrenty_period = request.form.get('warrenty_period')
                category = request.form.get('category')
                inventory = request.form.get('inventory')
                username = session['username']

                conn.execute(text("UPDATE product SET title=:title, username=:username, description=:description, warranty_period=:warranty_period, category=:category, inventory=:inventory WHERE product_id=:product_id"), 
                            {'title': title, 'description': description, 'warrenty_period': warrenty_period, 'category': category, 'username': username, 'inventory': inventory, 'product_id': product_id})
                conn.commit()     

           
                conn.execute(text('DELETE FROM size WHERE product_id=:product_id'), {'product_id': product_id})
                conn.commit()

                conn.execute(text('DELETE FROM color WHERE product_id=:product_id'), {'product_id': product_id})
                conn.commit()

                sizes_input = request.form.get('sizes')
                sizes = [size.strip() for size in sizes_input.split(',')]
                for size in sizes:
                    conn.execute(text('INSERT INTO size (size, product_id) VALUES (:size, :product_id)'), {'size': size, 'product_id': product_id})
                    conn.commit()


                colors_input = request.form.get('colors')
                colors = [color.strip() for color in colors_input.split(',')]
                for color in colors:
                    conn.execute(text('INSERT INTO color (color, product_id) VALUES (:color, :product_id)'), {'color': color, 'product_id': product_id})
                    conn.commit()

                images_input = request.form.get('images')
                images = [image.strip() for image in images_input.split(',')]
                for image in images:
                    conn.execute(text('UPDATE image SET image=:image WHERE product_id=:product_id'), {'image': image, 'product_id': product_id})
                    conn.commit() 

                # Update price in the database
                current_price = request.form.get('price')
                conn.execute(text('UPDATE price SET current_price=:current_price WHERE product_id=:product_id'), {'current_price': current_price, 'product_id': product_id})
                conn.commit()  


                return render_template('edit_product.html', products=products)
            else:
                return 'Unauthorized access. You must be either a Vendor or an Admin to post products.'
        else:
            return 'Unauthorized access. Please log in first.'
        
#discounts
@app.route('/discount', methods=['GET', 'POST'])
def discount():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        current_price = request.form.get('current_price')
        new_price = request.form.get('new_price')
        time_left = request.form.get('time_left')

        # Ensure all form fields have been provided
        if product_id and current_price and new_price and time_left:
            # Update the price in the database
            conn.execute(text('UPDATE price SET new_price = :new_price, time_left = :time_left WHERE product_id = :product_id AND current_price = :current_price'), {'new_price': new_price, 'time_left': time_left, 'product_id': product_id, 'current_price': current_price})
            conn.commit()
            return render_template('edit_product.html')
        else:
            # Handle case where form fields are missing
            return "Form fields missing. Please fill in all fields and try again."
    
    return render_template('edit.html')

#delete products on delete product page
@app.route('/delete_product', methods=["GET"])
def delete_return():
    username = session.get('username') 
    title = request.form.get('title')
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': username})
    user_data = account.fetchone()
    
    if user_data:
        user_type = user_data[6] 
        if user_type == 'vendor': 
            edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username})
            return render_template('delete.html', edit_products=edit_products)
        elif user_type == 'admin':
            edit_products = conn.execute(text('SELECT * FROM product'))
            return render_template('delete.html')
    return "Unauthorized access"
   
@app.route('/delete_product', methods=["POST"])
def delete_return_post():
    if request.method == 'POST':
        username = session.get('username')
        account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"),{'username': username})
        user_data = account.fetchone()
        
        if user_data:
            user_type = user_data[6]
            if user_type == 'vendor':
                product_id = request.form.get('product_id')
                
                if product_id:
                    conn.execute(text("Set FOREIGN_KEY_CHECKS=0;"))
                    conn.commit()

                    conn.execute(text("DELETE FROM product WHERE product_id = :product_id AND username = :username"), {'product_id': product_id, 'username': username})
                    conn.commit()

                    conn.execute(text("DELETE FROM size WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()

                    conn.execute(text("DELETE FROM color WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()

                    conn.execute(text("DELETE FROM image WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()

                    conn.execute(text("DELETE FROM price WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()
                    conn.execute(text("Set FOREIGN_KEY_CHECKS=1;"))
                    conn.commit()
                    # Fetch the updated product list
                    edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username}).fetchall()
                    return render_template('delete.html', edit_products=edit_products)
                    
                
            elif user_type == 'admin':
                product_id = request.form.get('product_id')
                if product_id:
                    conn.execute(text("Set FOREIGN_KEY_CHECKS=0;"))
                    conn.commit()

                    conn.execute(text("DELETE FROM product WHERE product_id = :product_id "), {'product_id': product_id})
                    conn.commit()

                    conn.execute(text("DELETE FROM size WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()

                    conn.execute(text("DELETE FROM color WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()

                    conn.execute(text("DELETE FROM image WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()

                    conn.execute(text("DELETE FROM price WHERE product_id = :product_id"), {'product_id': product_id})
                    conn.commit()
                    conn.execute(text("Set FOREIGN_KEY_CHECKS=1;"))
                    conn.commit()
                    
                    edit_products = conn.execute(text('SELECT * FROM product ')).fetchall()
                    return render_template('delete.html', edit_products=edit_products)
                else:
                    return "Product ID not provided."
    return render_template('delete.html')


#ALL PROD PAGE
#display products
@app.route('/show_product', methods=["POST", "GET"])
def show_product_page():
    if request.method == 'GET':
        products = conn.execute(text('SELECT * FROM product')).fetchall()
        price = conn.execute(text('SELECT * FROM price')).fetchone()
        sizes = conn.execute(text('SELECT * FROM size')).fetchall()
        colors = conn.execute(text('SELECT * FROM color')).fetchall()
        images = conn.execute(text('SELECT * FROM image')).fetchall()
        return render_template('show_product.html', products=products, sizes=sizes, colors=colors, images = images, price=price)
    
    if request.method == 'POST':
        clicked_product_id = request.form['clicked_product_id']
        return render_template('individual_page.html', clicked_product_id=clicked_product_id)
            
# search bar product page
@app.route('/search', methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        product_search = request.form['product_search']
        products = conn.execute(text("SELECT * FROM product WHERE title LIKE :product_search or description LIKE :product_search or username LIKE :product_search"), {'product_search': f"%{product_search}%"})
        sizes = conn.execute(text('SELECT * FROM size')).fetchall()
        colors = conn.execute(text('SELECT * FROM color')).fetchall()
        images = conn.execute(text('SELECT * FROM image')).fetchall()
        if product_search != products:
            return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images = images)  
        return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images = images)
        
    #categories filter
@app.route('/categories', methods=["POST", "GET"])
def categories():
    if request.method == 'POST':
        product_search = request.form['category']
        products = conn.execute(text("SELECT * FROM product WHERE category LIKE :product_search"), {'product_search': f"%{product_search}%"})
        sizes = conn.execute(text('SELECT * FROM size')).fetchall()
        colors = conn.execute(text('SELECT * FROM color')).fetchall()
        images = conn.execute(text('SELECT * FROM image')).fetchall()
        if product_search != products:
            return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images = images)  
        return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images = images)
    #size filter
@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == "POST":
        conn.execute(text("insert into reviews (product_id, rating, description) values (:product_id, :rating, :desc)"), request.form)
        conn.commit()

        reviews = conn.execute(text("select * from reviews")).all()
        num_reviews = len(reviews)
        return render_template('review.html', reviews=reviews, num_reviews=num_reviews)

    reviews = conn.execute(text("select * from reviews")).all()
    num_reviews = len(reviews)
    return render_template('review.html', reviews=reviews, num_reviews=num_reviews)

#cart
@app.route('/cart', methods=['GET'])
def cart():
    products = conn.execute(text('SELECT * FROM product')).fetchall()
    price = conn.execute(text('SELECT * FROM price')).fetchall()
    sizes = conn.execute(text('SELECT * FROM size')).fetchall()
    colors = conn.execute(text('SELECT * FROM color')).fetchall()
    images = conn.execute(text('SELECT * FROM image')).fetchall()
    return render_template('cart.html', products=products, sizes=sizes, colors=colors, images = images, price=price)

@app.route('/cart', methods=['POST'])
def cartpage():
    clicked_product_id = request.form['clicked_product_id']
    product = conn.execute(text('SELECT * FROM product WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchone()
    cart_items = conn.execute(text('SELECT * FROM cart WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchall()


    cart_product_ids = [item[0] for item in cart_items]


    if 'cart' not in session:
        session['cart'] = []

    if clicked_product_id not in cart_product_ids:
        session['cart'].append(product)

    return render_template('cart.html', cart=session['cart'])

@app.route('/submit_order', methods=['POST'])
def submit_order():
    if request.method == 'POST':
        product_id = request.form['product_id']
        buyer_id = request.form['buyer_id']
        title = request.form['title']
        order_process = request.form['order_process']
        date = request.form['date']
        vendor = request.form['vendor']
        return f"Order submitted successfully for Product ID: {product_id}"
    else:
        return "Method Not Allowed"

@app.route('/sizes', methods=["POST", "GET"])
def sizes():
    if request.method == 'POST':
        product_search = request.form['sizes']
        products = conn.execute(text("SELECT * FROM product WHERE product_id IN (SELECT product_id FROM size WHERE size = :size)"), {'size': product_search} ).fetchall()
        sizes = conn.execute(text('SELECT * FROM size')).fetchall()
        colors = conn.execute(text('SELECT * FROM color')).fetchall()
        images = conn.execute(text('SELECT * FROM image')).fetchall()

        return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images=images)
    #color filter
@app.route('/colors', methods=["POST", "GET"])
def colors():
    if request.method == 'POST':
        product_search = request.form['colors']
        products = conn.execute(text("SELECT * FROM product WHERE product_id IN (SELECT product_id FROM color WHERE color = :color)"), {'color': product_search} ).fetchall()
        sizes = conn.execute(text('SELECT * FROM size')).fetchall()
        colors = conn.execute(text('SELECT * FROM color')).fetchall()
        images = conn.execute(text('SELECT * FROM image')).fetchall()
        return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images=images)

@app.route('/inventory', methods=["POST", "GET"])
def inventory():
    if request.method == 'POST':
        product_search = request.form['inventory']
        if product_search == '1':
            products = conn.execute(text("SELECT * FROM product WHERE inventory >= 1")).fetchall()
            sizes = conn.execute(text('SELECT * FROM size')).fetchall()
            colors = conn.execute(text('SELECT * FROM color')).fetchall()
            images = conn.execute(text('SELECT * FROM image')).fetchall()
            return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images=images)
        elif product_search == '0':
            products = conn.execute(text("SELECT * FROM product WHERE inventory = 0")).fetchall()
            sizes = conn.execute(text('SELECT * FROM size')).fetchall()
            colors = conn.execute(text('SELECT * FROM color')).fetchall()
            images = conn.execute(text('SELECT * FROM image')).fetchall()
            return render_template("show_product.html", products=products, sizes=sizes, colors=colors, images=images)
    else:
        return render_template("show_product.html")



@app.route('/individual', methods=["POST", "GET"])
def individual():
    if request.method == 'GET':
        clicked_product_id = request.args.get('clicked_product_id') 
        products = conn.execute(text('SELECT * FROM product WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchone()
        price = conn.execute(text('SELECT * FROM price WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchone()
        sizes = conn.execute(text('SELECT * FROM size WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchall()
        images = conn.execute(text('SELECT * FROM image WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchall()
        colors = conn.execute(text('SELECT * FROM color WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchall()
        return render_template('individual_page.html', products=products, price=price, sizes=sizes, images=images, colors=colors)

    if request.method == 'POST':
        clicked_product_id = request.form['clicked_product_id']
        products = conn.execute(text('SELECT * FROM product WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchone()
        price = conn.execute(text('SELECT * FROM price WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchone()
        sizes = conn.execute(text('SELECT * FROM size WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchall()
        images = conn.execute(text('SELECT * FROM image WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchall()
        colors = conn.execute(text('SELECT * FROM color WHERE product_id = :product_id'), {'product_id': clicked_product_id}).fetchall()
        return render_template('individual_page.html', products=products, price=price, sizes=sizes, images=images, colors=colors)




@app.route('/complaint', methods=["POST", "GET"])
def complaint():
    if request.method == 'GET':
        if 'username' in session:
            account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': session['username']})
            user_data = account.fetchone()
            if user_data:
                if user_data and user_data[6] == 'customer':
                    buyer_id = user_data[0]
                    orders = conn.execute(text('SELECT * FROM orders WHERE buyer_id = :buyer_id and order_process = "delivered"'), {'buyer_id': buyer_id}).fetchall()
                    return render_template('complaint.html', orders=orders)
                
                if user_data and user_data[6] == 'vendor':
                    product_id = text('select product_id from product')
                    orders = conn.execute(text('SELECT * from complaint where product_id = product_id ' ),{'product_id':product_id}).fetchall()
                    return render_template('complaint.html', orders=orders)

                if user_data and user_data[6] == 'admin':
                    orders = conn.execute(text('SELECT * FROM complaint')).fetchall()
                    return render_template('complaint.html', orders=orders)
                else:
                    return "User data not found."  
            else:
                return "User not logged in." 

    if request.method == 'POST':
        if 'type' in session:
            request_type = session.get('type')
            if request_type == 'customer':
                words = request.form.get('words')
                request_request =  request.form.get('request')
                product_id = request.form.get('product_id')
                if words and product_id:
                    account = conn.execute(text("SELECT * FROM account WHERE type = :type"), {"type": request_type})
                    user_data = account.fetchone()
                    username = session['username']
                    if user_data:
                        if user_data:
                            conn.execute(text("Set FOREIGN_KEY_CHECKS=0;"))
                            conn.commit()
                            conn.execute(
                                text("INSERT INTO complaint (complaint_username, date_issued, demand, product_id, title) VALUES (:username, :date, :demand, :product_id, :title)"),
                                {'username': username, 'date': date.today(), 'demand': words, 'product_id': product_id, 'title': request_request })
                            conn.commit()
                            conn.execute(text("Set FOREIGN_KEY_CHECKS=1;"))
                            conn.commit()
                            buyer_id = user_data[0]
                            orders = conn.execute(text('SELECT * FROM orders WHERE buyer_id = :buyer_id and order_process = "delivered"'), {'buyer_id': buyer_id}).fetchall()
                            return render_template('complaint.html', orders=orders)
                    else:
                        return "User not found or not a customer."
                else:
                    return "Incomplete form data."
            elif request_type == 'vendor':
                complaint_id = request.form.get('complaint_id')
                if complaint_id:
                    conn.execute(text("delete from complaint where complaint_id= :complaint_id"), {'complaint_id': complaint_id})
                    conn.commit()
                    orders = conn.execute(text('SELECT * FROM complaint WHERE complaint_process = :pending'), {'pending': 'pending'}).fetchall()
                    return render_template('complaint.html', orders=orders)
                
            elif request_type == 'admin':
                product_id = request.form.get('product_id')
                if product_id:
                    conn.execute(text("UPDATE complaint SET complaint_process = 'confirmed' WHERE product_id = :product_id AND complaint_process = 'pending'"), {'product_id': product_id})
                    conn.commit()
                    orders = conn.execute(text('SELECT * FROM complaint')).fetchall()
                    return render_template('complaint.html', orders=orders)
                
                else:
                    return "Incomplete form data."
            else:
                return "User type not recognized."
        else:
            return "User type not found in session."

    return render_template('complaint.html')

@app.route('/order_page', methods=["GET", "POST"])
def orders():
    if request.method == 'GET':
        if 'username' in session:
            account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': session['username']})
            user_data = account.fetchone()
            if user_data:
                buyer_id = user_data[0]
                if user_data[6] == 'vendor':
                    username = session['username']
                    orders = conn.execute(text('Select * from orders where vendor =:username '), {'username': username}).fetchall() 
                    return render_template('order_page.html', orders=orders)

                if user_data and user_data[6] == 'admin': 
                    orders = conn.execute(text('SELECT * FROM orders WHERE order_proccess = :order_proccess'), {'order_proccess': 'confirmed'}).fetchall() 
                    return render_template('order_page.html', orders=orders)
                
                if user_data and user_data[6] == 'customer':
                    orders = conn.execute(text('SELECT * FROM orders WHERE buyer_id = :buyer_id'), {'buyer_id': buyer_id}).fetchall() 
                    return render_template('order_page.html', orders=orders)
            else:
                return "User data not found."
        else:
            return "User not logged in." 

    if request.method == 'POST':
        if 'type' in session:
            request_type = request.form.get('request')
            words = request.form.get('words')
            product_id = request.form.get('product_id')
            if request_type and words and product_id:
                account = conn.execute(text("SELECT * FROM account WHERE type = :type"), {"type": session['type']})
                user_data = account.fetchone()
                if user_data and user_data[6] == 'vendor':
                    # Vendor updates order process to 'confirmed'
                    conn.execute(text("UPDATE orders SET order_process = :order_process WHERE product_id = :product_id"), {'order_process': 'confirmed', 'product_id': product_id})
                    conn.commit()
                    
                    return render_template('order_page.html')  # Redirect to order page after updating order process
                # elif user_data and user_data[6] == 'customer':

                # elif user_data and user_data[6] == 'admin':

                    pass
                else:
                    return "User is not a customer."  
            else:
                return "Incomplete form data." 
        else:
            return "User type not found in session."  

    return render_template('order_page.html')

@app.route('/confirm', methods=["GET", "POST"])
def confirmed():
    # Fetch user data
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': session['username']})
    user_data = account.fetchone()

    if user_data and user_data[6] == 'vendor':
        username = session['username']

        if request.method == 'GET':
            orders = conn.execute(text('SELECT * FROM orders WHERE vendor = :username'), {'username': username}).fetchall()
            return render_template('order_page.html', orders=orders)

        elif request.method == 'POST':
            order_id = request.form.get('order_id')
            if order_id:
                conn.execute(text("UPDATE orders SET order_process = 'confirmed' WHERE order_id = :order_id"), {'order_id': order_id})
                conn.commit()
                orders = conn.execute(text('SELECT * FROM orders WHERE vendor = :username'), {'username': username}).fetchall()
                return render_template('order_page.html', orders=orders)
            else:
                return "Product ID is missing. Please provide the product ID and try again."
    else:
        return "User data not found or user is not a vendor."

@app.route('/handed', methods=["GET", "POST"])
def handed():
    # Fetch user data
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': session['username']})
    user_data = account.fetchone()

    if user_data and user_data[6] == 'vendor':
        username = session['username']

        if request.method == 'GET':
            orders = conn.execute(text('SELECT * FROM orders WHERE vendor = :username'), {'username': username}).fetchall()
            return render_template('order_page.html', orders=orders)

        elif request.method == 'POST':
            order_id = request.form.get('order_id')
            if order_id:
                conn.execute(text("UPDATE orders SET order_process = 'handed to delivery partner' WHERE order_id = :order_id"), {'order_id': order_id})
                conn.commit()
                orders = conn.execute(text('SELECT * FROM orders WHERE vendor = :username'), {'username': username}).fetchall()
                return render_template('order_page.html', orders=orders)
            else:
                return "Product ID is missing. Please provide the product ID and try again."
    else:
        return "User data not found or user is not a vendor."

@app.route('/delivered', methods=["GET", "POST"])
def delivered():
    # Fetch user data
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': session['username']})
    user_data = account.fetchone()

    if user_data and user_data[6] == 'vendor':
        username = session['username']

        if request.method == 'GET':
            orders = conn.execute(text('SELECT * FROM orders WHERE vendor = :username'), {'username': username}).fetchall()
            return render_template('order_page.html', orders=orders)

        elif request.method == 'POST':
            order_id = request.form.get('order_id')
            if order_id:
                conn.execute(text("UPDATE orders SET order_process = 'delivered' WHERE order_id = :order_id"), {'order_id': order_id})
                conn.commit()
                orders = conn.execute(text('SELECT * FROM orders WHERE vendor = :username'), {'username': username}).fetchall()
                return render_template('order_page.html', orders=orders)
            else:
                return "Product ID is missing. Please provide the product ID and try again."
    else:
        return "User data not found or user is not a vendor."


@app.route('/reject', methods=["GET", "POST"])
def rejected():
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': session['username']})
    user_data = account.fetchone()
    if  request.method == 'POST':
        if user_data and user_data[6] == 'admin':
            product_id = request.form.get('product_id')
            if product_id:
                conn.execute(text("Set FOREIGN_KEY_CHECKS=0;"))
                conn.commit()
                conn.execute(text("delete from complaint where product_id = product_id"), {'product_id': product_id})
                conn.commit()
                conn.execute(text("Set FOREIGN_KEY_CHECKS=1;"))
                conn.commit()
                orders = conn.execute(text('SELECT * FROM complaint')).fetchall()
                return render_template('complaint.html', orders=orders)

     
if __name__ == '__main__':
    app.run(debug=True)

    