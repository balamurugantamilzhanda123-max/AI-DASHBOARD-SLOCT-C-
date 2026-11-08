/*
 * ==============================================================================
 * Project: AI-Assisted Real-Time Digital Communication Signal Monitoring
 * Firmware: Arduino Nano Digital Transmitter (TX)
 * Target MCU: ATmega328P (Arduino Nano V3)
 * ==============================================================================
 * 
 * Hardware Connections:
 * - Pin D8  -> Logical Channel 1 (CH1 Signal Out)
 * - Pin D9  -> Logical Channel 2 (CH2 Signal Out)
 * - Pin D10 -> Logical Channel 3 (CH3 Signal Out)
 * - GND     -> Common Ground with Receiver Arduino Nano
 * 
 * Generates continuous digital pulse sequences across three logical channels.
 * ==============================================================================
 */

const int PIN_CH1 = 8;
const int PIN_CH2 = 9;
const int PIN_CH3 = 10;

uint32_t sequence_counter = 0;

void setup() {
  pinMode(PIN_CH1, OUTPUT);
  pinMode(PIN_CH2, OUTPUT);
  pinMode(PIN_CH3, OUTPUT);
  
  digitalWrite(PIN_CH1, LOW);
  digitalWrite(PIN_CH2, LOW);
  digitalWrite(PIN_CH3, LOW);

  // Optional TX diagnostic serial
  Serial.begin(115200);
}

void send_digital_byte(int pin, uint8_t data) {
  // NRZ-L bit modulation at 1 kbps (1.0 ms bit interval)
  for (int b = 7; b >= 0; b--) {
    int bit_val = (data >> b) & 0x01;
    digitalWrite(pin, bit_val ? HIGH : LOW);
    delayMicroseconds(1000); // 1.0 ms per bit
  }
  digitalWrite(pin, LOW);
}

void loop() {
  sequence_counter++;
  uint8_t payload = (uint8_t)(sequence_counter & 0xFF);

  // Transmit staggered logical channels
  send_digital_byte(PIN_CH1, payload);
  delayMicroseconds(250);

  send_digital_byte(PIN_CH2, payload ^ 0xAA);
  delayMicroseconds(250);

  send_digital_byte(PIN_CH3, payload ^ 0x55);

  // Frame interval ~50 Hz
  delay(20);
}
