// WORKING CODE WITH TIME STAMP 8/28

#include <Wire.h>

// ===== CONFIGURATION =====
const unsigned long runDuration = 10UL * 60UL * 6000000UL;  // 60 minutes
const unsigned long syncInterval = 10UL * 1000000UL;        // 5 minutes
const int SYNC_PIN = 6;

const byte nanoAddresses[] = {
  0x08, 0x09, 0x0A, 0x0B,
  0x0C, 0x0D, 0x0E, 0x0F
};

const int numNanos = sizeof(nanoAddresses) / sizeof(nanoAddresses[0]);

unsigned long startTime = 0;
unsigned long lastSyncTime = 0;

void setup() {
  Wire.begin();         
  Serial.begin(9600);   
  pinMode(SYNC_PIN, OUTPUT);
  digitalWrite(SYNC_PIN, LOW);
  startTime = micros(); 

  // ⏱️ Print master start time
  Serial.print("MST: "); // Server Start Time
  Serial.println(startTime);
}

void loop() {
  unsigned long now = micros();

  if (now - startTime >= runDuration) {
    Serial.println("Done");
    while (true);
  }

  if (now - lastSyncTime >= syncInterval || lastSyncTime == 0) {
    sendSyncPulse();
    delay(10);
    lastSyncTime = now;
  }

  // Always poll the Nanos for data
  requestTimestamps();
}

void sendSyncPulse() {
  unsigned long now = micros();
  Serial.print("MS: ");  // Master Sync timestamp
  Serial.println(now);

  digitalWrite(SYNC_PIN, HIGH);
  delay(10);  // 10ms sync pulse
  digitalWrite(SYNC_PIN, LOW);
}


void requestTimestamps() {
  for (int i = 0; i < numNanos; i++) {
    byte addr = nanoAddresses[i];
    Wire.requestFrom(addr, (uint8_t)6);  // 4 bytes timestamp + 1 byte ID + 1 byte type

    if (Wire.available() == 6) {
      unsigned long timestamp = 0;
      for (int j = 0; j < 4; j++) {
        ((byte *)&timestamp)[j] = Wire.read();
      }
      byte slaveID = Wire.read();
      byte dataType = Wire.read();

      if (timestamp == 0xFFFFFFFF) {
        continue;  // Skip if no new event
      }

      Serial.print(slaveID);
      Serial.print(",");

      if (dataType == 1) {
        Serial.print("PT,"); // Pulse Timestamp 
      } else if (dataType == 2) {
        // Serial.print("ST,"); // Sync Timestamp
      } else if (dataType == 3) {
        Serial.print("Start, "); // Start Time
      } else {
        Serial.print("UT "); // Unknown Type
        Serial.print(dataType);
        Serial.print(": ");
      }
      Serial.println(timestamp);
    }
  }
}

// Make it able to be easily transferable to a google sheet (minimal words in outputs)