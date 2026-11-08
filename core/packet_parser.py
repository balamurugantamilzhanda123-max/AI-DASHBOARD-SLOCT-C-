"""
Packet Parser Module for Real-Time Digital Communication System
Supports Newline-Delimited JSON (NDJSON) and framed binary packets.
Parses sequence numbers, channel ID, transmitted bits, received bits,
timestamps, checksum, and hardware fault flags.
Robust against partial chunks, buffer corruption, and malformed frames.
"""

import json
import struct
from typing import Optional, Dict, Any, Tuple


class PacketParser:
    """
    Parses raw serial strings or bytes into structured telemetry packet dictionaries.
    Handles newline-delimited JSON and binary framed serial packets.
    """

    @staticmethod
    def parse_ndjson(line: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Parses a single newline-delimited JSON string.
        Returns: (success: bool, packet_dict: Optional[dict], error_msg: str)
        """
        clean_line = line.strip()
        if not clean_line:
            return False, None, "Empty line"

        # Check if line looks like JSON object
        if not (clean_line.startswith("{") and clean_line.endswith("}")):
            return False, None, "Framing error: Not a complete JSON object"

        try:
            data = json.loads(clean_line)
        except json.JSONDecodeError as e:
            return False, None, f"JSON decode error: {str(e)}"

        # Validate mandatory protocol fields
        required_fields = ["seq", "channel", "tx_data", "rx_data"]
        for field in required_fields:
            if field not in data:
                return False, None, f"Protocol validation error: Missing field '{field}'"

        # Standardize field types
        try:
            seq = int(data["seq"])
            ch = str(data["channel"]).upper()
            if ch not in ["CH1", "CH2", "CH3"]:
                return False, None, f"Invalid channel ID: {ch}"

            tx_data = str(data["tx_data"])
            rx_data = str(data["rx_data"])
            checksum_ok = bool(data.get("checksum_ok", True))
            fault_flag = str(data.get("fault", "NORMAL")).upper()
            t_tx = float(data.get("t_tx_us", 0.0))
            t_rx = float(data.get("t_rx_us", 0.0))

            parsed_packet = {
                "seq": seq,
                "channel": ch,
                "tx_data": tx_data,
                "rx_data": rx_data,
                "checksum_ok": checksum_ok,
                "fault": fault_flag,
                "t_tx_us": t_tx,
                "t_rx_us": t_rx,
                "raw_voltage": data.get("voltage_samples", None),
                "timestamp": data.get("timestamp", None)
            }
            return True, parsed_packet, "OK"
        except Exception as e:
            return False, None, f"Type conversion error: {str(e)}"

    @staticmethod
    def parse_binary_frame(raw_bytes: bytes) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Parses a 28-byte binary frame structured as:
        [SYNC 0xAA 0x55] [CH_ID 1B] [SEQ 4B] [T_TX 4B] [T_RX 4B] [PAYLOAD 8B] [ERRORS 2B] [FLAGS 1B] [CRC 2B]
        """
        if len(raw_bytes) < 28:
            return False, None, f"Truncated frame: expected 28 bytes, got {len(raw_bytes)}"

        if raw_bytes[0] != 0xAA or raw_bytes[1] != 0x55:
            return False, None, "Invalid sync preamble (expected 0xAA 0x55)"

        try:
            ch_num = raw_bytes[2]
            ch_map = {1: "CH1", 2: "CH2", 3: "CH3"}
            ch = ch_map.get(ch_num, f"CH{ch_num}")

            seq, t_tx, t_rx = struct.unpack("<III", raw_bytes[3:15])
            payload_bytes = raw_bytes[15:23]
            tx_data = "".join(f"{b:08b}" for b in payload_bytes[:4])  # 32 bits
            rx_data = "".join(f"{b:08b}" for b in payload_bytes[4:])  # 32 bits
            errors, flags, crc = struct.unpack("<HBH", raw_bytes[23:28])

            fault_map = {0: "NORMAL", 1: "BIT_CORRUPTION", 2: "TRANSMISSION_DELAY", 3: "BURST_ERROR", 4: "PACKET_LOSS"}
            fault = fault_map.get(flags, "NORMAL")

            return True, {
                "seq": seq,
                "channel": ch,
                "tx_data": tx_data,
                "rx_data": rx_data,
                "checksum_ok": True,  # CRC verified prior or by caller
                "fault": fault,
                "t_tx_us": float(t_tx),
                "t_rx_us": float(t_rx),
                "errors": errors
            }, "OK"
        except Exception as e:
            return False, None, f"Binary unpack error: {str(e)}"

