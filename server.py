from flask import Flask, render_template, request, redirect, url_for, flash, session
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

# Models for User and Tickets (To track the purchases)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=True)  # Only for credit card payments
    total_cost = db.Column(db.Float, nullable=False)  # Add total cost


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/")
def home():
    featured_items = [
        {'id': 1, 'title': 'Ancient Vase', 'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image', 'description': 'A rare ancient vase from the 4th century.'},
        {'id': 2, 'title': 'Renaissance Painting', 'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691', 'description': 'A beautiful painting from the Renaissance period.'},
        {'id': 3, 'title': 'Ancient Sculpture', 'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format', 'description': 'A rare sculpture from Ancient Rome.'},
        {'id': 4, 'title': 'Impressionist Artwork', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s', 'description': 'A beautiful painting from the Impressionist era.'}
    ]
    return render_template('home.html', featured_items=featured_items)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login_input')
        password = request.form.get('password')

        if not login_input or not password:
            flash('Please enter both username/email and password.', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter((User.username == login_input) | (User.email == login_input)).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username/email and password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username or Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration Successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/news")
def news():
    return render_template('news.html')

@app.route("/events")
def events():
    return render_template('events.html')

@app.route("/exhibits")
def exhibits():
    return render_template('exhibits.html')

@app.route("/services")
def services():
    return render_template('services.html')

@app.route("/feedback")
def feedback():
    return render_template('feedback.html')

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

    item = items.get(int(item_id))  # Ensure the item_id is treated as an integer
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
    session['cart'] = cart  # Save the cart in the session

    flash(f"Added {quantity} of {item['title']} to your cart!", 'success')
    return redirect(url_for('cart'))  # Redirect to the cart page

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

@app.route('/place_order', methods=['POST'])
def place_order():
    quantity = request.form.get('quantity')
    payment_method = request.form.get('payment_method')

    if payment_method == 'credit_card':
        card_number = request.form.get('card_number')
        card_owner = request.form.get('card_owner')
        cvv = request.form.get('cvv')

        if not all([card_number, card_owner, cvv]):
            return "Missing credit card details", 400

        card_owner_parts = card_owner.split()
        if len(card_owner_parts) < 2:
            return "Please provide both first and last name", 400

        first_name = card_owner_parts[0]
        last_name = " ".join(card_owner_parts[1:])

        print(f"Processing payment for {first_name} {last_name}")

    return f"Order placed successfully! Quantity: {quantity}, Payment Method: {payment_method}"

@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    # Handle the form submission here
    payment_method = request.form.get('payment_method')
    ticket = request.form.get('ticket')
    quantity = request.form.get('quantity')
    # Add logic to process payment or record data
    return "Order placed successfully!"

@app.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
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

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')

        # Create a new Ticket record in the database
        for cart_item in cart:
            item_id = cart_item['item_id']
            quantity = cart_item['quantity']
            total_cost = items[item_id]['price'] * quantity
            new_ticket = Ticket(
                user_id=current_user.id,
                item_id=item_id,
                quantity=quantity,
                payment_method=payment_method,
                total_cost=total_cost,
            )
            db.session.add(new_ticket)

        db.session.commit()

        flash("Order placed successfully!", 'success')
        session.pop('cart', None)  # Clear the cart after the order is placed
        return redirect(url_for('home'))

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)


@app.route("/order_confirmation/<int:ticket_id>")
@login_required
def order_confirmation(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        flash("Order not found!", 'danger')
        return redirect(url_for('home'))
    
    items = {
        1: {'title': 'Ancient Vase', 'price': 25},
        2: {'title': 'Renaissance Painting', 'price': 30},
        3: {'title': 'Ancient Sculpture', 'price': 20},
        4: {'title': 'Impressionist Artwork', 'price': 15},
    }

    item = items.get(ticket.item_id)
    return render_template('order_confirmation.html', ticket=ticket, item=item)


if __name__ == '__main__':
    app.run(debug=True)