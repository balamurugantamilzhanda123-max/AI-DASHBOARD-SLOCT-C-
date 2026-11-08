"""
Packet Validator Module for Digital Communication Systems
Implements sequence gap detection, microcontroller reboot/reset handling,
duplicate packet detection, bit comparison (BER), and checksum verification.
"""

from typing import Dict, Any, List, Optional
from collections import deque
import logging

logger = logging.getLogger("PacketValidator")


class ChannelState:
    """Tracks sequence integrity, bit statistics, and latency for a single channel."""

    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self.last_seq: Optional[int] = None
        self.total_received = 0
        self.total_expected = 0
        self.total_missing = 0
        self.total_duplicates = 0
        self.total_checksum_errors = 0
        self.total_compared_bits = 0
        self.total_bit_errors = 0
        self.latency_window = deque(maxlen=60)
        self.recent_fault = "NORMAL"
        self.recent_severity = "INFO"
        self.reset_count = 0
        self.last_packet_time: Optional[float] = None
        self.last_tx_bits: str = ""
        self.last_rx_bits: str = ""
        self.discrepancy_indices: List[int] = []

    def process_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates an incoming packet, updates statistical accumulators,
        and returns validation diagnostic record.
        """
        seq = packet["seq"]
        tx_data = packet.get("tx_data", "")
        rx_data = packet.get("rx_data", "")
        checksum_ok = packet.get("checksum_ok", True)
        fault_flag = packet.get("fault", "NORMAL")

        is_duplicate = False
        is_reset = False
        missing_count = 0

        # 1. Sequence Gap & Reset Analysis
        if self.last_seq is None:
            # First packet anchor
            self.last_seq = seq
            self.total_expected = 1
            self.total_received = 1
        else:
            if seq == self.last_seq + 1:
                # Normal contiguous sequence
                self.total_expected += 1
                self.total_received += 1
                self.last_seq = seq
            elif seq > self.last_seq + 1:
                # Sequence gap detected (Dropped Packets)
                missing_count = seq - (self.last_seq + 1)
                self.total_missing += missing_count
                self.total_expected += (missing_count + 1)
                self.total_received += 1
                self.last_seq = seq
            elif seq == self.last_seq:
                # Duplicate packet retransmission
                is_duplicate = True
                self.total_duplicates += 1
            else:
                # Sequence went backward: Detect microcontroller reboot or sequence wrap
                if seq < 100 and self.last_seq > 500:
                    is_reset = True
                    self.reset_count += 1
                    self.last_seq = seq
                    self.total_expected += 1
                    self.total_received += 1
                else:
                    # Out-of-order delayed frame
                    self.total_received += 1

        # 2. Checksum Verification
        if not checksum_ok:
            self.total_checksum_errors += 1

        # 3. Bit-by-Bit Comparison for Exact BER
        bit_errors = 0
        discrepancies = []
        compare_len = min(len(tx_data), len(rx_data))
        if compare_len > 0:
            for idx in range(compare_len):
                if tx_data[idx] != rx_data[idx]:
                    bit_errors += 1
                    discrepancies.append(idx)
            self.total_compared_bits += compare_len
            self.total_bit_errors += bit_errors

        self.last_tx_bits = tx_data
        self.last_rx_bits = rx_data
        self.discrepancy_indices = discrepancies

        # 4. Latency Extraction
        t_tx = packet.get("t_tx_us", 0.0)
        t_rx = packet.get("t_rx_us", 0.0)
        measured_latency = None
        if t_rx > t_tx and t_tx > 0:
            measured_latency = (t_rx - t_tx) / 1000.0  # Convert us to ms
            self.latency_window.append(measured_latency)

        self.recent_fault = fault_flag

        return {
            "channel": self.channel_id,
            "seq": seq,
            "missing_in_step": missing_count,
            "is_duplicate": is_duplicate,
            "is_reset": is_reset,
            "checksum_ok": checksum_ok,
            "bit_errors": bit_errors,
            "discrepancies": discrepancies,
            "latency_ms": measured_latency
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Computes instantaneous and cumulative channel metrics."""
        # Packet Loss %: (Missing Packets / Expected Packets) * 100
        if self.total_expected > 0:
            loss_pct = round((self.total_missing / self.total_expected) * 100.0, 2)
        else:
            loss_pct = 0.0

        # Bit Error Rate (BER): (Incorrect Bits / Total Compared Bits)
        if self.total_compared_bits > 0:
            ber = round(self.total_bit_errors / self.total_compared_bits, 6)
        else:
            ber = 0.0

        # Average Latency
        if len(self.latency_window) > 0:
            avg_latency = round(sum(self.latency_window) / len(self.latency_window), 2)
        else:
            avg_latency = 12.0  # Nominal baseline

        # Signal Quality Index Calculation (Documented Formula)
        # Quality = 100 - (Loss * 2.5) - (BER penalty) - (Latency penalty)
        ber_penalty = min(35.0, (ber / 0.005) * 35.0) if ber > 0 else 0.0
        lat_penalty = min(25.0, max(0.0, (avg_latency - 20.0) * 0.35))
        loss_penalty = min(40.0, loss_pct * 2.5)
        quality = round(max(0.0, min(100.0, 100.0 - loss_penalty - ber_penalty - lat_penalty)), 1)

        return {
            "channel": self.channel_id,
            "total_received": self.total_received,
            "total_expected": self.total_expected,
            "total_missing": self.total_missing,
            "total_duplicates": self.total_duplicates,
            "total_checksum_errors": self.total_checksum_errors,
            "total_bit_errors": self.total_bit_errors,
            "total_compared_bits": self.total_compared_bits,
            "packet_loss_pct": loss_pct,
            "ber": ber,
            "avg_latency_ms": avg_latency,
            "signal_quality_pct": quality,
            "fault": self.recent_fault,
            "last_tx_bits": self.last_tx_bits,
            "last_rx_bits": self.last_rx_bits,
            "discrepancies": self.discrepancy_indices
        }


class PacketValidator:
    """Multi-channel validator managing CH1, CH2, and CH3."""

    def __init__(self):
        self.channels = {
            "CH1": ChannelState("CH1"),
            "CH2": ChannelState("CH2"),
            "CH3": ChannelState("CH3")
        }

    def validate_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """Routes packet to designated channel state."""
        ch = packet.get("channel", "CH1")
        if ch not in self.channels:
            self.channels[ch] = ChannelState(ch)
        return self.channels[ch].process_packet(packet)

    def get_channel_metrics(self, channel: str) -> Dict[str, Any]:
        if channel in self.channels:
            return self.channels[channel].get_metrics()
        return {}

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        return {ch: state.get_metrics() for ch, state in self.channels.items()}

    def reset(self):
        """Resets all accumulators."""
        for ch in self.channels.values():
            ch.__init__(ch.channel_id)


# Global Singleton instance
packet_validator = PacketValidator()
