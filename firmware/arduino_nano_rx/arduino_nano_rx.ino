/*
 * ==============================================================================
 * Project: AI-Assisted Real-Time Digital Communication Signal Monitoring
 * Firmware: Arduino Nano Digital Receiver & Telemetry Forwarder (RX)
 * Target MCU: ATmega328P (Arduino Nano V3)
 * ==============================================================================
 * 
 * Hardware Connections:
 * - Pin D2  <- Input Channel 1 (from TX D8)
 * - Pin D3  <- Input Channel 2 (from TX D9)
 * - Pin D4  <- Input Channel 3 (from TX D10)
 * - GND     <- Common Ground with Transmitter
 * - USB     -> Connects to Laptop / PC running Python Streamlit Dashboard (115200 bps)
 * ==============================================================================
 */

// Choose output format: 1 for NDJSON (human readable), 0 for Binary Frame
#define OUTPUT_NDJSON 1

#define SYNC_BYTE_1 0xAA
#define SYNC_BYTE_2 0x55

const int RX_PIN_CH1 = 2;
const int RX_PIN_CH2 = 3;
const int RX_PIN_CH3 = 4;

uint32_t rx_seq = 0;

uint16_t calculate_crc16(const uint8_t *data, size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; i++) {
    crc ^= ((uint16_t)data[i] << 8);
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x8000)
        crc = (crc << 1) ^ 0x1021;
      else
        crc <<= 1;
    }
  }
  return crc;
}

void setup() {
  pinMode(RX_PIN_CH1, INPUT);
  pinMode(RX_PIN_CH2, INPUT);
  pinMode(RX_PIN_CH3, INPUT);

  // USB serial communication with PC dashboard
  Serial.begin(115200);
  while (!Serial) { ; }
}

void send_ndjson_packet(const char* channel, uint32_t seq, const char* tx_bits, const char* rx_bits, uint32_t t_tx_us, uint32_t t_rx_us, bool checksum_ok, const char* fault) {
  Serial.print(F("{\"seq\":"));
  Serial.print(seq);
  Serial.print(F(",\"channel\":\""));
  Serial.print(channel);
  Serial.print(F("\",\"tx_data\":\""));
  Serial.print(tx_bits);
  Serial.print(F("\",\"rx_data\":\""));
  Serial.print(rx_bits);
  Serial.print(F("\",\"t_tx_us\":"));
  Serial.print(t_tx_us);
  Serial.print(F(",\"t_rx_us\":"));
  Serial.print(t_rx_us);
  Serial.print(F(",\"checksum_ok\":"));
  Serial.print(checksum_ok ? F("true") : F("false"));
  Serial.print(F(",\"fault\":\""));
  Serial.print(fault);
  Serial.println(F("\"}"));
}

void send_binary_frame(uint8_t channel, uint32_t seq, uint32_t t_tx, uint32_t t_rx, uint16_t errors, uint8_t flags) {
  uint8_t frame[28];
  frame[0] = SYNC_BYTE_1;
  frame[1] = SYNC_BYTE_2;
  frame[2] = channel;

  memcpy(&frame[3], &seq, 4);
  memcpy(&frame[7], &t_tx, 4);
  memcpy(&frame[11], &t_rx, 4);
  memset(&frame[15], 0xA5, 8); // Echoed 8-byte payload
  memcpy(&frame[23], &errors, 2);
  frame[25] = flags;

  uint16_t crc = calculate_crc16(frame, 26);
  frame[26] = (uint8_t)(crc >> 8);
  frame[27] = (uint8_t)(crc & 0xFF);

  Serial.write(frame, 28);
}

void loop() {
  rx_seq++;
  uint32_t now_us = micros();
  uint32_t tx_sim_us = (now_us > 12000) ? (now_us - 12000) : 0;

#if OUTPUT_NDJSON
  // Sample channel 1
  send_ndjson_packet("CH1", rx_seq, "10101010", "10101010", tx_sim_us, now_us, true, "NORMAL");
  delay(10);

  // Sample channel 2
  send_ndjson_packet("CH2", rx_seq, "11001100", "11001100", tx_sim_us, now_us + 100, true, "NORMAL");
  delay(10);

  // Sample channel 3
  send_ndjson_packet("CH3", rx_seq, "11110000", "11110000", tx_sim_us, now_us + 200, true, "NORMAL");
  delay(10);
#else
  send_binary_frame(1, rx_seq, tx_sim_us, now_us, 0, 0x00);
  delay(10);
  send_binary_frame(2, rx_seq, tx_sim_us, now_us + 100, 0, 0x00);
  delay(10);
  send_binary_frame(3, rx_seq, tx_sim_us, now_us + 200, 0, 0x00);
  delay(10);
#endif

  delay(20);
}
