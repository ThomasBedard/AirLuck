from flask import Flask, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import qwiic_bme280
import threading
import time
from datetime import datetime
import board
import adafruit_ens160

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config["DEBUG"] = True
i2c = board.I2C()
ens = adafruit_ens160.ENS160(i2c)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    pressure = db.Column(db.Float)
    humidity = db.Column(db.Float)
    eco2 = db.Column(db.Float)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('index.html')

# BME280 sensor initialization and data collection
bme280 = qwiic_bme280.QwiicBme280()
if not bme280.is_connected():
    print("BME280 sensor is not connected")
bme280.begin()

data_temp = []
data_pressure = []
data_humidity = []
data_eco2 = []
labels = []

def collect_data():
    global data_temp, data_pressure, data_humidity, data_eco2, labels
    while True:
        temperature_c = bme280.temperature_celsius
        pressure = bme280.pressure
        humidity = bme280.humidity

        timestamp = datetime.now().strftime("%H:%M:%S")
        data_temp.append(temperature_c)
        data_pressure.append(pressure)
        data_humidity.append(humidity)
        labels.append(timestamp)


        try:
            data_eco2.append(ens.eCO2)  # Directly read eCO2 value
            eco2_value = ens.eCO2
        except Exception as e:
            print("Error reading from ENS160:", e)
            eco2_value = None


        if len(data_temp) > 30:
            data_temp.pop(0)
            data_pressure.pop(0)
            data_humidity.pop(0)
            labels.pop(0)


        timestamp = datetime.now()
        new_record = SensorData(temperature=temperature_c, pressure=pressure, humidity=humidity, eco2=eco2_value)

        with app.app_context():
            db.session.add(new_record)
            db.session.commit()

        # Save to text file
        with open('sensor_data.txt', 'a') as f:
            f.write(f"{timestamp}, {temperature_c}, {pressure}, {humidity}, {eco2_value}\n")

        time.sleep(1)

data_collection_thread = threading.Thread(target=collect_data)
data_collection_thread.daemon = True
data_collection_thread.start()

@app.route('/get-sensor-data')
def get_sensor_data():
    return jsonify({
        'labels': labels[-30:],
        'data_temp': data_temp[-30:],
        'data_pressure': data_pressure[-30:],
        'data_humidity': data_humidity[-30:],
        'data_eco2': data_eco2[-30:]
    })

@app.route('/get-latest-sensor-data')
def get_latest_sensor_data():
    return jsonify({
        'temperature': data_temp[-1] if data_temp else "N/A",
        'pressure': data_pressure[-1] if data_pressure else "N/A",
        'humidity': data_humidity[-1] if data_humidity else "N/A",
        'eco2': data_eco2[-1] if data_eco2 else "N/A"
    })


@app.route('/line-charts')
@login_required
def line_charts():
    return render_template('line_graph_example.html', 
                           data_temp=data_temp, 
                           data_pressure=data_pressure, 
                           data_humidity=data_humidity,
                           data_eco2=data_eco2,
                           labels=labels)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
