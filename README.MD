

🚗 ANPR-Based Boom Barrier System (Raspberry Pi)

This is a fully offline Automatic Number Plate Recognition (ANPR) system that controls an entry boom barrier using Raspberry Pi, OpenCV, Tesseract OCR, and two ultrasonic sensors.

🚀 It works 100% offline and manages authorized vehicles using an Excel file (authorized_vehicles.xlsx).


---

📌 Features

✅ ANPR (Camera + OCR) recognizes license plates
✅ Barrier opens only for authorized vehicles (stored in an Excel file)
✅ Two ultrasonic sensors:

Before the gate → Detects incoming vehicle (Triggers ANPR)

After the gate → Ensures vehicle has fully passed before closing
✅ I2C LCD for real-time status updates
✅ Buzzer alert for unauthorized vehicles
✅ Uses relays to control Hikvision TMG300 barrier gate
✅ No internet or external database required (Standalone system)



---

🛠 Hardware Requirements

Raspberry Pi 3B+ or later

USB Camera (for ANPR)

Relay Module (for barrier control)

I2C LCD Display (16x2) (for status updates)

Buzzer (for unauthorized access alert)

2x Ultrasonic Sensors (HC-SR04)

Before gate (to detect an incoming vehicle)

After gate (to confirm vehicle has fully passed)




---

📥 Installation

1️⃣ Install Dependencies

Run the following command on Raspberry Pi:

pip install opencv-python pytesseract pandas openpyxl RPi.GPIO smbus2 RPLCD

2️⃣ Prepare the Excel File

Create an Excel file named authorized_vehicles.xlsx with only one column (A) containing plate numbers (uppercase, no spaces).

Example: | Plate Number | |-------------| | MH12AB1234  | | GJ05XY6789  | | DL01ZZ4321  |


---

📌 How It Works

1. Ultrasonic Sensor 1 (Before Gate) detects an incoming vehicle → ANPR is triggered.


2. Camera captures an image and OCR extracts the license plate number.


3. The extracted plate is checked against the Excel file (authorized_vehicles.xlsx).


4. If authorized:

✅ Barrier opens (Relay pulse).

✅ LCD displays "Access Granted".

✅ Barrier remains open until vehicle fully passes the second ultrasonic sensor (After Gate).

✅ Barrier closes only after vehicle is clear.



5. If unauthorized:

❌ Barrier remains closed.

❌ LCD displays "Access Denied".

❌ Buzzer sounds for 2 seconds.



6. System resets and waits for the next vehicle.




---

📜 Running the System

Run the following command on Raspberry Pi:

python3 anpr_gate.py

The system will now operate automatically! 🎯


---

🛠 Wiring Setup


---

🛠 System Customization

🔹 Modify Ultrasonic Sensor Distance Thresholds (Default: 50 cm before, 80 cm after)

vehicle_detected(TRIG_1, ECHO_1, 50)  # Before gate
vehicle_detected(TRIG_2, ECHO_2, 80)  # After gate

🔹 Edit authorized_vehicles.xlsx to add/remove vehicles.


---

📌 Future Enhancements

📌 Improve OCR Accuracy → Use deep learning-based ANPR models.
📌 Add Web Interface → For remote management of vehicles.
📌 Implement Logging → Store entry logs in a database.


---

📌 License
 MIT License Open source, use freely! 🎉


---

📞 Support

For any issues, feel free to create a GitHub Issue or contact me! 🚀
