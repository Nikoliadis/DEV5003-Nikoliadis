from flask import Flask, render_template, request, redirect, url_for, flash, session, json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'laichi'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

items = {
    1: {'title': 'Ancient Vase', 'price': 25, 'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image'},
    2: {'title': 'Renaissance Painting', 'price': 30, 'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691'},
    3: {'title': 'Ancient Sculpture', 'price': 20, 'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format'},
    4: {'title': 'Impressionist Artwork', 'price': 15, 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s'},
}

# Models for User and Tickets (To track the purchases)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Hash the password and set it to the database field."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the given password matches the stored hash."""
        return check_password_hash(self.password, password)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=True)  # Only for credit card payments
    total_cost = db.Column(db.Float, nullable=False)  # Add total cost

users = {}

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    # Redirect users to the login page when they're not authenticated
    flash("You need to log in to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/")
def home():
    featured_items = [
        {'id': 1, 'title': 'Ancient Vase', 'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image', 'description': 'A rare ancient vase from the 4th century.'},
        {'id': 2, 'title': 'Renaissance Painting', 'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691', 'description': 'A beautiful painting from the Renaissance period.'},
        {'id': 3, 'title': 'Ancient Sculpture', 'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format', 'description': 'A rare sculpture from Ancient Rome.'},
        {'id': 4, 'title': 'Impressionist Artwork', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s', 'description': 'A beautiful painting from the Impressionist era.'}
    ]
    user_logged_in = 'user_id' in session 
    return render_template('home.html', featured_items=featured_items, user_logged_in=user_logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login']
        password = request.form['password']

        if not login_input or not password:
            flash("Please enter both username/email and password", "danger")
            return redirect(url_for("login"))

        # Check if the input is an email or username
        user = None
        if '@' in login_input:
            user = User.query.filter_by(email=login_input).first()
        else:
            user = User.query.filter_by(username=login_input).first()

        # Check if user exists and password matches
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email/username or password', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('register'))

        # Create new user object
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        # Add the user to the session and commit to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/news")
def news():
    return render_template('news.html')

@app.route('/events')
def events():
    events = [
        {
            'title': 'Ancient Vase',
            'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image',
            'description': 'A rare ancient vase from the 4th century. It was discovered in a tomb in Italy and is a prime example of ancient Greek pottery.',
            'price': 25,
        },
        {
            'title': 'Renaissance Painting',
            'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691',
            'description': 'A beautiful painting from the Renaissance period, painted by Leonardo da Vinci. The Mona Lisa remains one of the most famous artworks in the world.',
            'price': 30,
        },
        {
            'title': 'Ancient Sculpture',
            'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format',
            'description': 'A rare sculpture from Ancient Rome, dating back to the 2nd century. It depicts a famous Roman general and is considered one of the finest works of its kind.',
            'price': 20,
        },
        {
            'title': 'Impressionist Artwork',
            'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s',
            'description': 'A beautiful painting from the Impressionist era. The work focuses on the beauty of light and nature, with vibrant colors and bold brushstrokes.',
            'price': 15,
        }
    ]
    return render_template('events.html', events=events)

@app.route("/exhibits")
def exhibits():
    return render_template('exhibits.html')

@app.route("/services")
def services():
    return render_template('services.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        feedback_text = request.form.get('feedback')

        flash("Thank You For Your Feedback! We Will Analyze It And If Necessary We Will Contact You Via Email", "success")
        return redirect(url_for('feedback'))

    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback = request.form['feedback']
    flash('Thank you for your feedback! We will analyze it and if necessary, we will contact you via email.', 'success')
    return redirect(url_for('feedback'))

@app.route("/item/<int:item_id>")
@login_required
def item_detail(item_id):
    items = {
        1: {
            'title': 'Ancient Vase',
            'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image',
            'description': 'A rare ancient vase from the 4th century. It was discovered in a tomb in Italy and is a prime example of ancient Greek pottery.',
            'price': 25,
        },
        2: {
            'title': 'Renaissance Painting',
            'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691',
            'description': 'A beautiful painting from the Renaissance period, painted by Leonardo da Vinci. The Mona Lisa remains one of the most famous artworks in the world.',
            'price': 30,
        },
        3: {
            'title': 'Ancient Sculpture',
            'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format',
            'description': 'A rare sculpture from Ancient Rome, dating back to the 2nd century. It depicts a famous Roman general and is considered one of the finest works of its kind.',
            'price': 20,
        },
        4: {
            'title': 'Impressionist Artwork',
            'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s',
            'description': 'A beautiful painting from the Impressionist era. The work focuses on the beauty of light and nature, with vibrant colors and bold brushstrokes.',
            'price': 15,
        },
    }

    item = items.get(item_id)
    if not item:
        flash("Item not found!", 'danger')
        return redirect(url_for('home'))

    return render_template('item_detail.html', item=item, item_id=item_id)

@app.route("/buy_ticket", methods=['POST'])
@login_required
def buy_ticket():
    item_id = request.form.get('item_id')
    items = {
        1: {'title': 'Ancient Vase', 'price': 25},
        2: {'title': 'Renaissance Painting', 'price': 30},
        3: {'title': 'Ancient Sculpture', 'price': 20},
        4: {'title': 'Impressionist Artwork', 'price': 15},
    }

    item = items.get(int(item_id))
    if not item:
        flash("Item not found!", 'danger')
        return redirect(url_for('home'))

    quantity = int(request.form.get('quantity'))
    total_cost = item['price'] * quantity

    flash(f"Successfully purchased {quantity} ticket(s) for {item['title']}! Total cost: ${total_cost}", 'success')
    return redirect(url_for('home'))

@app.route("/add_to_cart/<int:item_id>", methods=['POST'])
@login_required
def add_to_cart(item_id):
    items = {
        1: {'title': 'Ancient Vase', 'price': 25, 'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image'},
        2: {'title': 'Renaissance Painting', 'price': 30, 'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691'},
        3: {'title': 'Ancient Sculpture', 'price': 20, 'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format'},
        4: {'title': 'Impressionist Artwork', 'price': 15, 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s'},
    }

    item = items.get(item_id)
    if not item:
        flash("Item not found!", 'danger')
        return redirect(url_for('home'))

    # Get quantity from the form
    quantity = int(request.form.get('quantity'))
    
    # Add item to session
    cart = session.get('cart', [])
    cart.append({'item_id': item_id, 'quantity': quantity})
    session['cart'] = cart

    flash(f"Added {quantity} of {item['title']} to your cart!", 'success')
    return redirect(url_for('cart'))

@app.route("/cart")
@login_required
def cart():
    items = {
        1: {'title': 'Ancient Vase', 'price': 25, 'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image'},
        2: {'title': 'Renaissance Painting', 'price': 30, 'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691'},
        3: {'title': 'Ancient Sculpture', 'price': 20, 'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format'},
        4: {'title': 'Impressionist Artwork', 'price': 15, 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s'},
    }

    cart = session.get('cart', [])
    cart_items = []
    total_price = 0

    for cart_item in cart:
        item = items.get(cart_item['item_id'])
        if item:
            item['quantity'] = cart_item['quantity']
            item['total_price'] = item['price'] * cart_item['quantity']
            cart_items.append(item)
            total_price += item['total_price']

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = []
    total_price = 0

    # Fetch the cart from the session
    cart = session.get('cart', [])

    # Ensure items are in the expected format
    for cart_item in cart:
        print("Processing cart_item:", cart_item)
        print("Type of cart_item:", type(cart_item))

        # If cart_item is a string (e.g., JSON string), attempt to parse it
        if isinstance(cart_item, str):
            try:
                cart_item = json.loads(cart_item)  # Try parsing it as JSON
            except json.JSONDecodeError as e:
                print(f"Failed to parse cart_item: {cart_item} - {e}")
                continue  # Skip this cart_item if parsing fails

        # Ensure cart_item is a dictionary with 'item_id'
        if isinstance(cart_item, dict) and 'item_id' in cart_item:
            item = items.get(cart_item['item_id'])  # Fetch item from the items dictionary
            if item:
                # Calculate quantity and total price
                item['quantity'] = cart_item.get('quantity', 1)
                item['total_price'] = item['price'] * item['quantity']
                cart_items.append(item)
                total_price += item['total_price']
            else:
                print(f"Item not found for item_id: {cart_item['item_id']}")
        else:
            print("Unexpected cart_item format:", cart_item)

    # Render the checkout page with the cart items and total price
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

if __name__ == '__main__':
    app.run(debug=True)