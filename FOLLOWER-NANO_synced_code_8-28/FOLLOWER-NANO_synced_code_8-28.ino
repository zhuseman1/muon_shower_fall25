// WORKING CODE WITH MASTER-UNO_synced_code_8-28

#include <Wire.h>

// === CONFIGURATION ===
#define SLAVE_ADDRESS 0x08  // Change for each Nano
#define SLAVE_ID      1     // Unique ID for this Nano

volatile bool pulseDetected = false;
volatile unsigned long pulseTimestamp = 0;

volatile bool syncDetected = false;
volatile unsigned long syncTimestamp = 0;

volatile unsigned long lastPulseTime = 0;
volatile unsigned long lastSyncTime = 0;

unsigned long startupTime = 0;
bool startupSent = false;

void sendData();
void pulseISR();
void syncISR();

void setup() {
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendData);

  pinMode(2, INPUT);  // Pulse input
  pinMode(3, INPUT);  // Sync input

  attachInterrupt(digitalPinToInterrupt(2), pulseISR, FALLING);
  attachInterrupt(digitalPinToInterrupt(3), syncISR, RISING);

  Serial.begin(9600);

  startupTime = micros();  // ⏱️ Save boot time
  Serial.print("Nano ");
  Serial.print(SLAVE_ID);
  Serial.print(" Start Time: ");
  Serial.println(startupTime);
}

void loop() {
  // No main loop logic needed
}

void pulseISR() {
  unsigned long now = micros();
  if (!pulseDetected && (now - lastPulseTime > 5000)) {
    pulseTimestamp = now;
    pulseDetected = true;
    lastPulseTime = now;
  }
}

void syncISR() {
  unsigned long now = micros();
  if (!syncDetected && (now - lastSyncTime > 5000)) {
    syncTimestamp = now;
    syncDetected = true;
    lastSyncTime = now;
  }
}

void sendData() {
  unsigned long timestampToSend = 0xFFFFFFFF;
  byte typeToSend = 0;

  if (!startupSent) {
    timestampToSend = startupTime;
    typeToSend = 3;  // Special type for startup time
    startupSent = true;
  } else if (pulseDetected) {
    timestampToSend = pulseTimestamp;
    typeToSend = 1;
    pulseDetected = false;
  } else if (syncDetected) {
    timestampToSend = syncTimestamp;
    typeToSend = 2;
    syncDetected = false;
  }

  Wire.write((byte *)&timestampToSend, sizeof(timestampToSend));  // 4 bytes
  Wire.write(SLAVE_ID);                                           // 1 byte
  Wire.write(typeToSend);                                         // 1 byte

  if (typeToSend != 0) {
    Serial.print("Sent ");
    if (typeToSend == 1) Serial.print("Pulse");
    else if (typeToSend == 2) Serial.print("Sync");
    else if (typeToSend == 3) Serial.print("Startup");
    Serial.print(" Timestamp: ");
    Serial.println(timestampToSend);
  }
}
