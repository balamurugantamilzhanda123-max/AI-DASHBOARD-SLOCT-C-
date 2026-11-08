# Comprehensive Dashboard Audit & Hardware Integration Blueprint

## Project
**AI-Assisted Real-Time Digital Communication Signal Monitoring and Fault Detection System**

**Auditor / Roles**: Senior Python Architect, Embedded Communication Systems Engineer, AI/ML Engineer, Real-Time Dashboard Developer  
**Audit Timestamp**: 2026-11-08  
**Live Target**: Streamlit Dashboard running at `http://localhost:8501`

---

## 1. Executive Summary

An exhaustive technical audit of the existing dashboard was conducted. The application possesses a solid foundation with a professional dark theme, modular page structure (10 functional pages), SQLite storage, Scikit-learn AI models, and Plotly visualizations. However, several critical areas require architectural elevation to fulfill the requirements of **genuine real-time digital communication monitoring with live hardware integration**:

1. **Hardware Serial Driver**: `HardwareSerialDataSource` in `core/data_source.py` is currently a placeholder returning static zeros. It lacks PySerial background threading, non-blocking queueing, port auto-discovery, frame synchronization, and disconnection detection.
2. **Missing Packet & Sequence Loss Validation**: Currently, packet loss is calculated via simulated counters rather than tracking sequence numbers ($seq_k$). A dedicated `PacketValidator` must detect missing sequence gaps, packet reordering, and counter resets.
3. **Hardcoded Metric Artifact**: System uptime in `SimulationDataSource.get_system_summary()` is hardcoded to `"04h 32m 18s"` instead of being derived from real elapsed session time.
4. **Hardware Data Purity**: The dashboard must guarantee that in **Hardware Serial Mode**, when no serial frames arrive, it strictly displays `"WAITING FOR HARDWARE DATA"`, and when the port disconnects, it displays `"DISCONNECTED"`, with zero synthetic data fabrication.

---

## 2. Inventory of Existing Project Files

| File Path | Functional Domain | Audit Status |
| :--- | :--- | :--- |
| `app.py` | Main Streamlit entrypoint & router | **Functional**: Clean routing, CSS injection, database initialization. |
| `requirements.txt` | Dependency declarations | **Complete**: Added `pyserial>=3.5` alongside streamlit, plotly, scikit-learn, etc. |
| `signal_monitor.db` | SQLite persistent database | **Functional**: Contains sessions, telemetry, fault events, alerts, and settings. |
| `styles/theme.css` | Theme stylesheet | **Complete**: Futuristic midnight-blue & neon-cyan theme. |
| `components/top_navbar.py` | Top navigation bar | **Functional**: Displays system status, data source mode, live time, alerts. |
| `components/sidebar.py` | Sidebar navigation | **Functional**: 10-page radio selection & channel matrix status. |
| `components/kpi_cards.py` | Reusable KPI metric cards | **Functional**: 8 cards with glowing neon borders. |
| `pages_custom/p1_overview.py` | Page 1: Dashboard Overview | **Functional**: KPI cards, health gauge, channel cards, live log. |
| `pages_custom/p2_live_signal.py` | Page 2: Live Signal Monitoring | **Functional**: 3-row oscilloscope, bit comparison, Eye diagram, auto-stream. |
| `pages_custom/p3_channel_analysis.py` | Page 3: Channel Analysis | **Functional**: Polar radar, throughput comparison, health grades. |
| `pages_custom/p4_fault_detection.py` | Page 4: Fault Detection Centre | **Functional**: Interactive fault injection test bench, impact preview, audit log. |
| `pages_custom/p5_ai_prediction.py` | Page 5: AI Prediction Centre | **Functional**: Random Forest & Isolation Forest inference, confusion matrix. |
| `pages_custom/p6_signal_analytics.py` | Page 6: Signal Analytics | **Functional**: Multi-dimensional Plotly analytical charts & filters. |
| `pages_custom/p7_alert_centre.py` | Page 7: Alert Centre | **Functional**: Filterable incident tickets with working acknowledge/resolve actions. |
| `pages_custom/p8_historical_data.py` | Page 8: Historical Data | **Functional**: Tabbed archive with search query engine. |
| `pages_custom/p9_reports.py` | Page 9: Reports | **Functional**: Downloadable CSV and OpenPyXL styled multi-sheet Excel workbooks. |
| `pages_custom/p10_settings.py` | Page 10: System Settings | **Functional**: Configuration registry with SQLite persistence. |
| `core/database.py` | Database layer | **Functional**: SQLite schema, seeding, and queries. |
| `core/fault_injector.py` | Fault injection engine | **Functional**: Simulates Packet Loss, Bit Corruption, Delays, Bursts. |
| `core/signal_generator.py` | Digital waveform synthesizer | **Functional**: Generates NRZ logic, noise, slew rate, and 2-UI Eye diagram. |
| `core/ai_engine.py` | Scikit-learn AI engine | **Functional**: Random Forest + Isolation Forest with holdout evaluation. |
| `core/data_source.py` | Data source abstraction | **Needs Enhancement**: Replace static hardware stub with live PySerial worker. |
| `utils/exporter.py` | Report generation | **Functional**: CSV & styled Excel exports. |
| `utils/formatters.py` | Number & string formatting | **Functional**: Scientific notation BER formatters and HTML badges. |

---

## 3. Classification of Every Displayed Metric & Value

To ensure complete transparency and prevent sample data from ever being mislabeled as live hardware data, every displayed value across the system is classified below:

| Page / Component | Displayed Element | Current Classification | Target Hardware Mode Classification |
| :--- | :--- | :--- | :--- |
| **Top Navbar** | Operational Status (`SYSTEM ONLINE`) | **Calculated Metric** | **Calculated Metric** (`ONLINE` / `WAITING FOR DATA` / `DISCONNECTED`) |
| **Top Navbar** | Data Source Badge | **Calculated Metric** | **Calculated Metric** (`SIMULATION DATA` or `HARDWARE SERIAL`) |
| **Top Navbar** | Alert Count (`ALERTS: 7`) | **Calculated Metric** | **Calculated Metric** (Live DB active alerts) |
| **Top Navbar** | Local Timestamp | **Calculated Metric** | **Calculated Metric** (System clock) |
| **Top Navbar** | User Role (`Lead Systems Engineer`) | **Static Placeholder** | **Static Placeholder** (Operator profile label) |
| **Sidebar** | Channel Status (`CH1: NORMAL`) | **Calculated Metric** | **Calculated Metric** (From verified channel telemetry) |
| **Overview** | Total TX Packets | **Simulated Data** | **Actual Hardware Data** (Extracted from sequence header) |
| **Overview** | Total RX Packets | **Simulated Data** | **Actual Hardware Data** (Count of valid received frames) |
| **Overview** | Packet Loss % | **Calculated Metric** | **Calculated Metric** (From sequence gap analysis) |
| **Overview** | Signal Quality % | **Calculated Metric** | **Calculated Metric** (Derived formula from SNR, BER, & Loss) |
| **Overview** | Average Latency | **Simulated Data** | **Actual Hardware Data** (Loopback propagation time) |
| **Overview** | Bit Error Rate (BER) | **Calculated Metric** | **Calculated Metric** (Total bit errors / compared bits) |
| **Overview** | Detected Faults Count | **Calculated Metric** | **Calculated Metric** (Active non-normal channel flags) |
| **Overview** | System Uptime | **Static Placeholder** (`04h 32m 18s`) | **Calculated Metric** (Dynamic elapsed session duration) |
| **Overview** | System Health Index | **Calculated Metric** | **Calculated Metric** (Composite formula) |
| **Live Signal** | Transmitted Waveform (TX) | **Simulated Data** | **Actual Hardware Data** (Reported TX bitstream) |
| **Live Signal** | Received Waveform (RX) | **Simulated Data** | **Actual Hardware Data** (Sampled RX pin levels/ADC buffer) |
| **Live Signal** | Difference Curve ($|TX - RX|$) | **Calculated Metric** | **Calculated Metric** (Point-by-point difference) |
| **Live Signal** | SNR (dB), Jitter (ns), Eye Opening | **Calculated Metric** | **Calculated Metric** (Waveform statistics) |
| **Live Signal** | Bit Discrepancies | **Calculated Metric** | **Calculated Metric** (Parity/bit comparison) |
| **Live Signal** | Eye Diagram Persistence Overlay | **Simulated Data** | **Actual Hardware Data** (Overlaid 2-UI symbol slices) |
| **Channel Analysis**| Throughput Bar Chart | **Calculated Metric** | **Calculated Metric** (Cumulative received vs expected) |
| **Channel Analysis**| 5-Axis Polar Radar Chart | **Calculated Metric** | **Calculated Metric** (Normalized channel scores) |
| **Fault Detection** | Active Condition & Severity | **Simulated Data** | **Actual Hardware Data** (Receiver hardware fault flags) |
| **AI Prediction** | Predicted Fault Category | **Calculated Metric** | **Calculated Metric** (Random Forest inference on telemetry) |
| **AI Prediction** | Confidence Score (%) | **Calculated Metric** | **Calculated Metric** (`predict_proba` max score) |
| **AI Prediction** | Isolation Forest Anomaly Score | **Calculated Metric** | **Calculated Metric** (`decision_function` score) |
| **AI Prediction** | Confusion Matrix & Metrics | **Calculated Metric** | **Calculated Metric** (Holdout validation partition) |
| **Signal Analytics**| Latency & BER Trendlines | **Calculated Metric** | **Calculated Metric** (Time-series telemetry from DB) |
| **Alert Centre** | Incident Tickets | **Calculated Metric** | **Calculated Metric** (Triggered by threshold breaches) |
| **Historical Data**| Session Logs & Telemetry | **Calculated Metric** | **Actual Hardware Data** (Logged historical frames) |
| **Reports** | Downloadable CSV & Excel | **Calculated Metric** | **Actual Hardware Data** (Exported database tables) |

---

## 4. Deficiencies & Gaps to Resolve

### Gap 1: Standalone Modularization for Hardware Data Pipeline
Currently, data source logic resides in a monolithic `core/data_source.py`. We must separate this into discrete, testable components:
- `core/data_source.py`: Defines the abstract `BaseDataSource` contract.
- `core/signal_simulator.py`: Clean simulation engine encapsulating waveform and telemetry generation.
- `core/serial_reader.py`: Robust, non-blocking PySerial background reader with a thread-safe `queue.Queue`.
- `core/packet_parser.py`: Robust deserializer supporting both **Newline-Delimited JSON** and framed binary packets.
- `core/packet_validator.py`: Sequence gap counter, duplicate detector, checksum validator, and reset handler.
- `core/signal_metrics.py`: Standard mathematical formulations for Packet Loss, BER, Latency, and Signal Quality.
- `core/ai_prediction.py`: Modular AI inference pipeline consuming telemetry feature vectors.

### Gap 2: Dynamic Uptime Calculation
Replace the static `"04h 32m 18s"` string in `SimulationDataSource` and `HardwareSerialDataSource` with:
$$\text{Uptime} = \text{Current Timestamp} - \text{Session Start Timestamp}$$
formatted as `HHh MMm SSs`.

### Gap 3: Sequence Number Loss Detection
Relying solely on received packet counts cannot distinguish between dropped packets and slow transmission. The `PacketValidator` must inspect sequence numbers:
$$\text{Expected Packets} = seq_{\text{latest}} - seq_{\text{initial}} + 1$$
$$\text{Missing Packets} = \text{Expected Packets} - \text{Valid Received Packets}$$
$$\text{Packet Loss \%} = \frac{\text{Missing Packets}}{\text{Expected Packets}} \times 100$$
Additionally, sequence rollover or transmitter reboot must be safely detected when $seq_k < seq_{k-1}$.

### Gap 4: Hardware Disconnection & Waiting States
In Hardware Serial Mode:
- If COM port cannot be opened: status = `"DISCONNECTED"` (no data produced, no fake readings).
- If COM port is opened but no bytes have arrived: status = `"WAITING FOR HARDWARE DATA"`.
- If valid frames arrive: status = `"LIVE HARDWARE STREAMING"`.

---

## 5. Architectural Implementation Roadmap

```
           +-------------------------------------------------------+
           |                Streamlit Dashboard UI                 |
           |             (10 Dedicated Modular Pages)              |
           +-------------------------------------------------------+
                                      |
                      BaseDataSource (Abstract Interface)
                                      |
                 +--------------------+--------------------+
                 |                                         |
     SimulationDataSource                       HardwareSerialDataSource
                 |                                         |
    +------------+------------+             +--------------+--------------+
    | SignalSimulator         |             | SerialReader (PySerial / bg)|
    | FaultInjector           |             | Thread-Safe queue.Queue     |
    +-------------------------+             | PacketParser (JSON/Binary)  |
                                            | PacketValidator (Seq/CRC)   |
                                            +-----------------------------+
                                                           |
                                            +--------------+--------------+
                                            | SignalMetrics Calculator    |
                                            | AI Engine Inference         |
                                            | SQLite Database Storage     |
                                            +-----------------------------+
```

Next, we proceed to Phase 2 to implement the decoupled data source architecture.

