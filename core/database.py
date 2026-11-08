"""
Database Management Layer for AI-Assisted Signal Monitoring System
Uses SQLite to store session metrics, telemetry, faults, alerts, AI predictions, and settings.
Pre-seeds realistic historical test data on first initialization.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "signal_monitor.db")


def get_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes tables and seeds initial historical data if database is new."""
    conn = get_connection()
    cursor = conn.cursor()

    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        start_time TEXT,
        end_time TEXT,
        data_source TEXT,
        total_packets INTEGER,
        status TEXT
    )
    """)

    # Channel telemetry table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        timestamp TEXT,
        channel TEXT,
        tx_packets INTEGER,
        rx_packets INTEGER,
        packet_loss REAL,
        ber REAL,
        latency REAL,
        signal_quality REAL,
        fault_state TEXT
    )
    """)

    # Fault events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fault_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        timestamp TEXT,
        channel TEXT,
        fault_type TEXT,
        severity TEXT,
        description TEXT,
        ai_detected INTEGER,
        acknowledged INTEGER
    )
    """)

    # Alerts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        session_id TEXT,
        timestamp TEXT,
        channel TEXT,
        severity TEXT,
        fault_type TEXT,
        message TEXT,
        status TEXT
    )
    """)

    # AI Predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        timestamp TEXT,
        channel TEXT,
        predicted_fault TEXT,
        confidence REAL,
        anomaly_score REAL,
        is_anomaly INTEGER
    )
    """)

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()

    # Check if historical data exists; if empty, seed realistic historical sessions
    cursor.execute("SELECT COUNT(*) as count FROM sessions")
    if cursor.fetchone()["count"] == 0:
        _seed_historical_data(conn)

    conn.close()


def _seed_historical_data(conn):
    """Seeds realistic historical sessions, telemetry records, faults, alerts, and AI predictions."""
    cursor = conn.cursor()
    base_time = datetime.now() - timedelta(days=5)

    fault_types = ["NORMAL", "BIT_CORRUPTION", "TRANSMISSION_DELAY", "BURST_ERROR", "PACKET_LOSS"]
    severities = {"NORMAL": "INFO", "BIT_CORRUPTION": "WARNING", "TRANSMISSION_DELAY": "WARNING", "BURST_ERROR": "CRITICAL", "PACKET_LOSS": "CRITICAL"}

    session_ids = [
        f"SESSION-{base_time.strftime('%Y%m%d')}-001",
        f"SESSION-{(base_time + timedelta(days=1)).strftime('%Y%m%d')}-002",
        f"SESSION-{(base_time + timedelta(days=2)).strftime('%Y%m%d')}-003",
        f"SESSION-{(base_time + timedelta(days=3)).strftime('%Y%m%d')}-004",
        f"SESSION-{(base_time + timedelta(days=4)).strftime('%Y%m%d')}-005",
    ]

    alert_counter = 1001

    for s_idx, session_id in enumerate(session_ids):
        s_start = base_time + timedelta(days=s_idx, hours=9)
        s_end = s_start + timedelta(hours=4)
        total_packets = random.randint(45000, 95000)

        cursor.execute("""
            INSERT INTO sessions (session_id, start_time, end_time, data_source, total_packets, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, s_start.isoformat(), s_end.isoformat(), "SIMULATION DATA", total_packets, "COMPLETED"))

        # Generate telemetry points for this session
        num_points = 30
        for step in range(num_points):
            t_curr = s_start + timedelta(minutes=step * 8)
            t_str = t_curr.isoformat()

            for ch in ["CH1", "CH2", "CH3"]:
                # Normal baseline with occasional fault spikes
                is_fault = (step in [7, 14, 22]) and (ch == random.choice(["CH1", "CH2", "CH3"]))
                if is_fault:
                    fault_type = random.choice(["BIT_CORRUPTION", "TRANSMISSION_DELAY", "BURST_ERROR", "PACKET_LOSS"])
                else:
                    fault_type = "NORMAL"

                if fault_type == "NORMAL":
                    tx = random.randint(280, 320)
                    rx = tx - random.randint(0, 2)
                    loss = round(((tx - rx) / tx) * 100, 2)
                    latency = round(random.uniform(8.5, 14.2), 2)
                    ber = round(random.uniform(1e-6, 4e-5), 6)
                    quality = round(random.uniform(96.0, 99.8), 1)
                elif fault_type == "PACKET_LOSS":
                    tx = random.randint(280, 320)
                    rx = int(tx * random.uniform(0.70, 0.85))
                    loss = round(((tx - rx) / tx) * 100, 2)
                    latency = round(random.uniform(18.0, 35.0), 2)
                    ber = round(random.uniform(5e-4, 2e-3), 5)
                    quality = round(random.uniform(65.0, 78.0), 1)
                elif fault_type == "BIT_CORRUPTION":
                    tx = random.randint(280, 320)
                    rx = tx - 1
                    loss = round(((tx - rx) / tx) * 100, 2)
                    latency = round(random.uniform(12.0, 19.0), 2)
                    ber = round(random.uniform(1.2e-3, 6.5e-3), 5)
                    quality = round(random.uniform(70.0, 82.0), 1)
                elif fault_type == "TRANSMISSION_DELAY":
                    tx = random.randint(280, 320)
                    rx = tx
                    loss = 0.0
                    latency = round(random.uniform(75.0, 160.0), 2)
                    ber = round(random.uniform(1e-5, 8e-5), 5)
                    quality = round(random.uniform(74.0, 84.0), 1)
                else:  # BURST_ERROR
                    tx = random.randint(280, 320)
                    rx = int(tx * 0.90)
                    loss = round(((tx - rx) / tx) * 100, 2)
                    latency = round(random.uniform(30.0, 65.0), 2)
                    ber = round(random.uniform(8.0e-3, 2.5e-2), 4)
                    quality = round(random.uniform(55.0, 72.0), 1)

                cursor.execute("""
                    INSERT INTO channel_telemetry 
                    (session_id, timestamp, channel, tx_packets, rx_packets, packet_loss, ber, latency, signal_quality, fault_state)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (session_id, t_str, ch, tx, rx, loss, ber, latency, quality, fault_type))

                # Log fault event and alert if not normal
                if fault_type != "NORMAL":
                    sev = severities.get(fault_type, "WARNING")
                    desc = f"Simulated {fault_type.replace('_', ' ').title()} observed on {ch}."
                    cursor.execute("""
                        INSERT INTO fault_events 
                        (session_id, timestamp, channel, fault_type, severity, description, ai_detected, acknowledged)
                        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                    """, (session_id, t_str, ch, fault_type, sev, desc, random.choice([0, 1])))

                    cursor.execute("""
                        INSERT INTO alerts 
                        (id, session_id, timestamp, channel, severity, fault_type, message, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (f"ALT-{alert_counter}", session_id, t_str, ch, sev, fault_type, desc, random.choice(["ACKNOWLEDGED", "RESOLVED", "ACTIVE"])))
                    alert_counter += 1

                # AI prediction record
                conf = round(random.uniform(0.88, 0.98), 2) if fault_type != "NORMAL" else round(random.uniform(0.94, 0.99), 2)
                anom_score = round(random.uniform(-0.65, -0.25), 3) if fault_type != "NORMAL" else round(random.uniform(0.15, 0.45), 3)
                cursor.execute("""
                    INSERT INTO ai_predictions 
                    (session_id, timestamp, channel, predicted_fault, confidence, anomaly_score, is_anomaly)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (session_id, t_str, ch, fault_type, conf, anom_score, 1 if fault_type != "NORMAL" else 0))

    # Initialize default settings
    default_settings = {
        "data_source": "SIMULATION",
        "baud_rate": "115200",
        "serial_port": "COM3",
        "sampling_interval_ms": "100",
        "signal_update_interval_sec": "1.0",
        "packet_timeout_ms": "500",
        "ber_threshold": "0.001",
        "latency_threshold_ms": "50.0",
        "packet_loss_threshold_pct": "5.0",
        "theme_accent": "Electric Cyan",
        "active_channels": "CH1,CH2,CH3"
    }
    for k, v in default_settings.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

    conn.commit()


def get_all_sessions():
    """Retrieves all sessions ordered by start_time descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_telemetry_history(session_id=None, channel=None, limit=500):
    """Retrieves telemetry points with optional session and channel filtering."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM channel_telemetry WHERE 1=1"
    params = []
    if session_id and session_id != "ALL":
        query += " AND session_id = ?"
        params.append(session_id)
    if channel and channel != "ALL":
        query += " AND channel = ?"
        params.append(channel)
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_fault_events(session_id=None, channel=None, severity=None, limit=200):
    """Retrieves fault events with optional filters."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM fault_events WHERE 1=1"
    params = []
    if session_id and session_id != "ALL":
        query += " AND session_id = ?"
        params.append(session_id)
    if channel and channel != "ALL":
        query += " AND channel = ?"
        params.append(channel)
    if severity and severity != "ALL":
        query += " AND severity = ?"
        params.append(severity)
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_alerts(status=None, severity=None, channel=None):
    """Retrieves alerts with optional filters."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []
    if status and status != "ALL":
        query += " AND status = ?"
        params.append(status)
    if severity and severity != "ALL":
        query += " AND severity = ?"
        params.append(severity)
    if channel and channel != "ALL":
        query += " AND channel = ?"
        params.append(channel)
    query += " ORDER BY timestamp DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def update_alert_status(alert_id, new_status):
    """Updates an alert status (ACTIVE, ACKNOWLEDGED, RESOLVED)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET status = ? WHERE id = ?", (new_status, alert_id))
    conn.commit()
    conn.close()


def insert_alert(alert_id, session_id, timestamp, channel, severity, fault_type, message, status="ACTIVE"):
    """Inserts a new alert into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO alerts (id, session_id, timestamp, channel, severity, fault_type, message, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (alert_id, session_id, timestamp, channel, severity, fault_type, message, status))
    conn.commit()
    conn.close()


def insert_fault_event(session_id, timestamp, channel, fault_type, severity, description, ai_detected=1, acknowledged=0):
    """Inserts a new fault event."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fault_events (session_id, timestamp, channel, fault_type, severity, description, ai_detected, acknowledged)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, timestamp, channel, fault_type, severity, description, ai_detected, acknowledged))
    conn.commit()
    conn.close()


def insert_telemetry_batch(telemetry_records):
    """Inserts a list of telemetry dicts into channel_telemetry."""
    conn = get_connection()
    cursor = conn.cursor()
    for rec in telemetry_records:
        cursor.execute("""
            INSERT INTO channel_telemetry 
            (session_id, timestamp, channel, tx_packets, rx_packets, packet_loss, ber, latency, signal_quality, fault_state)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec.get("session_id"),
            rec.get("timestamp"),
            rec.get("channel"),
            rec.get("tx_packets"),
            rec.get("rx_packets"),
            rec.get("packet_loss"),
            rec.get("ber"),
            rec.get("latency"),
            rec.get("signal_quality"),
            rec.get("fault_state")
        ))
    conn.commit()
    conn.close()


def get_ai_predictions(limit=200):
    """Retrieves recent AI predictions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM ai_predictions ORDER BY timestamp DESC LIMIT {limit}")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_setting(key, default=None):
    """Retrieves a configuration setting value."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def save_setting(key, value):
    """Saves or updates a setting value."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


def get_all_settings():
    """Retrieves all settings as a dict."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    settings = {r["key"]: r["value"] for r in cursor.fetchall()}
    conn.close()
    return settings

