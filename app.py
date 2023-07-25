from flask import Flask, render_template, request, url_for, redirect, session, jsonify, flash
import sqlite3

## creating users database with sqlite
conn1 = sqlite3.connect('users.db')
cursor1 = conn1.cursor()

## crearting users table to store User/Admin credentials
cursor1.execute('''
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT NOT NULL
    )
''')
                
cursor1.execute('''
    CREATE TABLE IF NOT EXISTS admins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT NOT NULL
    )
''')


conn1.commit()
conn1.close()    


## Creating database to store Product Info
conn2 = sqlite3.connect('grocery_store.db')
cursor2 = conn2.cursor()

cursor2.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        unit TEXT NOT NULL,
        expiry_date DATE,
        image_path TEXT,
        quantity INTEGER NOT NULL,
        category_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
''')

conn2.commit()
conn2.close()


## Creating database to store categories
conn2 = sqlite3.connect('grocery_store.db')
cursor2 = conn2.cursor()

cursor2.execute('''
    CREATE TABLE IF NOT EXISTS category (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

conn2.commit()
conn2.close()

## Creating database to store cart 
conn3 = sqlite3.connect('cart.db')
cursor3 = conn3.cursor()

cursor3.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        admin_id INTEGER,
        product_id INTEGER,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        unit TEXT NOT NULL,
        image_path TEXT,
        quantity INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
''')

conn3.commit()
conn3.close()

## Creating database to store cart 
conn4 = sqlite3.connect('orders.db')
cursor4 = conn4.cursor()

cursor4.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        admin_id INTEGER,
        product_id INTEGER,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        unit TEXT NOT NULL,
        image_path TEXT,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
''')

conn4.commit()
conn4.close()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

# db connection function for users-db
def get_db_connection():
    conn1 = sqlite3.connect('users.db')
    conn1.row_factory = sqlite3.Row
    return conn1

# db connection function for store-db
def get_store_db_connection():
    conn2 = sqlite3.connect('grocery_store.db')
    conn2.row_factory = sqlite3.Row
    return conn2


# route for Home Page
@app.route('/')
def home():
    return render_template('home.html')

## User registration route
@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        conn1 = get_db_connection()
        cursor1 = conn1.cursor()

        # Check if username already exist
        cursor1.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor1.fetchone() is not None:
            # return "Username already exists"
            return redirect('/user/login')
        
        #Insert new user into database
        cursor1.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'user'))
        conn1.commit()

        conn1.close()

       # Registration successful, redirect to login page
        return redirect('/user/login')
        
    return render_template('user_register.html')

## User login route
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn1 = get_db_connection()
        cursor1 = conn1.cursor()

        # Check if credentials are valid
        cursor1.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor1.fetchone()

        if user is not None:
            # User login successfully, store user info in session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            conn1.close()

            #Redirect to user dashboard
            return redirect('/user/dashboard')
        else:
            # Invalid credentials or user not exist
            conn1.close()
            return "Invalid credentials or user not exist"
    return render_template('user_login.html')

## Admin Register route
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')

            
            conn1 = get_db_connection()
            cursor1 = conn1.cursor()

            # Check if username already exist
            cursor1.execute('SELECT * FROM admins WHERE username = ?', (username,))
            if cursor1.fetchone() is not None:
                return redirect('/admin/login')

        
            #Insert new admin into database
            cursor1.execute('INSERT INTO admins (username, password, role) VALUES (?, ?, ?)', (username, password, 'admin'))
            conn1.commit()

            conn1.close()

            # Registration successful, redirect to login page
            return redirect('/admin/login')
        return render_template('admin_register.html')

## Admin Login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn1 = get_db_connection()
        cursor1 = conn1.cursor()

        # Check if credentials are valid
        cursor1.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
        admin = cursor1.fetchone()

        if admin is not None:
            # User login successfully, store user info in session
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_role'] = admin['role']

            conn1.close()

            #Redirect to admin dashboard
            return redirect('/admin/dashboard')
        else:
            # Invalid credentials or admin not exist
            conn1.close()
            return "Invalid credentials or admin not exist"
    return render_template('admin_login.html')

## Logout route
@app.route('/logout')
def logout():
    # Clear the session and remove user authentication
    session.clear()

    # Redirect to Home Page
    return redirect('/')

## function to retrieve user id
def get_user_id(username):
    conn2 = sqlite3.connect('users.db')
    cursor2 = conn2.cursor()
    
    
    cursor2.execute('SELECT id FROM users WHERE username=?', (username,))
    result = cursor2.fetchone()
    
    if result:
        currentId = result[0]
        return currentId
    else:
        return None
    
## function to retrieve admin id
def get_admin_id(username):
    conn2 = sqlite3.connect('users.db')
    cursor2 = conn2.cursor()

    cursor2.execute('SELECT id FROM admins WHERE username=?', (username,))
    result = cursor2.fetchone()

    if result:
        currentId = result[0]
        return currentId
    else:
        return None

## User Dashboard route
@app.route('/user/dashboard', methods=['GET'])
def user_dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect('/user/login')
    
    if 'username' not in session:
        return redirect('/user/login')
    
    username = session['username']
    user_id = get_user_id(username=username)

    if user_id:
        # coonect to db
        conn2 = get_store_db_connection()
        cursor2 = conn2.cursor()
        
        # Retrieving product data
        cursor2.execute('SELECT * FROM products ORDER BY created_at DESC')
        products = cursor2.fetchall()

        # Retrieving category data
        cursor2.execute('SELECT * FROM category')
        categories = cursor2.fetchall()

        cursor2.execute('SELECT c.id, c.name, p.id AS product_id, p.name AS product_name, p.price, p.unit, p.expiry_date, p.image_path, p.quantity '
                        'FROM category c '
                        'LEFT JOIN products p ON c.id = p.category_id '
                        'ORDER BY c.id'
                        )
        data = cursor2.fetchall()

        conn2.close()

        # Create a dictionary to store products grouped by category
        products_category = {}

        for item in data:
            category_id = item['id']
            category_name = item['name']
            product_id = item['product_id']
            product_name = item['product_name']
            price = item['price']
            unit = item['unit']
            expiry_date = item['expiry_date']
            image_url = item['image_path']
            quantity = item['quantity']
        
            # Add products to the respective category in the dictionary
            if category_id not in products_category:
                products_category[category_id] = {'name': category_name, 'products' : []}

            products_category[category_id]['products'].append([
                product_id,
                product_name,
                price,
                unit,
                expiry_date,
                image_url,
                quantity
            ])

        #Display user dashboard
        return render_template('user_dashboard.html', products_category=products_category, products=products, role='user', categories=categories, id=user_id)

    else:
        return redirect(url_for('user_login'))


## Admin Dashboard route
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    # Check if admin is logged in
    if 'admin_id' not in session:
        return redirect('/admin/login')
    
    if 'admin_username' not in session:
        return redirect('/admin/login')
    
    username = session['admin_username']
    print('Username:', username)
    admin_id = get_admin_id(username=username)
    print('admin_id:', admin_id)


    if admin_id:    
        # coonect to db
        conn2 = get_store_db_connection()
        cursor2 = conn2.cursor()
        
        # Retrieving product data
        cursor2.execute('SELECT * FROM products ORDER BY created_at DESC')
        products = cursor2.fetchall()

        # Retrieving category data
        cursor2.execute('SELECT * FROM category')
        categories = cursor2.fetchall()

        cursor2.execute('SELECT c.id, c.name, p.id AS product_id, p.name AS product_name, p.price, p.unit, p.expiry_date, p.image_path, p.quantity '
                        'FROM category c '
                        'LEFT JOIN products p ON c.id = p.category_id '
                        'ORDER BY c.id'
                        )
        data = cursor2.fetchall()

        conn2.close()

        # Create a dictionary to store products grouped by category
        products_category = {}

        for item in data:
            category_id = item['id']
            category_name = item['name']
            product_id = item['product_id']
            product_name = item['product_name']
            price = item['price']
            unit = item['unit']
            expiry_date = item['expiry_date']
            image_url = item['image_path']
            quantity = item['quantity']
        
            # Add products to the respective category in the dictionary
            if category_id not in products_category:
                products_category[category_id] = {'name': category_name, 'products' : []}

            products_category[category_id]['products'].append([
                product_id,
                product_name,
                price,
                unit,
                expiry_date,
                image_url,
                quantity
            ])

            #Display user dashboard
        return render_template('admin_dashboard.html', products_category=products_category, products=products, role='admin', categories=categories, id=admin_id)

    else:
        return redirect(url_for('admin_login'))



## CRUD OPERATIONS FOR PRODUCT

## create route for Add product form
@app.route('/admin/add_product_form')
def addProductForm():
     # coonect to db
    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

     # Retrieving category data
    cursor2.execute('SELECT * FROM category')
    categories = cursor2.fetchall()

    conn2.close()
    
    return render_template('add_product_form.html', categories=categories)


## function for add products -- POST/CREATE API for Product 
@app.route('/admin/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    price = float(request.form.get('price'))
    unit = request.form.get('unit')
    expiry_date = request.form.get('expiry_date')
    image_url = request.form.get('image_url')
    quantity = int(request.form.get('quantity'))
    category_id = request.form.get('category')

    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

    cursor2.execute('INSERT INTO products (name, price, unit, expiry_date, image_path, quantity, category_id) VALUES (?, ?, ?, ?, ?, ?, ?)', (name, price, unit, expiry_date, image_url, quantity, category_id))

    conn2.commit()
    conn2.close()

    return redirect('/admin/dashboard')


# create route for edit product form -- GET/READ API for Product
@app.route('/product/edit/<int:product_id>', methods=['GET'])
def edit_product_form(product_id): 
    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

    cursor2.execute('SELECT * FROM category')
    categories = cursor2.fetchall()

    # Retrieve the product from the database
    cursor2.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor2.fetchone()

    conn2.close()

    return render_template('edit_product.html', product=product, categories=categories)

# route to handle product edit -- PUT/UPDATE API for Product
@app.route('/product/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    name = data.get('name')
    price = data.get('price')
    unit = data.get('unit')
    expiry_date = data.get('expiry_date')
    image_url = data.get('image_url')
    quantity = data.get('quantity')
    category_id = data.get('category_id')

    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

    #Update product details in database
    cursor2.execute('UPDATE products SET name=?, price=?, unit=?, expiry_date=?, image_path=?, quantity=?, category_id=? WHERE id = ?', (name, price, unit, expiry_date, image_url, quantity, category_id, product_id))
    conn2.commit()

    cursor2.execute('SELECT * FROM category')
    categories = cursor2.fetchall()

    # Retrieve the product from the database
    cursor2.execute('SELECT * FROM products')
    products = cursor2.fetchall()

        
    conn2.close()

    return render_template('admin_dashboard.html', products=products, categories=categories)


#route for deleting product -- DELETE API for Product
@app.route('/product/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

    # Delete product from database
    cursor2.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn2.commit()

    conn2.close()
    
    return jsonify({'message' : 'Product deleted'})


## CRUD OPERATIONS FOR CATEGORY

## create route for Add category form
@app.route('/admin/add_category')
def addCategoryForm():
    return render_template('add_category_form.html')


## function for add category -- POST/CREATE API for Category
@app.route('/category/add', methods=['POST'])
def add_category():
    name = request.form.get('category')
    
     # coonect to db
    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

    cursor2.execute('INSERT INTO category (name) VALUES (?)', (name,))

    conn2.commit()
    conn2.close()

    return redirect('/admin/dashboard')

## route for edit category form -- GET/READ for category
@app.route('/admin/edit_category_form/<int:category_id>', methods=['GET'])
def editCategoryForm(category_id):
    # coonect to db
    conn2 = sqlite3.connect('grocery_store.db')
    cursor2 = conn2.cursor()

    # Retrieving category data
    cursor2.execute('SELECT * FROM category WHERE id = ?', (category_id,))
    category = cursor2.fetchone()

    return render_template('edit_category.html', category=category)


# route to update category -- PUT/UPDATE API for Category
@app.route('/category/update/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.get_json()
    updated_name = data.get('name')

     # coonect to db
    conn2 = sqlite3.connect('grocery_store.db')
    cursor2 = conn2.cursor()

    # Retrieve the product from the database
    cursor2.execute('SELECT * FROM products')
    products = cursor2.fetchall()

    # Retrieving category data
    cursor2.execute('UPDATE category SET name = ? WHERE id = ?', (updated_name, category_id))
    conn2.commit()

    cursor2.execute('SELECT * FROM category')
    categories = cursor2.fetchall()

    conn2.close()

    return render_template('admin_dashboard.html', products=products, categories=categories)


# route to delete category -- DELETE API for category
@app.route('/category/delete/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    # coonect to db
    conn2 = sqlite3.connect('grocery_store.db')
    cursor2 = conn2.cursor()

    cursor2.execute('SELECT * FROM products WHERE category_id = ?', (category_id,))
    products = cursor2.fetchall()

    for product in products:
        product_id = product[0]
        delete_product(product_id=product_id)

    cursor2.execute('DELETE FROM category WHERE id = ?', (category_id,))
    conn2.commit()

    conn2.close()

    return jsonify({'message': 'Category Deleted Successfully!!'})

## function to get category specific product -- for user
@app.route('/user/category_product/<int:category_id>')
def user_product_by_category(category_id):
    unique_category_id = category_id
    # coonect to db
    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()
    
    # Retrieving product data
    cursor2.execute('SELECT * FROM products')
    products = cursor2.fetchall()

    # Retrieving category data
    cursor2.execute('SELECT * FROM category')
    categories = cursor2.fetchall()

    cursor2.execute('SELECT c.id, c.name, p.id AS product_id, p.name AS product_name, p.price, p.unit, p.expiry_date, p.image_path, p.quantity '
                    'FROM category c '
                    'LEFT JOIN products p ON c.id = p.category_id '
                    'ORDER BY c.id'
                    )
    data = cursor2.fetchall()

    conn2.close()

    # Create a dictionary to store products grouped by category
    products_category = {}

    for item in data:
        category_id = item['id']
        category_name = item['name']
        product_id = item['product_id']
        product_name = item['product_name']
        price = item['price']
        unit = item['unit']
        expiry_date = item['expiry_date']
        image_url = item['image_path']
        quantity = item['quantity']
    
        # Add products to the respective category in the dictionary
        if category_id not in products_category:
            products_category[category_id] = {'name': category_name, 'products' : []}

        products_category[category_id]['products'].append([
            product_id,
            product_name,
            price,
            unit,
            expiry_date,
            image_url,
            quantity
        ])
    
        selected_products = []
        category_ids = products_category.keys()

        if unique_category_id in category_ids:
            selected_catefory_name = products_category[unique_category_id]['name']
            selected_products = products_category[unique_category_id]['products']
    return render_template('user_product_by_category.html', products=selected_products, category_name=selected_catefory_name, categories=categories, role='user')

    
## function to get category specific product -- for admin
@app.route('/admin/category_product/<int:category_id>')
def admin_product_by_category(category_id):
    unique_category_id = category_id
    # coonect to db
    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()
    
    # Retrieving product data
    cursor2.execute('SELECT * FROM products')
    products = cursor2.fetchall()

    # Retrieving category data
    cursor2.execute('SELECT * FROM category')
    categories = cursor2.fetchall()

    cursor2.execute('SELECT c.id, c.name, p.id AS product_id, p.name AS product_name, p.price, p.unit, p.expiry_date, p.image_path, p.quantity '
                    'FROM category c '
                    'LEFT JOIN products p ON c.id = p.category_id '
                    'ORDER BY c.id'
                    )
    data = cursor2.fetchall()

    conn2.close()

    # Create a dictionary to store products grouped by category
    products_category = {}

    for item in data:
        category_id = item['id']
        category_name = item['name']
        product_id = item['product_id']
        product_name = item['product_name']
        price = item['price']
        unit = item['unit']
        expiry_date = item['expiry_date']
        image_url = item['image_path']
        quantity = item['quantity']
    
        # Add products to the respective category in the dictionary
        if category_id not in products_category:
            products_category[category_id] = {'name': category_name, 'products' : []}

        products_category[category_id]['products'].append([
            product_id,
            product_name,
            price,
            unit,
            expiry_date,
            image_url,
            quantity
        ])
    
        selected_products = []
        category_ids = products_category.keys()

        if unique_category_id in category_ids:
            selected_catefory_name = products_category[unique_category_id]['name']
            selected_products = products_category[unique_category_id]['products']
    return render_template('admin_product_by_category.html', products=selected_products, category_name=selected_catefory_name, categories=categories, role='admin')



## function to search product by it's name or category name
@app.route('/admin/search')
def admin_search():
    query = request.args.get('query')

    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

    result = []
    cursor2.execute('SELECT * FROM products WHERE name LIKE ?', ('%' + query + '%',))
    products = cursor2.fetchall()
    result.extend(products)

    cursor2.execute('SELECT * FROM category WHERE name LIKE ?', ('%' + query + '%',))
    categories = cursor2.fetchall()

    for category in  categories:
        cursor2.execute('SELECT * FROM products WHERE category_id = ?', (category[0],))
        product_by_category = cursor2.fetchall()
        result.extend(product_by_category)

    conn2.close()

    return render_template('admin_search.html', query=query, products=result)


@app.route('/user/search')
def user_search():
    query = request.args.get('query')

    conn2 = get_store_db_connection()
    cursor2 = conn2.cursor()

    result = []
    cursor2.execute('SELECT * FROM products WHERE name LIKE ?', ('%' + query + '%',))
    products = cursor2.fetchall()
    result.extend(products)

    cursor2.execute('SELECT * FROM category WHERE name LIKE ?', ('%' + query + '%',))
    categories = cursor2.fetchall()

    for category in  categories:
        cursor2.execute('SELECT * FROM products WHERE category_id = ?', (category[0],))
        product_by_category = cursor2.fetchall()
        result.extend(product_by_category)

    conn2.close()

    return render_template('user_search.html', query=query, products=result)


## CART Section

## route to add product to cart
@app.route('/user/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    user_id = data.get('id')
    product_id = data.get('productId')
    product_name = data.get('productName')
    product_price = data.get('productPrice')
    product_unit = data.get('productUnit')
    product_image = data.get('productImage')
    product_quantity = 1

    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    cursor3.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    item = cursor3.fetchone()

    if item:
        return jsonify('Product already exist in cart')
    
    else:
        cursor3.execute('INSERT INTO cart (user_id, product_id, name, price, unit, image_path, quantity) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, product_id, product_name, product_price, product_unit, product_image, product_quantity ))
        conn3.commit()

    conn3.close()    

    return jsonify({'message': item})
    

## route to add product to cart
@app.route('/admin/add_to_cart', methods=['POST'])
def add_to_admin_cart():
    data = request.get_json()
    admin_id = data.get('id')
    product_id = data.get('productId')
    product_name = data.get('productName')
    product_price = data.get('productPrice')
    product_unit = data.get('productUnit')
    product_image = data.get('productImage')
    product_quantity = 1

    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    cursor3.execute('SELECT * FROM cart WHERE admin_id = ? AND product_id = ?', (admin_id, product_id))
    item = cursor3.fetchone()

    if item:
        return jsonify('Product already exist in cart')
    
    else:
        cursor3.execute('INSERT INTO cart (admin_id, product_id, name, price, unit, image_path, quantity) VALUES (?, ?, ?, ?, ?, ?, ?)', (admin_id, product_id, product_name, product_price, product_unit, product_image, product_quantity ))
        conn3.commit()

    conn3.close()    

    return jsonify({'message': item})

# function to calculate total price and product of products in cart
def calculate_total_price_and_product(cart):
    total_count = 0
    total_price = 0

    for product in cart:
        total_count += 1
        price = product[5]
        quantity = product[8]
        total_price += price * quantity
    return total_count, total_price

## route for user cart
@app.route('/user/cart')
def user_cart():
    if 'user_id' not in session:
        return redirect('/user/login')
    
    else:
        user_id = session['user_id']
    
    if user_id:
        # connect to db
        conn3 = sqlite3.connect('cart.db')
        cursor3 = conn3.cursor()

        cursor3.execute('SELECT * FROM cart WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        cart = cursor3.fetchall()

        total_count, total_price = calculate_total_price_and_product(cart)

        return render_template('user_cart.html', cart=cart, total_price=total_price, total_count=total_count)
    else:
        return redirect('/user/login')



## route for admin cart
@app.route('/admin/cart')
def admin_cart():
    if 'admin_id' not in session:
        return redirect('/admin/login')
    
    else:
        admin_id = session['admin_id']
    
    if admin_id:
        # connect to db
        conn3 = sqlite3.connect('cart.db')
        cursor3 = conn3.cursor()

        cursor3.execute('SELECT * FROM cart WHERE admin_id = ? ORDER BY created_at DESC', (admin_id,))
        cart = cursor3.fetchall()
        total_count, total_price = calculate_total_price_and_product(cart)

        return render_template('admin_cart.html', cart=cart, total_price=total_price, total_count=total_count)
    
    else:
        return redirect('/admin/login')
      

## route to remove product from user cart
@app.route('/user/cart/product/delete/<int:userId>/<int:productId>', methods=['DELETE'])
def remove_from_user_cart(productId, userId):
   
    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    # Delete product from database
    cursor3.execute('DELETE FROM cart WHERE product_id = ? AND user_id = ?', (productId, userId))
    conn3.commit()

    conn3.close()
    
    return jsonify({'message' : 'Product deleted'})

## route to remove product from admin cart
@app.route('/admin/cart/product/delete/<int:adminId>/<int:productId>', methods=['DELETE'])
def remove_from_admin_cart(productId, adminId):
   
    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    # Delete product from database
    cursor3.execute('DELETE FROM cart WHERE product_id = ? AND admin_id = ?', (productId, adminId))
    conn3.commit()

    conn3.close()
    
    return jsonify({'message' : 'Product deleted'})


## route to update user cart
@app.route('/user/cart/product/<int:userId>/<int:productId>', methods=['PUT'])
def update_user_cart(userId, productId):
    quantity = int(request.json.get('quantity'))

    # connect to db
    conn2 = sqlite3.connect('grocery_store.db')
    cursor2 = conn2.cursor() 

    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()    

    cursor2.execute('SELECT quantity FROM products WHERE id = ?', (productId,))
    product_quantity = cursor2.fetchone()

    conn2.close()

    # To handle quantity -- admin can only increase quantity of products till given quantity
    if quantity <= product_quantity[0]:
        cursor3.execute('UPDATE cart SET quantity = ? WHERE product_id = ? AND user_id = ?', (quantity, productId, userId))
        conn3.commit()

    else:
        quantity = quantity - 1

    return jsonify('Product quantity updated')

## route to update admin cart
@app.route('/admin/cart/product/<int:adminId>/<int:productId>', methods=['PUT'])
def update_admin_cart(adminId, productId):
    quantity = int(request.json.get('quantity'))

    # connect to db
    conn2 = sqlite3.connect('grocery_store.db')
    cursor2 = conn2.cursor() 

    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()    

    cursor2.execute('SELECT quantity FROM products WHERE id = ?', (productId,))
    product_quantity = cursor2.fetchone()

    conn2.close()

    # To handle quantity -- admin can only increase quantity of products till given quantity
    if quantity <= product_quantity[0]:
        cursor3.execute('UPDATE cart SET quantity = ? WHERE product_id = ? AND admin_id = ?', (quantity, productId, adminId))
        conn3.commit()

    else:
        quantity = quantity - 1

    return jsonify('Product quantity updated')

## route for user checkout
@app.route('/user/checkout')
def user_checkout():
   # connect to db
    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    cursor3.execute('SELECT * FROM cart')
    cart = cursor3.fetchall()

    _, total_price = calculate_total_price_and_product(cart=cart)

    for product in cart:
        userId = product[1]

    return render_template('user_checkout.html', user_id=userId, total_price=total_price)

## route for admin checkout
@app.route('/admin/checkout')
def admin_checkout():
    # connect to db
    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    cursor3.execute('SELECT * FROM cart')
    cart = cursor3.fetchall()

    _, total_price = calculate_total_price_and_product(cart=cart)

    for product in cart:
        adminId = product[2]

    return render_template('admin_checkout.html', admin_id=adminId, total_price=total_price)


@app.route('/admin/order/complete', methods=['POST'])
def complete_admin_order():
    admin_id = request.form.get('admin_id')
    
    # connect to db
    conn2 = sqlite3.connect('grocery_store.db')
    cursor2 = conn2.cursor()

    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    conn4 = sqlite3.connect('orders.db')
    cursor4 = conn4.cursor()

    try:
        # Retrieving all product from cart
        cursor3.execute('SELECT * FROM cart WHERE admin_id=?', (admin_id,))
        cart = cursor3.fetchall()

        _, total_price = calculate_total_price_and_product(cart=cart)

        # Update product quantities and remove from cart
        for item in cart:
            adminId = item[2]
            product_id = item[3]
            name = item[4]
            price = item[5]
            unit = item[6]
            image_url = item[7]
            quantity = int(item[8])

            cursor4.execute('INSERT INTO orders (admin_id, product_id, name, price, unit, image_path, quantity, total_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (adminId, product_id, name, price, unit, image_url, quantity, total_price))
            conn4.commit()

                
            cursor2.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', (quantity, product_id))
            conn2.commit()


        # Remove all products from cart for user
        cursor3.execute('DELETE FROM cart WHERE admin_id = ?', (admin_id,))
        conn3.commit()


        response = {
            'message': 'Order completed successfully'
        }
         
        return redirect('/admin/dashboard')
        
    except Exception as e:
        response = {
            'error': str(e)
        }
        return jsonify(response), 500
        
    finally:
        conn2.close()
        conn3.close()
        conn4.close()


@app.route('/user/order/complete', methods=['POST'])
def complete_user_order():
    user_id = request.form.get('user_id')
    
    # connect to db
    conn2 = sqlite3.connect('grocery_store.db')
    cursor2 = conn2.cursor()

    conn3 = sqlite3.connect('cart.db')
    cursor3 = conn3.cursor()

    conn4 = sqlite3.connect('orders.db')
    cursor4 = conn4.cursor()

    try:
        # Retrieving all product from cart
        cursor3.execute('SELECT * FROM cart WHERE user_id=?', (user_id,))
        cart = cursor3.fetchall()

        _, total_price = calculate_total_price_and_product(cart=cart)

        # Update product quantities and remove from cart
        for item in cart:
            userId = item[1]
            product_id = item[3]
            name = item[4]
            price = item[5]
            unit = item[6]
            image_url = item[7]
            quantity = int(item[8])

            cursor4.execute('INSERT INTO orders (user_id, product_id, name, price, unit, image_path, quantity, total_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (userId, product_id, name, price, unit, image_url, quantity, total_price))
            conn4.commit()

            cursor2.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', (quantity, product_id))
            conn2.commit()
            
        # Remove all products from cart for user
        cursor3.execute('DELETE FROM cart WHERE user_id = ?', (user_id))
        conn3.commit()


        response = {
            'message': 'Order completed successfully'
        }
         
        return redirect('/user/dashboard')
    
    except Exception as e:
        response = {
            'error': str(e)
        }
        return jsonify(response), 500
        
    finally:
        conn2.close()
        conn3.close()
        conn4.close()

# route for admin orders
@app.route('/admin/orders')
def admin_orders():
    if 'admin_id' not in session:
        return redirect('/admin/login')
    
    else:
        admin_id = session['admin_id']
    
    if admin_id:
        # connect to db
        conn4 = sqlite3.connect('orders.db')
        cursor4 = conn4.cursor()

        cursor4.execute('SELECT * FROM orders WHERE admin_id = ? ORDER BY created_at DESC', (admin_id,))
        orders = cursor4.fetchall()

        return render_template('admin_orders.html', orders=orders)
    
    else:
        return redirect('/admin/login')
    
#route for user orders
@app.route('/user/orders')
def user_orders():
    if 'user_id' not in session:
        return redirect('/user/login')
    
    else:
        user_id = session['user_id']
    
    if user_id:
        # connect to db
        conn4 = sqlite3.connect('orders.db')
        cursor4 = conn4.cursor()

        cursor4.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        orders = cursor4.fetchall()

        return render_template('user_orders.html', orders=orders)
    
    else:
        return redirect('/user/login')


if __name__ == "__main__":
    app.run(debug=True)