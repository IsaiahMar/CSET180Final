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
        account = conn.execute(text(f"SELECT * FROM account WHERE username = \'{username}\'"))
        user_data = account.fetchone()
        
        if user_data:
            if username == "Admin":
                session['loggedin'] = True
                return redirect(url_for('admin_home'))
            elif username == "Vendor":
                session['loggedin'] = True
                return redirect(url_for('vendor_home'))
            elif password == user_data.password:
                session['loggedin'] = True
                session['Username'] = user_data.username
                session['Name'] = f"{user_data.first} {user_data.last}"
                msg = 'Login success!'
                print(session)
                return redirect(url_for('login'))
            else:
                msg = 'Wrong username or password'
        else:
            msg = 'User does not exist'
        
        return url_for('homepage', msg=msg)
    return render_template('my_account.html')

#button in heading
@app.route('/signout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))

#accounts page
@app.route('/my_account', methods= ['get', 'post'])
def my_account_page():
    if 'Username' in session:
        return render_template('my_account.html', username = session['Username'])
    else:
        return redirect(url_for('login'))
    
@app.route('/create_acc', methods=['GET'])
def show_newacc():
    return render_template('create_acc.html')
#create/ register account 
@app.route('/create_acc', methods=['POST'])
def create_account():
    if request.method == 'POST':
        first = request.form.get('first')
        last = request.form.get('last')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        conn.execute(text(
            'INSERT INTO account (first, last, username, password, email) VALUES (:first, :last, :username, :password, :email)'),
                     {'first': first, 'last': last, 'username': username, 'password': password , 'email': email})
        conn.commit()
        return render_template("create_acc.html")
    else:
        return render_template('create_acc.html')


#Create Prodcuts

@app.route('/create_products', methods=['POST', 'GET'])
def post_products():
    if 'username' in session:
        account = conn.execute(text("SELECT * FROM account WHERE username = :username"), {"username": session['username']})
        user_data = account.fetchone()
        if user_data and (user_data['username'] == 'Vendor' or user_data['username'] == 'Admin'):
                if request.method == 'POST':
                    title = request.form['title']
                    description = request.form['description']
                    images = request.form['images']
                    warranty_period = request.form['warranty_period']
                    category = request.form['category']
                    colors = request.form['colors']
                    sizes = request.form['sizes']
                    inventory = request.form['inventory']
                    
                    conn.execute(text("INSERT INTO product (title, description, images, warranty_period, category, colors, sizes, inventory) VALUES (:title, :description, :images, :warranty_period, :category, :colors, :sizes, :inventory)"), 
                                {'title': title, 'description': description, 'images': images, 'warranty_period': warranty_period, 'category': category, 'colors': colors, 'sizes': sizes, 'inventory': inventory})
                    conn.commit()
                    return render_template('add_product.html')
                else:
                    return 'Invalid request method. Only POST requests are allowed.'
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



#edit prodcuts
@app.route('/edit', methods=['GET'])
def edit():
    return render_template('edit_product.html')

@app.route('/edit', methods=['POST'])
def edit_products():
    upd = conn.execute(text("select * from product`  where product_id = :product_id"), request.form).all()
    if not upd:
        return render_template('update.html', search_info="Does not exist")
    conn.execute(text("update boat set name=:name, type=:type, owner_id=:owner_id, rental_price=:rental_price where id=:id"), request.form)
    conn.commit()
    return render_template('edit_product.html', search_info=upd[0:])

#delete products


@app.route('/delete_product', methods=["POST", "GET"])
def delete_return():
     if request.method == 'POST':
        sear = conn.execute(text("select * from product where product_id = :product_id"), request.form).all()
        if not sear:
            return render_template('delete.html', search_info="Does not exist")
        conn.execute(text("delete from product where product_id = :product_id"), request.form)
        conn.commit()
        return render_template('delete.html', search_info=sear[0:])
     return render_template('delete.html')

#
@app.route('/show_product', methods=["POST", "GET"])
def show_product_page():
        products = conn.execute(text('select * from product'))
        return render_template('show_product.html', products = products)


#search
# @app.route('/search', methods=["POST", "GET"])
# def search():
#     if request.method == 'POST':
#         product = conn.execute(text("select * from product where productid = :product_search"), request.form)
#         return render_template("search.html", product=product)
        


if __name__ == '__main__':
    app.run(debug=True)