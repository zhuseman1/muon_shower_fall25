# Go to folder with python script in it and type 'cmd' into file path
# Copy this into command prompt: py muon_shower_serial-to-csv_python-script_7-1.py

import serial
import csv
import time
from datetime import datetime

# ---- Configuration ----
SERIAL_PORT = 'COM4'            # Replace with your actual port
BAUD_RATE = 9600                # Match your device's baud rate
CSV_FILE = 'syncing_measurement_test_9-9.csv'   # Output CSV file

# ---- Record Script Start Time ----
start_time = datetime.now()
start_time_str = start_time.isoformat(timespec='seconds')
start_timestamp = int(time.time())
print(f"Logging started at {start_time_str} (Unix: {start_timestamp})")

# ---- Serial to CSV Logger ----
try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser, \
         open(CSV_FILE, mode='w', newline='') as file:

        # Write start time as first line
        file.write(f"# Logging started at {start_time_str}\n")
        writer = csv.writer(file)

        while True:
            line = ser.readline().decode('utf-8').strip()

            if line:
                # Check for "Done" message (case-insensitive)
                if line.lower() == "done":
                    file.write("# Done\n")
                    print("Received 'Done' message. Logging finished.")
                    break

                try:
                    slave_id, timestamp = line.split(",")
                    writer.writerow([slave_id.strip(), timestamp.strip()])
                    print(f"Logged: {slave_id}, {timestamp}")
                except ValueError:
                    print(f"Skipping malformed line: {line}")

except serial.SerialException as e:
    print(f"Serial error: {e}")
except KeyboardInterrupt:
    print("Logging stopped by user.")

