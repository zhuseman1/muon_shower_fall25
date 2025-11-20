#include <Wire.h>

// List of Nano I2C addresses
const byte nanoAddresses[] = {
  0x08, 0x09, 0x0A, 0x0B,
  0x0C, 0x0D, 0x0E, 0x0F
};
const int numNanos = sizeof(nanoAddresses) / sizeof(nanoAddresses[0]);

const int SYNC_PIN = 6;  // Pin to send sync pulse to all Nanos
unsigned long lastSyncTime = 0;
const unsigned long syncInterval = 30UL * 1000000UL;  // 30 seconds in microseconds

void setup() {
  Wire.begin();  // Start I2C as master
  Serial.begin(9600);
  pinMode(SYNC_PIN, OUTPUT);
  digitalWrite(SYNC_PIN, LOW);
}

void loop() {
  unsigned long now = micros();

  // Send sync pulse every 30 seconds
  if (now - lastSyncTime >= syncInterval || lastSyncTime == 0) {
    sendSyncPulse();
    lastSyncTime = now;
  }

  // Request data from each Nano
  for (int i = 0; i < numNanos; i++) {
    byte addr = nanoAddresses[i];
    Wire.requestFrom(addr, (uint8_t)5);  // Request 4-byte timestamp + 1-byte ID

    if (Wire.available() == 5) {
      unsigned long timestamp = 0;
      for (int j = 0; j < 4; j++) {
        ((byte *)&timestamp)[j] = Wire.read();
      }
      byte slaveID = Wire.read();

      if (timestamp != 0xFFFFFFFF) {
        printFormattedTime(timestamp, slaveID);
      }
    }

    delay(50);  // Prevent I2C bus overload
  }
}

void sendSyncPulse() {
  digitalWrite(SYNC_PIN, HIGH);
  delay(10);  // 10 ms pulse
  digitalWrite(SYNC_PIN, LOW);
}

void printFormattedTime(unsigned long us, byte slaveID) {
  unsigned long hours = us / 3600000000UL;
  unsigned long minutes = (us / 60000000UL) % 60;
  unsigned long seconds = (us / 1000000UL) % 60;
  unsigned long microsRem = us % 1000000UL;

  Serial.print(slaveID);
  Serial.print(",");

  if (hours < 10) Serial.print('0');
  Serial.print(hours); Serial.print(':');

  if (minutes < 10) Serial.print('0');
  Serial.print(minutes); Serial.print(':');

  if (seconds < 10) Serial.print('0');
  Serial.print(seconds); Serial.print(':');

  if (microsRem < 100000) Serial.print('0');
  if (microsRem < 10000) Serial.print('0');
  if (microsRem < 1000) Serial.print('0');
  if (microsRem < 100) Serial.print('0');
  if (microsRem < 10) Serial.print('0');
  Serial.println(microsRem);
}