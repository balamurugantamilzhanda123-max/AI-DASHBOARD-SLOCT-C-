"""
Realistic Digital Signal Generator for Communication System
Generates digital waveforms (TX / RX), square pulses, binary transitions,
timing jitter, attenuation, and fault distortions (Bit Flips, Bursts, Loss, Delays).
Includes Eye Diagram synthesizer for high-speed signal integrity analysis.
"""

import numpy as np
import random
from typing import Dict, Tuple, List


class DigitalSignalGenerator:
    def __init__(self, bit_rate_bps: int = 1000, samples_per_bit: int = 30):
        self.bit_rate_bps = bit_rate_bps
        self.samples_per_bit = samples_per_bit
        self.bit_duration = 1.0 / bit_rate_bps  # seconds per bit

    def generate_random_bits(self, num_bits: int = 16) -> List[int]:
        """Generates a pseudorandom binary sequence."""
        preamble = [1, 0, 1, 0]
        payload = [random.choice([0, 1]) for _ in range(num_bits - len(preamble))]
        return preamble + payload

    def synthesize_waveform(
        self,
        bits: List[int],
        fault_type: str = "NORMAL",
        fault_severity: str = "INFO",
        channel_name: str = "CH1"
    ) -> Dict:
        """
        Synthesizes TX and RX time-domain waveforms and Eye Diagram traces.
        Returns time array, tx voltage, rx voltage, bit labels, eye traces, and metrics.
        """
        num_bits = len(bits)
        total_samples = num_bits * self.samples_per_bit
        t = np.linspace(0, num_bits * self.bit_duration * 1000, total_samples)  # time in ms

        # Ideal TX Signal (0V to 3.3V logic or normalized 0.0 to 1.0)
        tx_bits = list(bits)
        tx_signal = np.zeros(total_samples)

        for i, b in enumerate(tx_bits):
            start_idx = i * self.samples_per_bit
            end_idx = (i + 1) * self.samples_per_bit
            tx_signal[start_idx:end_idx] = float(b)

        # Build RX bitstream and introduce channel physics + faults
        rx_bits = list(tx_bits)
        discrepancies = []

        noise_std = 0.035
        base_delay_samples = 4
        slew_filter_alpha = 0.35

        if fault_type == "BIT_CORRUPTION":
            num_flips = 1 if fault_severity in ["LOW", "INFO"] else 2
            flip_indices = random.sample(range(4, num_bits), min(num_flips, num_bits - 4))
            for idx in flip_indices:
                rx_bits[idx] = 1 - rx_bits[idx]
                discrepancies.append(idx)
            noise_std = 0.08

        elif fault_type == "BURST_ERROR":
            burst_len = 4 if fault_severity in ["HIGH", "CRITICAL"] else 3
            start_flip = random.randint(4, max(4, num_bits - burst_len))
            for idx in range(start_flip, min(num_bits, start_flip + burst_len)):
                rx_bits[idx] = 1 - rx_bits[idx]
                discrepancies.append(idx)
            noise_std = 0.16

        elif fault_type == "TRANSMISSION_DELAY":
            delay_factor = 12 if fault_severity in ["HIGH", "CRITICAL"] else 8
            base_delay_samples += delay_factor
            noise_std = 0.05

        elif fault_type == "PACKET_LOSS":
            rx_bits = [0] * num_bits
            discrepancies = [i for i, b in enumerate(tx_bits) if b == 1]

        rx_raw = np.zeros(total_samples)
        for i, b in enumerate(rx_bits):
            start_idx = i * self.samples_per_bit
            end_idx = (i + 1) * self.samples_per_bit
            rx_raw[start_idx:end_idx] = float(b)

        if base_delay_samples > 0:
            rx_shifted = np.roll(rx_raw, base_delay_samples)
            rx_shifted[:base_delay_samples] = rx_raw[0]
        else:
            rx_shifted = rx_raw.copy()

        rx_filtered = np.zeros_like(rx_shifted)
        if fault_type == "PACKET_LOSS":
            rx_filtered = np.random.normal(0.02, 0.04, total_samples)
            rx_filtered = np.clip(rx_filtered, 0.0, 0.15)
        else:
            current_val = rx_shifted[0]
            for i in range(total_samples):
                current_val += slew_filter_alpha * (rx_shifted[i] - current_val)
                rx_filtered[i] = current_val

            channel_noise = np.random.normal(0, noise_std, total_samples)
            rx_filtered += channel_noise

        rx_final = np.clip(rx_filtered, -0.15, 1.25)

        # Eye Diagram Generation (2-bit overlapping slices)
        eye_window_len = 2 * self.samples_per_bit
        eye_time_axis = np.linspace(0, 2.0, eye_window_len).tolist()
        eye_traces = []

        for k in range(max(1, num_bits - 2)):
            s_idx = k * self.samples_per_bit
            e_idx = s_idx + eye_window_len
            if e_idx <= len(rx_final):
                eye_traces.append(rx_final[s_idx:e_idx].tolist())

        # Signal Quality Metrics
        if fault_type == "PACKET_LOSS":
            snr_db = round(random.uniform(2.0, 8.0), 1)
            eye_opening_pct = 0.0
            jitter_ns = round(random.uniform(250.0, 480.0), 1)
            signal_quality = round(random.uniform(20.0, 45.0), 1)
        elif fault_type == "BURST_ERROR":
            snr_db = round(random.uniform(9.0, 14.0), 1)
            eye_opening_pct = round(random.uniform(25.0, 45.0), 1)
            jitter_ns = round(random.uniform(120.0, 220.0), 1)
            signal_quality = round(random.uniform(50.0, 68.0), 1)
        elif fault_type == "BIT_CORRUPTION":
            snr_db = round(random.uniform(15.0, 20.0), 1)
            eye_opening_pct = round(random.uniform(50.0, 70.0), 1)
            jitter_ns = round(random.uniform(65.0, 110.0), 1)
            signal_quality = round(random.uniform(68.0, 80.0), 1)
        elif fault_type == "TRANSMISSION_DELAY":
            snr_db = round(random.uniform(21.0, 26.0), 1)
            eye_opening_pct = round(random.uniform(75.0, 88.0), 1)
            jitter_ns = round(random.uniform(140.0, 260.0), 1)
            signal_quality = round(random.uniform(75.0, 85.0), 1)
        else:  # NORMAL
            snr_db = round(random.uniform(28.0, 36.0), 1)
            eye_opening_pct = round(random.uniform(90.0, 98.5), 1)
            jitter_ns = round(random.uniform(15.0, 38.0), 1)
            signal_quality = round(random.uniform(95.0, 99.8), 1)

        transitions = []
        for i in range(1, num_bits):
            if tx_bits[i] != tx_bits[i - 1]:
                edge_type = "RISING" if tx_bits[i] == 1 else "FALLING"
                time_point = i * self.bit_duration * 1000
                transitions.append({"bit_index": i, "type": edge_type, "time_ms": time_point})

        return {
            "channel": channel_name,
            "time_ms": t.tolist(),
            "tx_voltage": tx_signal.tolist(),
            "rx_voltage": rx_final.tolist(),
            "tx_bits": tx_bits,
            "rx_bits": rx_bits,
            "discrepancies": discrepancies,
            "transitions": transitions,
            "eye_diagram": {
                "time_ui": eye_time_axis,  # Unit Intervals (0.0 to 2.0 UI)
                "traces": eye_traces
            },
            "metrics": {
                "snr_db": snr_db,
                "eye_opening_pct": eye_opening_pct,
                "jitter_ns": jitter_ns,
                "signal_quality": signal_quality,
                "rise_time_us": round(random.uniform(1.2, 2.8), 2),
                "fall_time_us": round(random.uniform(1.1, 2.7), 2),
                "v_high": 3.3,
                "v_low": 0.0,
            }
        }


# Global Singleton generator
signal_generator = DigitalSignalGenerator()
