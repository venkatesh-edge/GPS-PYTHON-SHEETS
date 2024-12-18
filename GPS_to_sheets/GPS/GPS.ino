#include <SoftwareSerial.h>

const int GPS_RX_PIN = 2;  // Connect GPS TX to this pin
const int GPS_TX_PIN = 3;  // Connect GPS RX to this pin

SoftwareSerial gpsSerial(GPS_RX_PIN, GPS_TX_PIN);  // Create a SoftwareSerial object

void setup() {
  Serial.begin(9600);         // Initialize serial communication for debugging
  gpsSerial.begin(9600);      // Initialize serial communication with GPS module
}

void loop() {
  while (gpsSerial.available() > 0) {  // Check if data is available to read
    char c = gpsSerial.read();         // Read a character from the GPS module
    Serial.print(c);                   // Print the character to serial monitor
  }
}
