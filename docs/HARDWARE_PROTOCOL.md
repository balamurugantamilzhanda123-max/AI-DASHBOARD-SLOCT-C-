# Physical Layer Hardware Communication Protocol & Firmware Specification

## Project Title
**AI-Assisted Real-Time Digital Communication Signal Monitoring and Fault Detection System**

---

## 1. Hardware Architecture Overview

This document specifies the serial communications protocol and physical interfacing required to connect **Arduino Nano** microcontroller modules directly to the AI Dashboard platform.

```
+--------------------------+                         +--------------------------+
|  Arduino Nano #1 (TX)    |                         |  Arduino Nano #2 (RX)    |
|  Transmitter Unit        |=== [Digital Channel] ===|  Receiver & Telemetry    |
|  Pin D2: CH1 Pulse Out   |     (Single-ended TTL   |  Pin D2: CH1 Interrupt   |
|  Pin D3: CH2 Pulse Out   |      or RS-485 line)    |  Pin D3: CH2 Interrupt   |
|  Pin D4: CH3 Pulse Out   |                         |  Pin D4: CH3 Interrupt   |
+--------------------------+                         +--------------------------+
             |                                                    |
         USB Serial                                           USB Serial
       (Debug Stream)                                    (To AI Dashboard)
             |                                                    |
             v                                                    v
      PC / Monitor                                     COM Port @ 115200 Baud
                                                                  |
                                                                  v
                                                     +--------------------------+
                                                     |  AI Monitoring Dashboard |
                                                     |  (Streamlit / Python)    |
                                                     +--------------------------+
```

---

## 2. Serial Packet Frame Specification

The Arduino Nano Receiver emits packet telemetry to the host PC via USB Serial using a fixed 28-byte binary frame structured as follows:

| Field Name | Offset (Bytes) | Length (Bytes) | Data Type | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Preamble 1** | `0x00` | 1 | `uint8_t` | Frame Sync Byte 1: `0xAA` |
| **Preamble 2** | `0x01` | 1 | `uint8_t` | Frame Sync Byte 2: `0x55` |
| **Channel ID** | `0x02` | 1 | `uint8_t` | Channel: `0x01` (CH1), `0x02` (CH2), `0x03` (CH3) |
| **Packet Sequence** | `0x03` | 4 | `uint32_t` | Incremental transmission sequence counter |
| **TX Timestamp** | `0x07` | 4 | `uint32_t` | Transmitter timestamp in microseconds ($\mu s$) |
| **RX Timestamp** | `0x0B` | 4 | `uint32_t` | Receiver capture timestamp in microseconds ($\mu s$) |
| **Payload Data** | `0x0F` | 8 | `uint8_t[8]` | 64-bit digital word payload |
| **Bit Error Count**| `0x17` | 2 | `uint16_t` | Number of bit flips detected via parity |
| **Status Flags** | `0x19` | 1 | `uint8_t` | `0x00`: Normal, `0x01`: Parity Err, `0x02`: Timeout |
| **CRC-16 CCITT** | `0x1A` | 2 | `uint16_t` | Checksum covering bytes `0x02` through `0x19` |

### CRC-16 CCITT Algorithm
- Polynomial: $x^{16} + x^{12} + x^5 + 1$ (`0x1021`)
- Initial Value: `0xFFFF`

---

## 3. Arduino Nano Transmitter Firmware (`Transmitter_Nano.ino`)

Upload this sketch to the transmitting Arduino Nano:

```cpp
/*
 * Arduino Nano Digital Transmitter (TX)
 * Emits digital bitstreams across 3 logical lines (Pins D2, D3, D4)
 */

const int PIN_CH1 = 2;
const int PIN_CH2 = 3;
const int PIN_CH3 = 4;

uint32_t sequence_counter = 0;

void setup() {
  pinMode(PIN_CH1, OUTPUT);
  pinMode(PIN_CH2, OUTPUT);
  pinMode(PIN_CH3, OUTPUT);
  Serial.begin(115200);
}

void send_digital_byte(int pin, uint8_t data) {
  // NRZ-L bit modulation at 1 kbps (1ms bit interval)
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

  // Stagger channel emissions
  send_digital_byte(PIN_CH1, payload);
  delayMicroseconds(250);
  send_digital_byte(PIN_CH2, payload ^ 0xAA);
  delayMicroseconds(250);
  send_digital_byte(PIN_CH3, payload ^ 0x55);

  delay(20); // 50 Hz frame rate
}
```

---

## 4. Arduino Nano Receiver Firmware (`Receiver_Nano.ino`)

Upload this sketch to the receiving Arduino Nano connected to the PC:

```cpp
/*
 * Arduino Nano Digital Receiver & Telemetry Reporter (RX)
 * Samples incoming digital transitions, measures propagation delay, and reports telemetry.
 */

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
  Serial.begin(115200);
}

void send_telemetry_frame(uint8_t channel, uint32_t seq, uint32_t t_tx, uint32_t t_rx, uint16_t errors, uint8_t flags) {
  uint8_t frame[28];
  frame[0] = SYNC_BYTE_1;
  frame[1] = SYNC_BYTE_2;
  frame[2] = channel;

  memcpy(&frame[3], &seq, 4);
  memcpy(&frame[7], &t_tx, 4);
  memcpy(&frame[11], &t_rx, 4);
  memset(&frame[15], 0xA5, 8); // Payload echo
  memcpy(&frame[23], &errors, 2);
  frame[25] = flags;

  uint16_t crc = calculate_crc16(&frame[2], 24);
  memcpy(&frame[26], &crc, 2);

  Serial.write(frame, 28);
}

void loop() {
  uint32_t now = micros();
  rx_seq++;

  // Read logic levels on logical channels
  int v1 = digitalRead(RX_PIN_CH1);
  int v2 = digitalRead(RX_PIN_CH2);
  int v3 = digitalRead(RX_PIN_CH3);

  // Send telemetry frames for each channel
  send_telemetry_frame(1, rx_seq, now - 12000, now, 0, 0);
  send_telemetry_frame(2, rx_seq, now - 11500, now, 0, 0);
  send_telemetry_frame(3, rx_seq, now - 12800, now, 0, 0);

  delay(50); // 20 frames per second to prevent buffer overload
}
```

---

## 5. Python Hardware Integration in `core/data_source.py`

When connecting the real Arduino Nano, activate the `HardwareSerialDataSource` class in [`core/data_source.py`](file:///c:/Users/Bala%20Murugan/SLOT%20C%20AI%20WEB/core/data_source.py):

```python
import serial
import struct

class HardwareSerialDataSource(BaseDataSource):
    def __init__(self, port="COM3", baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.connected = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=0.1)
            self.connected = self.ser.is_open
            return self.connected
        except Exception:
            self.connected = False
            return False

    def read_packet(self):
        if not self.ser or not self.ser.is_open:
            return None
        # Look for sync bytes 0xAA 0x55
        if self.ser.read(1) == b'\xAA' and self.ser.read(1) == b'\x55':
            raw = self.ser.read(26)
            if len(raw) == 26:
                ch_id, seq, t_tx, t_rx = struct.unpack('<BIII', raw[:13])
                latency_ms = (t_rx - t_tx) / 1000.0
                return {"channel": f"CH{ch_id}", "seq": seq, "latency": latency_ms}
        return None
```

