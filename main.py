import cv2
import pytesseract
import RPi.GPIO as GPIO
import time
import sqlite3
from flask import Flask, request, jsonify, render_template, session
from smbus2 import SMBus
import serial

# -------------------- GPIO SETUP --------------------
GPIO.setmode(GPIO.BCM)

# Boom Barrier Relays
RELAY_OPEN = 17  # Opens barrier
RELAY_CLOSE = 27  # Closes barrier

# Buzzer (Unauthorized Alert)
BUZZER = 22

# Push Buttons (Manual Override)
BUTTON_OPEN = 5
BUTTON_CLOSE = 6

GPIO.setup([RELAY_OPEN, RELAY_CLOSE, BUZZER, BUTTON_OPEN, BUTTON_CLOSE], GPIO.OUT)
GPIO.output([RELAY_OPEN, RELAY_CLOSE], GPIO.LOW)

# -------------------- LCD SETUP --------------------
I2C_ADDR = 0x27
bus = SMBus(1)

def lcd_display(text):
    bus.write_byte_data(I2C_ADDR, 0x00, ord(text))

# -------------------- DATABASE SETUP --------------------
conn = sqlite3.connect('anpr.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    plate TEXT UNIQUE NOT NULL
)
''')

conn.commit()

# -------------------- FLASK SERVER --------------------
app = Flask(__name__)
app.secret_key = "secret_key"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username, password = data["username"], data["password"]
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        session["username"] = username
        session["role"] = result[0]
        return jsonify({"role": result[0]})
    return jsonify({"error": "Invalid login"}), 401

@app.route('/admin')
def admin_dashboard():
    if session.get('role') == 'admin':
        return render_template('admin.html')
    return "Access Denied", 403

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    username, password = data["username"], data["password"]

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, password))
        conn.commit()
        return jsonify({"message": "User created successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"message": "User already exists"}), 400

@app.route('/link_vehicle', methods=['POST'])
def link_vehicle():
    data = request.json
    username, plate = data["username"], data["plate"]

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if not cursor.fetchone():
        return jsonify({"message": "User does not exist"}), 400

    try:
        cursor.execute("INSERT INTO vehicles (username, plate) VALUES (?, ?)", (username, plate))
        conn.commit()
        return jsonify({"message": f"Vehicle {plate} linked to {username}"})
    except sqlite3.IntegrityError:
        return jsonify({"message": "Vehicle already exists"}), 400

# -------------------- ANPR SYSTEM --------------------
def process_anpr():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plate_number = pytesseract.image_to_string(gray, config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        plate_number = plate_number.strip()
        if plate_number:
            print(f"Detected Plate: {plate_number}")
            check_vehicle(plate_number)

        time.sleep(1)

# -------------------- VEHICLE AUTHENTICATION --------------------
def check_vehicle(plate):
    cursor.execute("SELECT username FROM vehicles WHERE plate=?", (plate,))
    result = cursor.fetchone()

    if result:
        print(f"Access Granted: {plate}")
        lcd_display(f"Access Granted: {plate}")
        open_barrier()
    else:
        print(f"Access Denied: {plate}")
        lcd_display("Access Denied")
        GPIO.output(BUZZER, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(BUZZER, GPIO.LOW)

# -------------------- BOOM BARRIER CONTROL --------------------
def open_barrier():
    GPIO.output(RELAY_OPEN, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(RELAY_OPEN, GPIO.LOW)

def close_barrier():
    GPIO.output(RELAY_CLOSE, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(RELAY_CLOSE, GPIO.LOW)

# -------------------- EXIT GATE (Ultrasonic Sensor) --------------------
def exit_gate():
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    
    while True:
        distance = float(ser.readline().decode().strip())
        if distance < 15:
            print("Vehicle exiting...")
            lcd_display("Exit Detected")
            time.sleep(2)
            close_barrier()

# -------------------- MANUAL OVERRIDE --------------------
def manual_override():
    while True:
        if GPIO.input(BUTTON_OPEN) == GPIO.HIGH:
            open_barrier()
        if GPIO.input(BUTTON_CLOSE) == GPIO.HIGH:
            close_barrier()
        time.sleep(0.5)

# -------------------- START SYSTEM --------------------
if __name__ == '__main__':
    import threading

    anpr_thread = threading.Thread(target=process_anpr)
    exit_thread = threading.Thread(target=exit_gate)
    manual_thread = threading.Thread(target=manual_override)

    anpr_thread.start()
    exit_thread.start()
    manual_thread.start()

    app.run(debug=True, host='0.0.0.0')
