"""
Fault Injection Module for AI-Assisted Signal Monitoring System
Manages active fault states, simulates fault profiles (Packet Loss, Bit Corruption,
Transmission Delay, Burst Error), and logs fault injection events to database.
"""

from datetime import datetime
import uuid
from core.database import insert_fault_event, insert_alert


class FaultInjector:
    def __init__(self):
        # Active fault dictionary per channel: {'CH1': {...}, 'CH2': {...}, 'CH3': {...}}
        self.active_faults = {
            "CH1": {"type": "NORMAL", "severity": "INFO", "start_time": None, "duration_sec": 0, "description": "Normal signal flow"},
            "CH2": {"type": "NORMAL", "severity": "INFO", "start_time": None, "duration_sec": 0, "description": "Normal signal flow"},
            "CH3": {"type": "NORMAL", "severity": "INFO", "start_time": None, "duration_sec": 0, "description": "Normal signal flow"},
        }

    def inject_fault(self, channel: str, fault_type: str, severity: str = "WARNING", duration_sec: int = 15, session_id: str = "LIVE-SESSION"):
        """
        Injects a test fault onto a specified channel (or all channels).
        Logs the fault event and raises an alert.
        """
        now_str = datetime.now().isoformat()
        target_channels = ["CH1", "CH2", "CH3"] if channel == "ALL" else [channel]

        descriptions = {
            "NORMAL": "Channel restored to nominal baseline condition.",
            "PACKET_LOSS": f"Injected artificial packet drop ({severity} severity). Receiver packet drop triggered.",
            "BIT_CORRUPTION": f"Injected pseudorandom bit inversions ({severity} severity). CRC checks failing.",
            "TRANSMISSION_DELAY": f"Injected propagation delay buffer lag ({severity} severity). Latency elevated.",
            "BURST_ERROR": f"Injected burst noise distortion ({severity} severity). Clustered bit errors active."
        }
        desc = descriptions.get(fault_type, f"Injected {fault_type} on {channel}")

        for ch in target_channels:
            self.active_faults[ch] = {
                "type": fault_type,
                "severity": severity if fault_type != "NORMAL" else "INFO",
                "start_time": datetime.now(),
                "duration_sec": duration_sec,
                "description": desc
            }

            if fault_type != "NORMAL":
                # Log event in database
                insert_fault_event(
                    session_id=session_id,
                    timestamp=now_str,
                    channel=ch,
                    fault_type=fault_type,
                    severity=severity,
                    description=desc,
                    ai_detected=1,
                    acknowledged=0
                )

                # Generate alert
                alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
                alert_sev = "CRITICAL" if severity in ["HIGH", "CRITICAL"] or fault_type in ["BURST_ERROR", "PACKET_LOSS"] else "WARNING"
                insert_alert(
                    alert_id=alert_id,
                    session_id=session_id,
                    timestamp=now_str,
                    channel=ch,
                    severity=alert_sev,
                    fault_type=fault_type,
                    message=f"[{ch}] {desc}",
                    status="ACTIVE"
                )

        return True

    def clear_fault(self, channel: str = "ALL"):
        """Clears active fault and restores normal baseline."""
        target_channels = ["CH1", "CH2", "CH3"] if channel == "ALL" else [channel]
        for ch in target_channels:
            self.active_faults[ch] = {
                "type": "NORMAL",
                "severity": "INFO",
                "start_time": None,
                "duration_sec": 0,
                "description": "Normal signal flow"
            }

    def get_channel_fault(self, channel: str) -> dict:
        """Returns the current fault state of a channel, handling auto-expiry if duration elapsed."""
        state = self.active_faults.get(channel, {"type": "NORMAL", "severity": "INFO"})
        if state["type"] != "NORMAL" and state["start_time"] and state["duration_sec"] > 0:
            elapsed = (datetime.now() - state["start_time"]).total_seconds()
            if elapsed > state["duration_sec"]:
                # Auto-clear expired fault
                self.active_faults[channel] = {
                    "type": "NORMAL",
                    "severity": "INFO",
                    "start_time": None,
                    "duration_sec": 0,
                    "description": "Fault duration expired; returned to baseline."
                }
                return self.active_faults[channel]
        return state

    def get_all_active_faults(self) -> dict:
        """Returns active fault states across all channels."""
        return {ch: self.get_channel_fault(ch) for ch in ["CH1", "CH2", "CH3"]}


# Global Singleton instance
fault_injector = FaultInjector()

