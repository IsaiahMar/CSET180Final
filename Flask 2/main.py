import flask
from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify, flash
from sqlalchemy import *
from random import randint
from datetime import datetime
import time

app = Flask(__name__)
conn_str = 'mysql://root:Cookiebear1@/180final'
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'secret key'

# Home page
@app.route('/', methods=['GET'])
def homepage():
    return render_template('home.html')

# Login & logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        account = conn.execute(text(f"SELECT * FROM account WHERE username = :username or email = :username"), {'username': username})
        user_data = account.fetchone()
    
        if user_data and username == user_data[4] and password == user_data[5]:
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
        print(info)
        return render_template('my_account.html', info = info)
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
        'INSERT INTO account (first, last, username, password, email, type) VALUES (:first, :last, :username, :password, :email, :type)'),
                    {'first': first, 'last': last, 'username': username, 'password': password , 'email': email, 'type': type})
    conn.commit()
    return render_template("create_acc.html")


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
            # Singular inputs
            title = request.form.get('title')
            description = request.form.get('description')
            warranty_period = request.form.get('warranty_period')
            category = request.form.get('category')
            inventory = request.form.get('inventory')
            username = session['username']

            # # Check if required fields are present
            # if not all([title, description, category, price, inventory]):
            #     flash('Please fill in all required fields', 'error')
            #     return redirect(url_for('new_products'))

            # # Check for duplicate product
            # duplicate_product = conn.execute(text("SELECT * FROM product WHERE username = :username AND title = :title"), {'username': username, 'title': title}).fetchone()
            # if duplicate_product:
            #     flash('This product already exists', 'error')
            #     return redirect(url_for('new_products'))

            # Insert product into database
            result = conn.execute(text("INSERT INTO product (title, username, description, warranty_period, category, inventory) VALUES (:title, :username, :description, :warranty_period, :category, :inventory)"), 
                        {'title': title, 'description': description, 'warranty_period': warranty_period, 'category' : category,  'username': username, 'inventory': inventory})
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
            elif session['type'] == 'vendor':
                username = session['username']
                edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username}).fetchall()
            else:
                return 'Unauthorized access'

            return render_template('edit_product.html', edit_products=edit_products)
        #discounts
            # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    elif request.method == 'POST':
        if 'type' in session:
            account = conn.execute(text("SELECT * FROM account WHERE type = :type"), {"type": session['type']})
            user_data = account.fetchone()

            if user_data and (user_data[6] == 'vendor' or user_data[6] == 'admin'):
                # Singular inputs
                product_id = request.form.get('product_id')
                title = request.form.get('title')
                description = request.form.get('description')
                warranty_period = request.form.get('warranty_period')
                category = request.form.get('category')
                inventory = request.form.get('inventory')
                username = session['username']

                # # Check if required fields are present
                # if not all([title, description, category, price, inventory]):
                #     flash('Please fill in all required fields', 'error')
                #     return redirect(url_for('new_products'))

                # # Check for duplicate product
                # duplicate_product = conn.execute(text("SELECT * FROM product WHERE username = :username AND title = :title"), {'username': username, 'title': title}).fetchone()
                # if duplicate_product:
                #     flash('This product already exists', 'error')
                #     return redirect(url_for('new_products'))

                # Insert product into database
                conn.execute(text("UPDATE product SET title=:title, username=:username, description=:description, warranty_period=:warranty_period, category=:category, inventory=:inventory WHERE product_id=:product_id"), 
                            {'title': title, 'description': description, 'warranty_period': warranty_period, 'category': category, 'username': username, 'inventory': inventory, 'product_id': product_id})
                conn.commit()     

                # Update sizes in the database
                sizes_input = request.form.get('sizes')
                sizes = [size.strip() for size in sizes_input.split(',')]
                for size in sizes:
                    print (size)
                    conn.execute(text('UPDATE size SET size=:size WHERE product_id=:product_id'), {'size': size, 'product_id': product_id})
                    conn.commit()   
                conn.execute(text('delete from size where WHERE product_id=:product_id and size != size'), {'size': size, 'product_id': product_id})
                conn.commit()   


                # Update colors in the database
                colors_input = request.form.get('colors')
                colors = [color.strip() for color in colors_input.split(',')]
                for color in colors:
                    conn.execute(text('UPDATE color SET color=:color WHERE product_id=:product_id'), {'color': color, 'product_id': product_id})
                    conn.commit()     

                # Update images in the database
                images_input = request.form.get('images')
                images = [image.strip() for image in images_input.split(',')]
                for image in images:
                    conn.execute(text('UPDATE image SET image=:image WHERE product_id=:product_id'), {'image': image, 'product_id': product_id})
                    conn.commit() 

                # Update price in the database
                current_price = request.form.get('price')
                conn.execute(text('UPDATE price SET current_price=:current_price WHERE product_id=:product_id'), {'current_price': current_price, 'product_id': product_id})
                conn.commit()  


                return render_template('edit_product.html')
            else:
                return 'Unauthorized access. You must be either a Vendor or an Admin to post products.'
        else:
            return 'Unauthorized access. Please log in first.'
        
                    # conn.execute(text('UPDATE size SET size=:size WHERE product_id=:product_id'), {'size': size, 'product_id': product_id})
#discounts
@app.route('/discount', methods=['GET', 'POST'])
def discount():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        current_price = request.form.get('current_price')
        new_price = request.form.get('new_price')
        time_left = request.form.get('time_left')

    conn.execute(text('UPDATE price SET new_price=:new_price, time_left=:time_left WHERE product_id=:product_id AND current_price=:current_price'),{'time_left': time_left, 'new_price': new_price, 'product_id': product_id, 'current_price': current_price})
    conn.commit()
    return render_template('edit_product.html')

#delete products on delete product page
@app.route('/delete_product', methods=["GET"])
def delete_return():
   if request.method == 'GET':
    username = session.get('username') 
    account = conn.execute(text("SELECT * FROM account WHERE username = :username OR email = :username"), {'username': username})
    user_data = account.fetchone()
    
    if user_data:
        user_type = user_data[6] 
        if user_type == 'vendor': 
            edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username})
            return render_template('delete.html', edit_products=edit_products)
        elif user_type == 'admin':
            edit_products = conn.execute(text('SELECT * FROM product'))
            return render_template('delete.html', edit_products=edit_products)
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
                    conn.execute(text("DELETE FROM product WHERE product_id = :product_id AND username = :username"),{'product_id': product_id, 'username': username})
                    conn.commit()
                    conn.execute(text("Set FOREIGN_KEY_CHECKS=1;"))
                    conn.commit()
                    edit_products = conn.execute(text('SELECT * FROM product WHERE username = :username'), {'username': username}).fetchall()
                    return render_template('delete.html', edit_products=edit_products)
                else:
                    return "Product ID not provided."
            
            elif user_type == 'admin':
                product_id = request.form.get('product_id')
                if product_id:
                    conn.execute(text("Set FOREIGN_KEY_CHECKS=0;"))
                    conn.commit()
                    conn.execute(text("DELETE FROM product WHERE product_id = :product_id"),{'product_id': product_id})
                    conn.commit()
                    conn.execute(text("Set FOREIGN_KEY_CHECKS=1;"))
                    conn.commit()
                    edit_products = conn.execute(text('SELECT * FROM product')).fetchall()
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
        price = conn.execute(text('SELECT * FROM price')).fetchall()
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


@app.route('/individual', methods=["POST", "GET"])
def individual():
    if request.method == 'GET':
        clicked_product_id = request.args.get('clicked_product_id')
        # print(clicked_product_id) 
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
      render_template('complaint.html')


if __name__ == '__main__':
    app.run(debug=True)

    