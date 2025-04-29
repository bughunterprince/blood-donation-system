from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from flask_cors import CORS
from dotenv import load_dotenv
import os

# ✅ Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret')

# ✅ PostgreSQL config from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    appointment_date = db.Column(db.String(20))
    time_slot = db.Column(db.String(20))

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(120))
    contact_name = db.Column(db.String(120))
    blood_type = db.Column(db.String(10))
    units = db.Column(db.Integer)
    priority = db.Column(db.String(20))
    required_date = db.Column(db.String(20))

# ✅ Create tables
with app.app_context():
    db.create_all()

# ✅ Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='User already exists.')

        hashed_pw = sha256_crypt.hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        try:
            if user and sha256_crypt.verify(password, user.password_hash):
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('login.html', error='Invalid password format.')

        return render_template('login.html', error='Invalid credentials.')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', username=user.username)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/custfinal')
def custfinal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('custfinal.html')

@app.route('/hospital')
def hospital():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('hospital.html')

@app.route('/bloodbank')
def bloodbank():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('bloodbank.html')

@app.route('/submit-customer', methods=['POST'])
def submit_customer():
    try:
        data = request.get_json()
        new_appointment = Appointment(
            name=data['name'],
            email=data['email'],
            age=data['age'],
            gender=data['gender'],
            appointment_date=data['appointment_date'],
            time_slot=data['time_slot']
        )
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({'message': '✅ Appointment booked successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit-hospital', methods=['POST'])
def submit_hospital():
    try:
        data = request.get_json()
        new_request = BloodRequest(
            hospital_name=data['hospital_name'],
            contact_name=data['contact_name'],
            blood_type=data['blood_type'],
            units=data['units'],
            priority=data['priority'],
            required_date=data['required_date']
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({'message': '✅ Blood request submitted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # ✅ Debug False for production
