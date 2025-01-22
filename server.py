from flask import Flask, render_template, request, redirect, url_for, flash, session, json, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from functools import wraps
import os
from datetime import datetime


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
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """Hash the password and set it to the database field."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the given password matches the stored hash."""
        return check_password_hash(self.password, password)
    
# Admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function
 
def create_admin_user():
    with app.app_context():
        admin_username = "Admin"
        admin_email = "Admin@gmail.com"
        admin_password = "Admin123!"

        existing_admin = User.query.filter_by(username=admin_username).first()

        if not existing_admin:
            admin_user = User(username=admin_username, email=admin_email)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=True)  # Only for credit card payments
    total_cost = db.Column(db.Float, nullable=False)  # Add total cost


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=True)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='unread')


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    feedback = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='unread')

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

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/news', methods=['GET', 'POST'])
@login_required
@admin_required
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']

        # Save the uploaded image to the static/uploads directory
        if image:
            image_path = f"static/uploads/{image.filename}"
            image.save(image_path)

        # Add the news to the database
        new_news = News(title=title, content=content, image_path=image_path)
        db.session.add(new_news)
        db.session.commit()

        flash("News added successfully!", "success")
        return redirect(url_for('add_news'))

    # Fetch all news items from the database to display in the Manage News section
    news_items = News.query.all()
    print(news_items)
    return render_template('add_news.html', news_items=news_items)


@app.route('/delete_news/<int:news_id>', methods=['POST'])
@login_required
@admin_required
def delete_news(news_id):
    news = News.query.get_or_404(news_id)  # Find the news item by ID or return 404
    if news.image_path:
        try:
            os.remove(news.image_path)  # Remove the associated image file
        except FileNotFoundError:
            pass  # Ignore if the file does not exist
    db.session.delete(news)  # Delete the news item
    db.session.commit()  # Commit changes to the database
    flash('News deleted successfully!', 'success')  # Show success message
    return redirect(url_for('add_news'))  # Redirect back to the Add News page


@app.route('/admin/events', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date']
        price = request.form.get('price')  # Get price from the form
        image = request.files['image']

        # Convert date string to datetime.date
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('add_event'))

        # Save the image
        upload_folder = 'static/uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        if image:
            image_path = os.path.join(upload_folder, image.filename)
            image.save(image_path)
        else:
            flash("Image upload failed. Please try again.", "danger")
            return redirect(url_for('add_event'))

        # Create the event
        new_event = Event(
            title=title,
            description=description,
            date=event_date,
            price=float(price) if price else None,
            image_path=image_path,
        )
        db.session.add(new_event)
        db.session.commit()
        flash("Event added successfully!", "success")
        return redirect(url_for('add_event'))

    # Fetch all events to display in the Manage Events section
    events = Event.query.all()
    return render_template('add_event.html', events=events)


@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)

@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully!", "success")
    return redirect(url_for('add_event'))

@app.route('/admin/feedback')
@login_required
@admin_required
def view_feedback():
    feedbacks = Feedback.query.all()
    print(feedbacks)
    return render_template('view_feedback.html', feedbacks=feedbacks)

@app.route('/admin/feedback/mark_read/<int:feedback_id>', methods=['POST'])
@login_required
@admin_required
def mark_feedback_read(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.status = 'read'
    db.session.commit()
    flash("Feedback marked as read.", "success")
    return redirect(url_for('view_feedback'))

@app.route('/admin/feedback/mark_unread/<int:feedback_id>', methods=['POST'])
@login_required
@admin_required
def mark_feedback_unread(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.status = 'unread'
    db.session.commit()
    flash("Feedback marked as unread.", "success")
    return redirect(url_for('view_feedback'))

@app.route('/admin/messages', methods=['GET', 'POST'])
@login_required
@admin_required
def view_messages():
    show_archived = request.args.get('archived', 'false').lower() == 'true'

    if request.method == 'POST':
        action = request.form.get('action')
        message_id = request.form.get('message_id')
        message = ContactMessage.query.get(message_id)

        if message:
            if action == 'mark_read':
                message.status = 'read'
            elif action == 'mark_unread':
                message.status = 'unread'
            elif action == 'archive':
                message.status = 'archived'
            db.session.commit()
            flash(f"Message {action.replace('_', ' ')} successfully.", "success")
        else:
            flash("Message not found.", "danger")

    if show_archived:
        messages = ContactMessage.query.filter_by(status='archived').all()
    else:
        messages = ContactMessage.query.filter(ContactMessage.status != 'archived').all()

    return render_template('view_messages.html', messages=messages, show_archived=show_archived)


@app.route('/admin/messages/archive/<int:message_id>', methods=['POST'])
@login_required
@admin_required
def archive_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.status = 'archived'
    db.session.commit()
    flash("Message archived successfully.", "success")
    return redirect(url_for('view_messages'))


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
            if user.is_admin:
                flash('Welcome, Admin!', 'success')
                return redirect(url_for('admin_dashboard'))  # Redirect admin to the admin dashboard
            return redirect(url_for('home'))  # Regular user redirection
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
        
        db.session.add(new_user)
        try:
            db.session.commit()
            print("User added successfully!")
        except Exception as e:
            print(f"Error adding user to database: {e}")
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for('register'))

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
    news_items = News.query.all()  # Fetch all news from the database
    return render_template('news.html', news_items=news_items)


@app.route('/events')
def events():
    # Fetch events from the database
    events_from_db = Event.query.all()
    
    # Hardcoded events (update 'item_id' to 'id' for consistency)
    hardcoded_events = [
        {
            'id': 'H1',  # Changed from 'item_id' to 'id'
            'title': 'Ancient Vase',
            'image_path': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image',
            'description': 'A rare ancient vase from the 4th century. It was discovered in a tomb in Italy and is a prime example of ancient Greek pottery.',
            'price': 25,
        },
        {
            'id': 'H2',  # Changed from 'item_id' to 'id'
            'title': 'Renaissance Painting',
            'image_path': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691',
            'description': 'A beautiful painting from the Renaissance period, painted by Leonardo da Vinci. The Mona Lisa remains one of the most famous artworks in the world.',
            'price': 30,
        },
        {
            'id': 'H3',  # Changed from 'item_id' to 'id'
            'title': 'Ancient Sculpture',
            'image_path': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format',
            'description': 'A rare sculpture from Ancient Rome, dating back to the 2nd century. It depicts a famous Roman general and is considered one of the finest works of its kind.',
            'price': 20,
        },
        {
            'id': 'H4',  # Changed from 'item_id' to 'id'
            'title': 'Impressionist Artwork',
            'image_path': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s',
            'description': 'A beautiful painting from the Impressionist era. The work focuses on the beauty of light and nature, with vibrant colors and bold brushstrokes.',
            'price': 15,
        },
    ]
    
    db_events = Event.query.all()
    # Combine both hardcoded events and database events
    events = hardcoded_events + [
        {
            'id': event.id,
            'title': event.title,
            'image_path': event.image_path,
            'description': event.description,
            'price': event.price,
        }
        for event in db_events
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

        print(f"Received Feedback: {name}, {email}, {feedback_text}")

        new_feedback = Feedback(user_id=current_user.id if current_user.is_authenticated else None,
                                feedback=feedback_text)
        db.session.add(new_feedback)
        db.session.commit()

        flash("Thank you for your feedback!", "success")
        return redirect(url_for('feedback'))

    return render_template('feedback.html')


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback_text = request.form['feedback']
    new_feedback = Feedback(user_id=current_user.id if current_user.is_authenticated else None, feedback=feedback_text)
    db.session.add(new_feedback)
    db.session.commit()
    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('feedback'))

@app.route('/submit_contact_message', methods=['POST'])
def submit_contact_message():
    name = request.form['name']
    email = request.form['email']
    message_text = request.form['message']

    # Create a new ContactMessage instance
    new_message = ContactMessage(name=name, email=email, message=message_text)
    db.session.add(new_message)
    db.session.commit()

    flash("Thank you for your message! We'll get back to you soon.", "success")
    return redirect(url_for('contact'))


@app.route("/item/<string:item_id>")
@login_required
def item_detail(item_id):
    # Check if the item ID is prefixed for hardcoded items
    if item_id.startswith("H"):
        hardcoded_items = {
            "H1": {'title': 'Ancient Vase', 'price': 25, 'image_path': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image', 'description': 'A rare ancient vase from the 4th century.'},
            "H2": {'title': 'Renaissance Painting', 'price': 30, 'image_path': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691', 'description': 'A beautiful painting from the Renaissance period.'},
            "H3": {'title': 'Ancient Sculpture', 'price': 20, 'image_path': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format', 'description': 'A rare sculpture from Ancient Rome.'},
            "H4": {'title': 'Impressionist Artwork', 'price': 15, 'image_path': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s', 'description': 'A beautiful painting from the Impressionist era.'},
        }
        item = hardcoded_items.get(item_id)
        if not item:
            abort(404)
    else:
        # Look for the event in the database
        event = Event.query.get_or_404(int(item_id))
        item = {
            'title': event.title,
            'price': getattr(event, 'price', None),
            'image_path': event.image_path,
            'description': event.description,
        }

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

@app.route('/add_to_checkout', methods=['POST'])
def add_to_checkout():
    item_id = request.json.get('item_id')
    items = session.get('checkout_items', [])
    items.append(item_id)  # Store ID as-is (with prefixes for hardcoded items)
    session['checkout_items'] = items
    return jsonify(success=True, message="Item added to checkout!", redirect_url=url_for('home', item_added='true'))



@app.route('/get_checkout_items', methods=['GET'])
def get_checkout_items():
    hardcoded_items = {
        "H1": {'id': "H1", 'title': 'Ancient Vase', 'price': 25, 'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image'},
        "H2": {'id': "H2", 'title': 'Renaissance Painting', 'price': 30, 'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691'},
        "H3": {'id': "H3", 'title': 'Ancient Sculpture', 'price': 20, 'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format'},
        "H4": {'id': "H4", 'title': 'Impressionist Artwork', 'price': 15, 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s'},
    }

    checkout_items = session.get('checkout_items', [])
    grouped_items = {}

    for item_id in checkout_items:
        if item_id.startswith("H"):
            item = hardcoded_items.get(item_id)
        else:
            event = Event.query.get(int(item_id))
            item = {
                'id': event.id,
                'title': event.title,
                'price': event.price,
                'image': event.image_path,
            }

        if item_id in grouped_items:
            grouped_items[item_id]['quantity'] += 1
        else:
            grouped_items[item_id] = {**item, 'quantity': 1}

    return jsonify(items=list(grouped_items.values()))



@app.route('/update_cart_quantity', methods=['POST'])
def update_cart_quantity():
    data = request.json
    item_id = str(data['item_id'])  # Ensure item_id is treated as a string
    action = data['action']
    
    # Retrieve the checkout items from the session
    checkout_items = session.get('checkout_items', [])
    
    if action == 'increase':
        checkout_items.append(item_id)  # Add the item_id to increase quantity
    elif action == 'decrease':
        if item_id in checkout_items:
            checkout_items.remove(item_id)  # Safely remove the item if it exists
    
    # Update the session with the modified checkout items
    session['checkout_items'] = checkout_items

    # Calculate the new quantity of the item
    new_quantity = checkout_items.count(item_id)

    return jsonify(success=True, new_quantity=new_quantity)

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
    # Define the items (as per your requirement)
    items = {
        1: {'title': 'Ancient Vase', 'price': 25, 'image': 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/248902/541985/main-image'},
        2: {'title': 'Renaissance Painting', 'price': 30, 'image': 'https://cdn.shopify.com/s/files/1/1414/2472/files/1-_604px-Mona_Lisa__by_Leonardo_da_Vinci__from_C2RMF_retouched.jpg?v=1558424691'},
        3: {'title': 'Ancient Sculpture', 'price': 20, 'image': 'https://cdn.sanity.io/images/cctd4ker/production/1aa8046e23e93e92b205aae6be6480549b9c7ca1-1440x960.jpg?w=3840&q=75&fit=clip&auto=format'},
        4: {'title': 'Impressionist Artwork', 'price': 15, 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlC9suapfI1YOZYafNsa_N-0DlDAaXpha6YA&s'},
    }

    cart_items = []
    total_price = 0

    # Fetch the cart from the session
    cart = session.get('cart', [])

    # Process each item in the cart
    for cart_item in cart:
        # Ensure cart_item is a dictionary and has an item_id
        if isinstance(cart_item, dict) and 'item_id' in cart_item:
            item = items.get(cart_item['item_id'])
            if item:
                # Add quantity and calculate total price for each item
                item['quantity'] = cart_item['quantity']
                item['total_price'] = item['price'] * item['quantity']
                cart_items.append(item)
                total_price += item['total_price']
        else:
            print(f"Unexpected cart_item format: {cart_item}")

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/complete_checkout', methods=['POST'])
def complete_checkout():
    # Retrieve form data
    payment_method = request.form.get('payment_method')
    address_line_1 = request.form.get('address_line_1')
    address_line_2 = request.form.get('address_line_2')
    postal_code = request.form.get('postal_code')
    city = request.form.get('city')
    phone = request.form.get('phone')

    # Simulate item and order details
    checkout_items = session.get('checkout_items', [])
    items_data = {
        1: {'title': 'Ancient Vase', 'price': 25},
        2: {'title': 'Renaissance Painting', 'price': 30},
        3: {'title': 'Ancient Sculpture', 'price': 20},
        4: {'title': 'Impressionist Artwork', 'price': 15},
    }

    # Calculate total cost
    total_cost = 0
    for item_id in checkout_items:
        total_cost += items_data[int(item_id)]['price']

    # Prepare ticket details for the confirmation page
    ticket = {
        'payment_method': payment_method,
        'address': f"{address_line_1}, {address_line_2}, {postal_code}, {city}",
        'total_cost': total_cost,
        'quantity': len(checkout_items),
    }

    # Redirect to the order confirmation page
    return render_template('order_confirmation.html', ticket=ticket, item=items_data[int(checkout_items[0])])

if __name__ == '__main__':
    app.run(debug=True)