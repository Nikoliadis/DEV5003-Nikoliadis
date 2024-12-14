from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    if current_user.is_authenticated:
        featured_items = [
            {'title': 'Ancient Vase', 'image': 'https://static01.nyt.com/images/2017/08/01/nyregion/01-SEIZE-1/01-SEIZE-1-superJumbo.jpg', 'description': 'A rare ancient vase from the 4th century.'},
            {'title': 'Renaissance Painting', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYQzhGI2Jnk42d8TP2E6D1nd5k3q3BqRpf7Q&s', 'description': 'A beautiful painting from the Renaissance period.'}
        ]
        return render_template('home.html', featured_items=featured_items)
    else:
        return render_template('home.html')

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
            return redirect(url_for('profile'))
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

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
