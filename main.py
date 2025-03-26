import cv2
import subprocess
import json
import pandas as pd
import RPi.GPIO as GPIO
import time
from smbus2 import SMBus
from RPLCD.i2c import CharLCD

# ==== GPIO SETUP ====
RELAY_OPEN = 17   # GPIO pin for OPEN relay
RELAY_CLOSE = 27  # GPIO pin for CLOSE relay
BUZZER_PIN = 22   # Buzzer for unauthorized access

TRIG_1 = 23  # Ultrasonic sensor 1 (Before Gate)
ECHO_1 = 24

TRIG_2 = 5  # Ultrasonic sensor 2 (After Gate)
ECHO_2 = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup([RELAY_OPEN, RELAY_CLOSE, BUZZER_PIN, TRIG_1, TRIG_2], GPIO.OUT)
GPIO.setup([ECHO_1, ECHO_2], GPIO.IN)

# Default States
GPIO.output(RELAY_OPEN, GPIO.LOW)
GPIO.output(RELAY_CLOSE, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

# ==== I2C LCD SETUP ====
lcd = CharLCD(i2c_expander="PCF8574", address=0x27, port=1, cols=16, rows=2, dotsize=8)

def lcd_display(message):
    """ Display a message on the LCD """
    lcd.clear()
    lcd.write_string(message)
    time.sleep(2)

# ==== LOAD AUTHORIZED VEHICLES ====
EXCEL_FILE = "authorized_vehicles.xlsx"
authorized_plates = []

def load_authorized_plates():
    """ Load vehicle plate numbers from an Excel file """
    global authorized_plates
    try:
        df = pd.read_excel(EXCEL_FILE)
        authorized_plates = df.iloc[:, 0].astype(str).str.upper().tolist()
    except Exception as e:
        print(f"Error loading authorized plates: {e}")

load_authorized_plates()

# ==== IMAGE CAPTURE & OPENALPR ANPR ====
def capture_plate():
    """ Capture an image, process it using OpenALPR, and return the detected plate number """
    cap = cv2.VideoCapture(0)  # Use first webcam
    try:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not capture image")
            return None

        image_path = "/tmp/car_plate.jpg"
        cv2.imwrite(image_path, frame)

        # Run OpenALPR via subprocess
        command = f"alpr -c us -j {image_path}"  # Change 'us' to your country code
        result = subprocess.run(command.split(), capture_output=True, text=True)

        try:
            data = json.loads(result.stdout)
            if data['results']:
                plate_number = data['results'][0]['plate']
                return plate_number.upper()
            else:
                return None
        except json.JSONDecodeError:
            print("Error parsing OpenALPR output")
            return None
    except Exception as e:
        print(f"Error capturing plate: {e}")
        return None
    finally:
        cap.release()

# ==== ULTRASONIC SENSOR FUNCTIONS ====
def vehicle_detected(sensor_trig, sensor_echo, distance_threshold):
    """ Returns True if a vehicle is detected within the given distance threshold """
    GPIO.output(sensor_trig, True)
    time.sleep(0.00001)
    GPIO.output(sensor_trig, False)

    start_time = time.time()
    while GPIO.input(sensor_echo) == 0:
        if time.time() - start_time > 0.1:
            return False

    start_time = time.time()
    while GPIO.input(sensor_echo) == 1:
        if time.time() - start_time > 0.1:
            return False

    distance = (time.time() - start_time) * 17150
    return distance < distance_threshold

# ==== BOOM BARRIER CONTROL ====
def open_barrier():
    """ Opens the boom barrier """
    print("Opening Barrier...")
    GPIO.output(RELAY_OPEN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(RELAY_OPEN, GPIO.LOW)

def close_barrier():
    """ Closes the boom barrier """
    print("Closing Barrier...")
    GPIO.output(RELAY_CLOSE, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(RELAY_CLOSE, GPIO.LOW)

# ==== MAIN SYSTEM LOOP ====
try:
    while True:
        print("Waiting for vehicle...")
        lcd_display("Waiting for Car...")

        while not vehicle_detected(TRIG_1, ECHO_1, 50):
            time.sleep(0.5)

        print("Vehicle Detected! Running ANPR...")
        lcd_display("Scanning Plate...")

        plate_number = capture_plate()

        if plate_number:
            print(f"Detected Plate: {plate_number}")

            if plate_number in authorized_plates:
                print("Access Granted!")
                lcd_display("Access Granted!")
                open_barrier()

                print("Waiting for vehicle to pass fully...")
                while vehicle_detected(TRIG_2, ECHO_2, 80):  # Ensure vehicle has left
                    time.sleep(0.5)

                close_barrier()
                lcd_display("Gate Closed!")
            else:
                print("Access Denied!")
                lcd_display("Access Denied!")
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(BUZZER_PIN, GPIO.LOW)
        else:
            print("No Plate Detected!")
            lcd_display("No Plate Found!")

        time.sleep(3)

except KeyboardInterrupt:
    print("Shutting down...")
    GPIO.cleanup()
