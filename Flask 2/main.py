import flask
from flask import Flask, render_template, request, redirect, url_for, abort, session
from sqlalchemy import create_engine, text
from random import randint

app = Flask(__name__)
conn_str = 'mysql://root:IMatornado$2023@localhost/180final'
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
        type = request.form.get('type')
        print(user_data)
        if user_data:
            if type == "Admin":
                session['loggedin'] = True
                session['type'] = "Admin"
                return redirect(url_for('admin_home'))
            elif username == "Vendor":
                session['loggedin'] = True
                session['type'] = "Vendor"
                return redirect(url_for('vendor_home'))
            elif password == user_data.password:
                session['loggedin'] = True
                session['Username'] = user_data.username
                session['Name'] = f"{user_data.first} {user_data.last}"
                msg = 'Login success!'
                print(session)
                print(username)
                return redirect(url_for('my_account_page'))
            else:
                msg = 'Wrong username or password'
        else:
            msg = 'User does not exist'
        
        return url_for('homepage', msg=msg)
    return render_template('my_account.html')

#button in heading
@app.route('/signout', methods = ['POST'])
def logout():
    session.clear()
    return redirect(url_for('homepage'))

@app.route('/admin_home')
def admin_home():
    if session.get('loggedin') and session.get('type') == "Admin":
        return "Welcome Admin!"
    else:
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
    first = request.form.get('first')
    last = request.form.get('last')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    conn.execute(text(
            'INSERT INTO account (first, last, username, password, email) VALUES (:first, :last, :username, :password, :email)'),
                     {'first': first, 'last': last, 'username': username, 'password': password , 'email': email})
    conn.commit()
    return url_for("show_newacc")


#Create Prodcuts

@app.route('/create_products', methods=['POST', 'GET'])
def post_products():
    if 'username' in session:
        account = conn.execute(text("SELECT * FROM account WHERE username = :username"), {"username": session['username']})
        user_data = account.fetchone()
        if user_data and (user_data['role'] == 'Vendor' or user_data['role'] == 'Admin'):
            if request.method == 'POST':
                conn.execute(text("INSERT INTO product (title, description, images, warranty_period, category, colors, sizes, inventory) VALUES (:title, :description, :images, :warranty_period, :category, :colors, :sizes, :inventory)"), request.form)
                conn.commit()
                return render_template('add_product.html')
            else:
                return 'Invalid request method. Only POST requests are allowed.'
        else:
            return 'Unauthorized access. You must be either a Vendor or an Admin to post products.'
    else:
        # return 'Unauthorized access. Please log in first.'
        return render_template('add_product.html')

#edit prodcuts
@app.route('/edit', methods=['GET'])
def edit():
    return render_template('edit_product.html')

@app.route('/edit', methods=['POST'])
def edit_products():
    upd = conn.execute(text("select * from product where product_id = :product_id"), request.form).all()
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


# @app.route('/my_account', methods=['GET'])
# def my_account():
#     user = session.get('user')
#     if user is None:
#         return redirect(url_for('login'))

#     account_info = conn.execute(text("SELECT * FROM accounts WHERE accountID = :accountID LIMIT 1"), {'user_id': user[0], 'accountID':  }).fetchone()
#     return render_template('my_account.html', info_type=account_info)

# @app.route('/my_account', methods=['GET', 'POST'])
# def my_account():
#     if request.method == 'GET':
#         all_accounts = conn.execute(text("SELECT * FROM accounts")).fetchone()
#         return render_template('my_account.html', info_type = all_accounts)
#     elif request.method == 'POST':
#         x = request.form['type']
#         account_info = conn.execute(text("SELECT * FROM accounts WHERE  = :type LIMIT 1"), {'type': x}).fetchone()
#         return render_template('my_account.html', info_type=account_info)
    
    
# @app.route('/deposit_money', methods=['GET', 'POST'])
# def send_money():
#     if request.method == "POST":
#         amounted = float(request.form['amount'])
#         account_num = int(request.form['accountNum'])
#         conn.execute(text(f'UPDATE accounts SET balance = balance + {amounted} where bank_number = {account_num}'),  {"amounted": amounted, "account_num": account_num} )
#         conn.commit()
#         return redirect("/deposit_money")
#     else:
#         return render_template("deposit_money.html")

# @app.route('/transfer', methods=['GET', 'POST'])
# def transfer_money():
#     if request.method == 'POST':
#         amount = float(request.form['amount'])
#         sender_bank_number = request.form['sender_bank_number']
#         receiver_bank_number = request.form['receiver_bank_number']
#         conn.execute(text("UPDATE accounts SET balance = balance - :amount WHERE bank_number = :bank_number"), {'amount': amount, 'bank_number': sender_bank_number})
#         conn.execute(text("UPDATE accounts SET balance = balance + :amount WHERE bank_number = :bank_number"), {'amount': amount, 'bank_number': receiver_bank_number})
#         conn.commit()
#         return render_template("transfer.html", message="Transfer successful")
#     else:
#         return render_template("transfer.html", message="Transfer failed! Make sure account numbers are correct.")
    
# # ADMIN PANEL
# # View pending accounts
# @app.route('/admin_dashboard', methods=['GET', 'POST'])
# def if_admin():
#     accounts = conn.execute(text('select * from pending_accounts')).all()
#     return render_template('admin_dashboard', account_info=accounts)


# @app.route('/accounts_page', methods=['GET', 'POST'])
# def account():
#     if request.method == 'GET':
#         all_accounts = conn.execute(text("SELECT * FROM accounts")).fetchall()
#         return render_template('accounts_page.html', info_type = all_accounts)
#     elif request.method == 'POST':
#         x = request.form['type']
#         account_info = conn.execute(text("SELECT * FROM accounts WHERE  = :type"), {'type': x}).fetchall()
#         return render_template('accounts_page.html', info_type=account_info)
    
# # Accept pending accounts
# @app.route('/accept', methods = ['GET', 'POST'])
# def accept():
#     if request.method == 'POST':
#         x = request.form['accept']
#         params = {"approval":'true', 'type' : x}
#         conn.execute(text(f"UPDATE accounts SET approved=:approval where accountID =  {x} ;"), params)
#         conn.commit()
#         bank_number = randint(0, 1000000000)
#         conn.execute(text("UPDATE accounts SET bank_number = :bank_number WHERE accountID = :account_id;"), {"bank_number": bank_number, "account_id": x})
#         conn.commit()
#         return redirect('/accounts_page')


if __name__ == '__main__':
    app.run(debug=True)