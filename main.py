import cv2
import pytesseract
import pandas as pd
import RPi.GPIO as GPIO
import time
from openpyxl import load_workbook
from smbus2 import SMBus
from RPLCD.i2c import CharLCD

# ==== GPIO SETUP ====
RELAY_OPEN = 17   # GPIO pin for OPEN relay
RELAY_CLOSE = 27  # GPIO pin for CLOSE relay
BUZZER_PIN = 22   # Buzzer for unauthorized access

TRIG_1 = 23  # Ultrasonic sensor 1 (Before Gate) - Detects incoming vehicle
ECHO_1 = 24

TRIG_2 = 5  # Ultrasonic sensor 2 (After Gate) - Ensures vehicle has fully passed
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
    lcd.clear()
    lcd.write_string(message)
    time.sleep(2)

# ==== EXCEL FILE FOR AUTHORIZED VEHICLES ====
EXCEL_FILE = "authorized_vehicles.xlsx"

def load_authorized_plates():
    df = pd.read_excel(EXCEL_FILE)
    return df.iloc[:, 0].astype(str).str.upper().tolist()

# ==== IMAGE CAPTURE & OCR ====
def capture_plate():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Could not capture image")
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    plate_text = pytesseract.image_to_string(thresh, config='--psm 8')
    plate_text = ''.join(filter(str.isalnum, plate_text)).upper()

    return plate_text

# ==== ULTRASONIC SENSOR FUNCTIONS ====
def vehicle_detected(sensor_trig, sensor_echo, distance_threshold):
    """ Returns True if a vehicle is detected within the given distance threshold """
    GPIO.output(sensor_trig, True)
    time.sleep(0.00001)
    GPIO.output(sensor_trig, False)

    start_time, end_time = 0, 0
    while GPIO.input(sensor_echo) == 0:
        start_time = time.time()
    while GPIO.input(sensor_echo) == 1:
        end_time = time.time()

    distance = (end_time - start_time) * 17150
    return distance < distance_threshold

# ==== BOOM BARRIER CONTROL ====
def open_barrier():
    print("Opening Barrier...")
    GPIO.output(RELAY_OPEN, GPIO.HIGH)
    time.sleep(0.5)  # Pulse to trigger relay
    GPIO.output(RELAY_OPEN, GPIO.LOW)

def close_barrier():
    print("Closing Barrier...")
    GPIO.output(RELAY_CLOSE, GPIO.HIGH)
    time.sleep(0.5)  # Pulse to trigger relay
    GPIO.output(RELAY_CLOSE, GPIO.LOW)

# ==== MAIN SYSTEM LOOP ====
try:
    while True:
        print("Waiting for vehicle...")
        lcd_display("Waiting for Car...")

        # 🔹 WAIT UNTIL VEHICLE ARRIVES (BEFORE THE GATE)
        while not vehicle_detected(TRIG_1, ECHO_1, 50):  # Detects vehicle within 50 cm before gate
            time.sleep(0.5)

        print("Vehicle Detected! Running ANPR...")
        lcd_display("Scanning Plate...")

        authorized_plates = load_authorized_plates()
        plate_number = capture_plate()

        if plate_number:
            print(f"Detected Plate: {plate_number}")

            if plate_number in authorized_plates:
                print("Access Granted!")
                lcd_display("Access Granted!")
                open_barrier()

                # 🔹 WAIT FOR VEHICLE TO FULLY PASS AFTER THE GATE
                print("Waiting for vehicle to fully pass...")
                while not vehicle_detected(TRIG_2, ECHO_2, 80):  # Ensures vehicle has fully passed beyond 80 cm
                    time.sleep(0.5)

                close_barrier()
                lcd_display("Gate Closed!")
            else:
                print("Access Denied!")
                lcd_display("Access Denied!")
                GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Buzzer alert
                time.sleep(2)
                GPIO.output(BUZZER_PIN, GPIO.LOW)

        time.sleep(3)  # Small delay before next scan

except KeyboardInterrupt:
    print("Shutting down...")
    GPIO.cleanup()