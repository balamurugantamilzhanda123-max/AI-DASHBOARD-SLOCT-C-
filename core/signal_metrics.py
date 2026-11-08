"""
Signal Metrics Formulation Module
Defines standard digital communications mathematical metrics:
- Packet Loss Percentage
- Bit Error Rate (BER)
- Transmission Latency & Jitter
- Signal Quality Index (Standardized ITU-T inspired formulation)
Includes explicit documentation of measurement bounds and clock drift limitations.
"""

from typing import Dict, Any, List
import math


def calculate_packet_loss_pct(missing_packets: int, expected_packets: int) -> float:
    """
    Computes Packet Loss Percentage.
    Formula: (missing_packets / expected_packets) * 100
    Prevents division by zero; clamps output to [0.0, 100.0]%.
    """
    if expected_packets <= 0:
        return 0.0
    loss = (missing_packets / expected_packets) * 100.0
    return round(max(0.0, min(100.0, loss)), 2)


def calculate_bit_error_rate(incorrect_bits: int, total_compared_bits: int) -> float:
    """
    Computes Bit Error Rate (BER).
    Formula: incorrect_bits / total_compared_bits
    """
    if total_compared_bits <= 0:
        return 0.0
    ber = incorrect_bits / total_compared_bits
    return round(max(0.0, min(1.0, ber)), 6)


def calculate_average_latency(delays_ms: List[float]) -> float:
    """
    Computes arithmetic mean of valid latency measurements.
    
    LIMITATION NOTE (Asynchronous Microcontroller Clocks):
    If transmitter and receiver microcontrollers do not share a synchronized hardware
    clock line (e.g. via PPS/NTP or hardware sync trigger), latency measurements represent
    relative delta times with minor drift. Accurate absolute latency requires hardware
    loopback ping (TX -> RX -> ACK) or unified clock master.
    """
    if not delays_ms:
        return 0.0
    valid_delays = [d for d in delays_ms if 0.0 <= d <= 5000.0]  # Filter out anomalies > 5s
    if not valid_delays:
        return 0.0
    return round(sum(valid_delays) / len(valid_delays), 2)


def calculate_signal_quality_score(
    loss_pct: float,
    ber: float,
    latency_ms: float,
    snr_db: float = 30.0,
    nominal_latency_ms: float = 15.0
) -> float:
    """
    Standardized Composite Signal Quality Index (0.0% to 100.0%).
    Formulation:
    1. Base Score = 100.0%
    2. Loss Penalty: w_loss * loss_pct (up to 40% reduction)
    3. BER Penalty: Logarithmic degradation relative to 10^-6 baseline (up to 35% reduction)
    4. Latency Penalty: Surcharge for excess latency above nominal (up to 25% reduction)
    """
    base_score = 100.0

    # Loss penalty (2.5% quality drop per 1% loss)
    loss_penalty = min(40.0, loss_pct * 2.5)

    # BER penalty: BER of 10^-6 -> 0 penalty; BER of 10^-2 -> 35% penalty
    if ber > 1e-6:
        log_factor = (math.log10(ber) - (-6.0)) / ((-2.0) - (-6.0))  # maps [1e-6, 1e-2] to [0, 1]
        ber_penalty = min(35.0, max(0.0, log_factor * 35.0))
    else:
        ber_penalty = 0.0

    # Latency penalty: 0.3% penalty per ms above nominal threshold
    excess_lat = max(0.0, latency_ms - nominal_latency_ms)
    lat_penalty = min(25.0, excess_lat * 0.3)

    # Composite Score
    score = base_score - loss_penalty - ber_penalty - lat_penalty
    return round(max(0.0, min(100.0, score)), 1)

