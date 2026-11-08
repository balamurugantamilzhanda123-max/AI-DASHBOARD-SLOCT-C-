"""
Signal Simulator Module
High-fidelity digital communication signal simulator.
Generates multi-channel realistic digital pulses, models channel physics,
incorporates active injected faults, and dynamically tracks session uptime.
"""

from typing import Dict, Any, List
from datetime import datetime
import random

from core.signal_generator import signal_generator
from core.fault_injector import fault_injector
from core.signal_metrics import calculate_signal_quality_score, calculate_packet_loss_pct, calculate_bit_error_rate


class SignalSimulator:
    """Manages synthetic traffic simulation across CH1, CH2, CH3."""

    def __init__(self):
        self.session_id = f"LIVE-SIM-{datetime.now().strftime('%Y%m%d%H%M')}"
        self.session_start = datetime.now()
        self.channels = ["CH1", "CH2", "CH3"]
        self.packet_counters = {
            "CH1": {"tx": 14200, "rx": 14192, "errors": 3},
            "CH2": {"tx": 15840, "rx": 15830, "errors": 4},
            "CH3": {"tx": 13910, "rx": 13898, "errors": 5},
        }

    def get_uptime_string(self) -> str:
        """Calculates true dynamic elapsed uptime formatted as HHh MMm SSs."""
        elapsed = datetime.now() - self.session_start
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    def read_channel_telemetry(self, channel: str) -> Dict[str, Any]:
        """Generates instantaneous telemetry record for the requested channel."""
        fault_info = fault_injector.get_channel_fault(channel)
        fault_type = fault_info["type"]
        severity = fault_info.get("severity", "INFO")

        tx_delta = random.randint(12, 28)
        self.packet_counters[channel]["tx"] += tx_delta

        if fault_type == "NORMAL":
            rx_delta = tx_delta - (1 if random.random() < 0.05 else 0)
            latency = round(random.uniform(9.0, 14.5), 2)
            ber = round(random.uniform(1e-6, 3e-5), 6)
            loss_pct = round(((tx_delta - rx_delta) / tx_delta) * 100, 2)
            status_text = "OPTIMAL"

        elif fault_type == "PACKET_LOSS":
            drop_ratio = 0.35 if severity in ["HIGH", "CRITICAL"] else 0.18
            rx_delta = int(tx_delta * (1.0 - drop_ratio))
            latency = round(random.uniform(22.0, 48.0), 2)
            ber = round(random.uniform(4e-4, 1.8e-3), 5)
            loss_pct = round(((tx_delta - rx_delta) / tx_delta) * 100, 2)
            status_text = "PACKET LOSS DETECTED"

        elif fault_type == "BIT_CORRUPTION":
            rx_delta = tx_delta
            self.packet_counters[channel]["errors"] += random.randint(2, 6)
            latency = round(random.uniform(14.0, 22.0), 2)
            ber = round(random.uniform(1.5e-3, 5.8e-3), 5)
            loss_pct = 0.0
            status_text = "BIT CORRUPTION ACTIVE"

        elif fault_type == "TRANSMISSION_DELAY":
            rx_delta = tx_delta
            latency = round(random.uniform(95.0, 220.0), 2)
            ber = round(random.uniform(1e-5, 6e-5), 5)
            loss_pct = 0.0
            status_text = "HIGH LATENCY LAG"

        elif fault_type == "BURST_ERROR":
            rx_delta = int(tx_delta * 0.90)
            self.packet_counters[channel]["errors"] += random.randint(8, 18)
            latency = round(random.uniform(40.0, 85.0), 2)
            ber = round(random.uniform(1.2e-2, 3.5e-2), 4)
            loss_pct = round(((tx_delta - rx_delta) / tx_delta) * 100, 2)
            status_text = "BURST ERROR CLUSTER"
        else:
            rx_delta = tx_delta
            latency = 12.0
            ber = 1e-5
            loss_pct = 0.0
            status_text = "OPTIMAL"

        self.packet_counters[channel]["rx"] += rx_delta
        total_tx = self.packet_counters[channel]["tx"]
        total_rx = self.packet_counters[channel]["rx"]
        overall_loss = calculate_packet_loss_pct(total_tx - total_rx, total_tx)

        quality = calculate_signal_quality_score(
            loss_pct=overall_loss,
            ber=ber,
            latency_ms=latency,
            nominal_latency_ms=14.0
        )

        return {
            "channel": channel,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "status": status_text,
            "fault_type": fault_type,
            "fault_severity": severity,
            "tx_packets": total_tx,
            "rx_packets": total_rx,
            "packet_loss_pct": overall_loss,
            "recent_loss_pct": loss_pct,
            "error_count": self.packet_counters[channel]["errors"],
            "latency_ms": latency,
            "ber": ber,
            "signal_quality_pct": quality,
            "is_healthy": (fault_type == "NORMAL" and overall_loss < 2.0 and latency < 35.0)
        }

    def read_all_channels_telemetry(self) -> Dict[str, Dict[str, Any]]:
        return {ch: self.read_channel_telemetry(ch) for ch in self.channels}

    def get_waveform_data(self, channel: str, num_bits: int = 16) -> Dict[str, Any]:
        fault_info = fault_injector.get_channel_fault(channel)
        bits = signal_generator.generate_random_bits(num_bits=num_bits)
        return signal_generator.synthesize_waveform(
            bits=bits,
            fault_type=fault_info["type"],
            fault_severity=fault_info.get("severity", "INFO"),
            channel_name=channel
        )


# Global Singleton instance
signal_simulator = SignalSimulator()

