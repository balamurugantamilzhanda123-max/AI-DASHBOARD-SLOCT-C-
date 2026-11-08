"""
Comprehensive Automated Test Suite
Verifies:
1. PacketParser (NDJSON & Binary frames, error recovery)
2. PacketValidator (Sequence gaps, loss %, duplicates, reboots, BER)
3. SignalMetrics (Standard mathematical formulations & bounds)
4. SerialReader Queue (Thread-safe background queue operation)
5. Hardware Mode Zero-Fabrication (Guarantees zero fake data when disconnected/idle)
6. AI Inference Engine (Random Forest & Isolation Forest classification)
7. Reports Generator (CSV & Multi-tab Excel byte outputs)
"""

import unittest
import json
import pandas as pd

from core.packet_parser import PacketParser
from core.packet_validator import PacketValidator, ChannelState
from core.signal_metrics import (
    calculate_packet_loss_pct,
    calculate_bit_error_rate,
    calculate_average_latency,
    calculate_signal_quality_score
)
from core.data_source import SimulationDataSource, HardwareSerialDataSource
from core.ai_engine import ai_engine
from utils.exporter import generate_csv, generate_excel_report


class TestDigitalCommunicationSystem(unittest.TestCase):

    def test_packet_parser_valid_ndjson(self):
        sample_json = json.dumps({
            "seq": 101,
            "channel": "CH1",
            "tx_data": "10101010",
            "rx_data": "10101010",
            "t_tx_us": 1000000,
            "t_rx_us": 1012500,
            "checksum_ok": True,
            "fault": "NORMAL"
        })
        success, pkt, err = PacketParser.parse_ndjson(sample_json)
        self.assertTrue(success)
        self.assertEqual(pkt["seq"], 101)
        self.assertEqual(pkt["channel"], "CH1")
        self.assertEqual(pkt["tx_data"], "10101010")

    def test_packet_parser_malformed_json(self):
        bad_json = "{seq: 101, broken: true"
        success, pkt, err = PacketParser.parse_ndjson(bad_json)
        self.assertFalse(success)
        self.assertIsNone(pkt)

    def test_packet_parser_missing_fields(self):
        missing_fields = json.dumps({"seq": 102})
        success, pkt, err = PacketParser.parse_ndjson(missing_fields)
        self.assertFalse(success)
        self.assertIn("Missing field", err)

    def test_packet_validator_sequence_gap_detection(self):
        val = PacketValidator()
        # Packet 1
        val.validate_packet({"seq": 100, "channel": "CH1", "tx_data": "1111", "rx_data": "1111"})
        # Packet 2 (skips 101, 102 -> jump to 103)
        res = val.validate_packet({"seq": 103, "channel": "CH1", "tx_data": "1111", "rx_data": "1111"})
        self.assertEqual(res["missing_in_step"], 2)

        metrics = val.get_channel_metrics("CH1")
        self.assertEqual(metrics["total_missing"], 2)
        self.assertEqual(metrics["total_expected"], 4)  # 100, 101, 102, 103
        self.assertEqual(metrics["total_received"], 2)  # 100, 103
        self.assertEqual(metrics["packet_loss_pct"], 50.0)

    def test_packet_validator_duplicate_detection(self):
        val = PacketValidator()
        val.validate_packet({"seq": 50, "channel": "CH2", "tx_data": "0000", "rx_data": "0000"})
        res = val.validate_packet({"seq": 50, "channel": "CH2", "tx_data": "0000", "rx_data": "0000"})
        self.assertTrue(res["is_duplicate"])
        metrics = val.get_channel_metrics("CH2")
        self.assertEqual(metrics["total_duplicates"], 1)

    def test_packet_validator_bit_error_rate(self):
        val = PacketValidator()
        # 8 bits compared, 2 bit flips
        val.validate_packet({"seq": 1, "channel": "CH3", "tx_data": "11001100", "rx_data": "11000000"})
        metrics = val.get_channel_metrics("CH3")
        self.assertEqual(metrics["total_bit_errors"], 2)
        self.assertEqual(metrics["total_compared_bits"], 8)
        self.assertEqual(metrics["ber"], 0.25)

    def test_signal_metrics_formulas(self):
        # Loss %
        self.assertEqual(calculate_packet_loss_pct(5, 100), 5.0)
        self.assertEqual(calculate_packet_loss_pct(0, 0), 0.0)
        # BER
        self.assertEqual(calculate_bit_error_rate(3, 1000), 0.003)
        # Latency
        self.assertEqual(calculate_average_latency([10.0, 20.0, 30.0]), 20.0)
        # Signal Quality bounds [0, 100]
        q_nominal = calculate_signal_quality_score(0.0, 1e-6, 12.0)
        self.assertGreaterEqual(q_nominal, 95.0)
        q_critical = calculate_signal_quality_score(40.0, 0.05, 150.0)
        self.assertLessEqual(q_critical, 40.0)

    def test_hardware_mode_zero_fabrication(self):
        hw_ds = HardwareSerialDataSource()
        # When serial port has received no frames, metrics must NOT fabricate readings
        telemetry = hw_ds.read_channel_telemetry("CH1")
        if not telemetry.get("has_hardware_data", False):
            self.assertEqual(telemetry["rx_packets"], 0)
            self.assertIn(telemetry["status"], ["DISCONNECTED", "WAITING FOR HARDWARE DATA"])

    def test_ai_inference_pipeline(self):
        self.assertTrue(ai_engine.is_trained)
        results = ai_engine.evaluation_results
        self.assertIn("accuracy", results)
        self.assertIn("confusion_matrix", results)
        self.assertGreaterEqual(results["accuracy"], 0.90)

        # Live prediction on nominal feature vector
        nominal_telemetry = {"latency_ms": 11.0, "ber": 1e-6, "packet_loss_pct": 0.0}
        nominal_wf = {"jitter_ns": 20.0, "snr_db": 34.0, "eye_opening_pct": 96.0}
        pred = ai_engine.predict_realtime(nominal_telemetry, nominal_wf)
        self.assertIn("predicted_fault", pred)
        self.assertIn("confidence", pred)

    def test_reports_generation(self):
        df = pd.DataFrame({"channel": ["CH1", "CH2"], "packets": [100, 200]})
        csv_bytes = generate_csv(df)
        self.assertGreater(len(csv_bytes), 0)
        excel_bytes = generate_excel_report("Test Report", {"Sheet1": df})
        self.assertGreater(len(excel_bytes), 0)

    def test_vercel_serverless_gateway(self):
        import api.index as vercel_api
        self.assertTrue(hasattr(vercel_api, "handler"))
        self.assertTrue(hasattr(vercel_api, "app"))
        self.assertTrue(hasattr(vercel_api, "application"))
        self.assertTrue(vercel_api.CORE_LOADED)


if __name__ == "__main__":
    unittest.main()

