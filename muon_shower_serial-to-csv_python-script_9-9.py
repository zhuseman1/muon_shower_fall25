# Go to folder with python script in it and type 'cmd' into file path
# Copy this into command prompt: py muon_shower_serial-to-csv_python-script_9-9.py

import serial
import csv
import time
from datetime import datetime

# ---- Configuration ----
SERIAL_PORT = 'COM4'            # Replace with your actual port
BAUD_RATE = 9600                # Match your Arduino's baud rate
CSV_FILE = 'code_test_11-20.csv'

# ---- Record Script Start Time ----
start_time = datetime.now()
start_time_str = start_time.isoformat(timespec='seconds')
start_timestamp = int(time.time())
print(f"Logging started at {start_time_str} (Unix: {start_timestamp})")

# Store nano start times here
nano_start_times = {}

# ---- Serial to CSV Logger ----
try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser, \
         open(CSV_FILE, mode='w', newline='') as file:

        # Write start time as a comment
        file.write(f"# Logging started at {start_time_str}\n")
        writer = csv.writer(file)

        while True:
            line = ser.readline().decode('utf-8', errors='replace').strip()

            if line:
                # Check for "Done" message (case-insensitive)
                if line.lower() == "done":
                    file.write("# Done\n")
                    print("Received 'Done' message. Logging finished.")
                    break

                # Handle master start time (MST), sync time (MS), etc.
                if line.startswith("MST:"):
                    timestamp = line.replace("MST:", "").strip()
                    writer.writerow(["MasterStart", timestamp])
                    print(f"Logged: MasterStart, {timestamp}")

                elif line.startswith("MS:"):
                    timestamp = line.replace("MS:", "").strip()
                    writer.writerow(["MasterSync", timestamp])
                    print(f"Logged: MasterSync, {timestamp}")

                elif any(prefix in line for prefix in [",PT,", ",ST,", "Start:", "UT "]):
                    try:
                        parts = line.split(",")
                        if len(parts) >= 3:
                            slave_id = parts[0].strip()
                            event_type = parts[1].strip()
                            timestamp = ",".join(parts[2:]).strip()

                            # Detect and record Nano start times
                            if event_type.startswith("Start"):
                                nano_start_times[slave_id] = timestamp
                                print(f"Recorded start time for Nano {slave_id}: {timestamp}")

                            writer.writerow([slave_id, event_type, timestamp])
                            print(f"Logged: {slave_id}, {event_type}, {timestamp}")
                        else:
                            raise ValueError
                    except ValueError:
                        print(f"Skipping malformed nano line: {line}")

                else:
                    # Unknown format – log anyway
                    print(f"Unknown line format: {line}")

        # ---- After logging ends, write Nano start times ----
        if nano_start_times:
            file.write("\n# Nano Start Times\n")
            for nano_id, start_time in nano_start_times.items():
                file.write(f"# Nano {nano_id} Start: {start_time}\n")
            print("\nSaved all Nano start times at end of file.")

except serial.SerialException as e:
    print(f"Serial error: {e}")
except KeyboardInterrupt:
    print("Logging stopped by user.")

