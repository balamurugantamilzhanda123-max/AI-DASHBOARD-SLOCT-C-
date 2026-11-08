"""
Robust PySerial Background Reader Module
Maintains a dedicated background daemon worker thread and thread-safe queue.Queue.
Discovers COM ports, manages reconnection, handles timeouts, and guarantees that
the Streamlit frontend never blocks on serial I/O.
Single-instance singleton pattern prevents duplicate COM port allocations across reruns.
"""

import threading
import queue
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

import serial
import serial.tools.list_ports

from core.packet_parser import PacketParser

logger = logging.getLogger("SerialReader")


class SerialReader:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Thread-safe Singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SerialReader, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.ser: Optional[serial.Serial] = None
        self.port: str = "COM3"
        self.baud_rate: int = 115200
        self.is_running: bool = False
        self.status: str = "DISCONNECTED"  # DISCONNECTED, CONNECTING, WAITING FOR HARDWARE DATA, LIVE HARDWARE STREAMING, ERROR
        self.status_detail: str = "Serial port not connected"

        self.data_queue: queue.Queue = queue.Queue(maxsize=2000)
        self.worker_thread: Optional[threading.Thread] = None
        self.last_packet_time: Optional[float] = None
        self.total_bytes_received: int = 0
        self.total_frames_parsed: int = 0
        self.total_parse_errors: int = 0

        self._initialized = True

    @staticmethod
    def list_available_ports() -> List[str]:
        """Scans system and returns list of accessible serial / COM port identifiers."""
        try:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            return ports if ports else ["No Ports Found"]
        except Exception as e:
            logger.error(f"Failed to scan serial ports: {e}")
            return ["COM1", "COM2", "COM3", "COM4", "COM5"]

    def connect(self, port: str, baud_rate: int = 115200) -> Tuple[bool, str]:
        """Opens serial port and launches background worker thread."""
        with self._lock:
            if self.is_running and self.ser and self.ser.is_open:
                if self.port == port and self.baud_rate == baud_rate:
                    return True, "Already connected to target port."
                self._stop_thread()

            self.port = port
            self.baud_rate = baud_rate
            self.status = "CONNECTING"
            self.status_detail = f"Attempting connection to {port} @ {baud_rate} baud..."

            try:
                self.ser = serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    timeout=0.5,
                    write_timeout=0.5
                )
                self.is_running = True
                self.status = "WAITING FOR HARDWARE DATA"
                self.status_detail = f"Connected to {port}. Waiting for incoming frames..."

                # Start background thread
                self.worker_thread = threading.Thread(target=self._read_worker_loop, daemon=True)
                self.worker_thread.start()
                return True, f"Successfully opened {port} @ {baud_rate} baud."
            except Exception as e:
                self.is_running = False
                self.status = "DISCONNECTED"
                self.status_detail = f"Failed to open {port}: {str(e)}"
                return False, self.status_detail

    def disconnect(self):
        """Safely stops background thread and closes serial handle."""
        with self._lock:
            self._stop_thread()
            self.status = "DISCONNECTED"
            self.status_detail = "Serial connection closed by operator."

    def _stop_thread(self):
        self.is_running = False
        if self.ser:
            try:
                if self.ser.is_open:
                    self.ser.close()
            except Exception:
                pass
            self.ser = None

    def _read_worker_loop(self):
        """Dedicated background daemon loop reading serial bytes without blocking UI."""
        logger.info(f"Serial worker thread started on {self.port}")
        buffer = ""

        while self.is_running:
            try:
                if not self.ser or not self.ser.is_open:
                    self.status = "DISCONNECTED"
                    self.status_detail = "Serial port handle closed."
                    break

                # Non-blocking read of available bytes
                waiting_bytes = self.ser.in_waiting
                if waiting_bytes > 0:
                    raw_chunk = self.ser.read(waiting_bytes)
                    self.total_bytes_received += len(raw_chunk)
                    self.last_packet_time = time.time()
                    self.status = "LIVE HARDWARE STREAMING"

                    try:
                        text_chunk = raw_chunk.decode("utf-8", errors="ignore")
                        buffer += text_chunk
                    except Exception:
                        continue

                    # Process complete newline-delimited lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line:
                            success, packet, err = PacketParser.parse_ndjson(line)
                            if success and packet:
                                self.total_frames_parsed += 1
                                try:
                                    self.data_queue.put_nowait(packet)
                                except queue.Full:
                                    # Discard oldest to keep fresh telemetry
                                    try:
                                        self.data_queue.get_nowait()
                                        self.data_queue.put_nowait(packet)
                                    except Exception:
                                        pass
                            else:
                                self.total_parse_errors += 1
                else:
                    # No bytes ready: Check timeout
                    if self.last_packet_time is not None:
                        elapsed = time.time() - self.last_packet_time
                        if elapsed > 3.0:
                            self.status = "WAITING FOR HARDWARE DATA"
                            self.status_detail = f"No incoming frames for {elapsed:.1f}s"
                    time.sleep(0.015)  # 15ms sleep to yield CPU
            except (serial.SerialException, OSError) as e:
                logger.error(f"Serial I/O error on {self.port}: {e}")
                self.status = "DISCONNECTED"
                self.status_detail = f"Hardware disconnection detected: {str(e)}"
                break
            except Exception as e:
                logger.error(f"Unexpected worker exception: {e}")
                time.sleep(0.05)

        self.is_running = False
        logger.info("Serial worker thread exited.")

    def get_packets(self, max_packets: int = 100) -> List[Dict[str, Any]]:
        """Drains up to max_packets from the thread-safe queue."""
        packets = []
        while not self.data_queue.empty() and len(packets) < max_packets:
            try:
                p = self.data_queue.get_nowait()
                packets.append(p)
            except queue.Empty:
                break
        return packets

    def get_status_info(self) -> Dict[str, Any]:
        """Returns connection diagnostics."""
        return {
            "status": self.status,
            "status_detail": self.status_detail,
            "port": self.port,
            "baud_rate": self.baud_rate,
            "is_connected": (self.is_running and self.ser is not None and self.ser.is_open),
            "bytes_received": self.total_bytes_received,
            "frames_parsed": self.total_frames_parsed,
            "parse_errors": self.total_parse_errors,
            "queue_size": self.data_queue.qsize()
        }


# Global Singleton instance
serial_reader = SerialReader()

