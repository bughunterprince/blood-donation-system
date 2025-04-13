from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Pinku9810#&@localhost/flask_forms'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ===================== MODELS =====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    appointment_date = db.Column(db.String(20))
    time_slot = db.Column(db.String(20))

class HospitalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(100))
    contact_name = db.Column(db.String(100))
    blood_type = db.Column(db.String(10))
    units = db.Column(db.Integer)
    priority = db.Column(db.String(10))
    required_date = db.Column(db.String(20))

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)

with app.app_context():
    db.create_all()

# ===================== DECORATOR =====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ===================== AUTH ROUTES =====================

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if User.query.filter_by(email=email).first():
        return render_template('signup.html', error='User already exists.')

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login_page'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template('login.html', error='Invalid credentials.')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ===================== PAGE ROUTES =====================

@app.route('/')
def root():
    return redirect(url_for('login_page'))

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/signup.html')
def signup_page():
    return render_template('signup.html')

@app.route('/register.html')
@login_required
def register_page():
    return render_template('register.html')

@app.route('/index.html')
@login_required
def index():
    return render_template('index.html')

@app.route('/customer.html')
@login_required
def customer_page():
    return render_template('customer.html')

@app.route('/hospital.html')
@login_required
def hospital_page():
    return render_template('hospital.html')

@app.route('/bloodbank.html')
@login_required
def bloodbank_page():
    return render_template('bloodbank.html')

@app.route('/custfinal.html')
@login_required
def custfinal_page():
    return render_template('custfinal.html')

# ===================== FORM SUBMISSIONS =====================

@app.route('/submit-customer', methods=['POST'])
@login_required
def submit_customer():
    data = request.get_json()
    try:
        customer = Customer(**data)
        db.session.add(customer)
        db.session.commit()
        return jsonify({"message": "✅ Appointment confirmed!"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/submit-hospital', methods=['POST'])
@login_required
def submit_hospital():
    data = request.get_json()
    try:
        req = HospitalRequest(**data)
        db.session.add(req)
        db.session.commit()
        return jsonify({"message": "✅ Request submitted!"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/register', methods=['POST'])
@login_required
def register_donor():
    data = request.get_json()
    donor = Donor(name=data['name'], phone=data['phone'], age=data['age'])
    db.session.add(donor)
    db.session.commit()
    return jsonify({"message": "Donor registered"})

# ===================== RUN =====================

if __name__ == '__main__':
    app.run(debug=True)
