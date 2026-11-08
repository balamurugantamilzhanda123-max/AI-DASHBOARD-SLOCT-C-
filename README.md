# AI-Assisted Real-Time Digital Communication Signal Monitoring and Fault Detection System

An industrial-grade, futuristic AI-powered digital communications monitoring and telemetry analysis platform designed for a Final-Year Engineering Capstone Project. 

Inspired by modern **Network Operations Center (NOC)** platforms, **Industrial IoT diagnostic systems**, and **deep-learning cyber-physical signal analyzers**, this application provides comprehensive real-time waveform inspection, logical bus matrix comparison (CH1, CH2, CH3), interactive fault injection, scikit-learn machine learning fault classification & anomaly detection, historical session auditing, multi-format reporting, and a production-ready **Arduino Nano USB Serial** hardware interface.

---

## 🚀 Key Highlights & Architectural Strengths

- **Dual Data Source Architecture**: Built with a decoupled `BaseDataSource` contract allowing instant toggling between **High-Fidelity Physics Simulation** and **Live Arduino Nano USB Serial Hardware Mode** without altering any UI components.
- **Robust Hardware Serial Communication**: Non-blocking PySerial background worker thread reading incoming NDJSON or binary framed packets into a thread-safe `queue.Queue`.
- **Zero Data Fabrication Guarantee**: When running in Hardware Mode, the dashboard strictly displays `"WAITING FOR HARDWARE DATA"` or `"DISCONNECTED"` when frames are absent—never synthesizing fake telemetry.
- **Rigorous Mathematical Formulation**: Calculates sequence gaps ($\text{Expected} - \text{Valid Received}$), bit-by-bit comparison BER, latency tracking, and a documented Signal Quality Index ($\mathcal{Q}$).
- **Genuine Machine Learning Pipelines**: Powered by genuine scikit-learn models (**Random Forest Classifier** with 100 decision trees + **Isolation Forest Anomaly Detector**), trained and evaluated on holdout partitions with genuine confusion matrices, accuracy, precision, recall, and F1 scores.
- **Rich Interactive Visualizations**: Plotly-driven multi-row digital oscilloscope views ($TX$ vs $RX$ correlation, $|TX-RX|$ discrepancy detection, clock markers), polar radar health charts, and latency/BER trendlines.
- **SQLite Persistence & Multi-Format Exporter**: Complete session database storing multi-channel telemetry, fault occurrences, alert incident tickets with acknowledgement workflows, and persistent configuration settings, plus CSV and styled multi-sheet OpenPyXL Excel reports.
- **Automated Unit Testing Suite**: Comprehensive unit tests in `tests/test_system.py` verifying packet parsing, validation, sequence tracking, metrics bounds, AI inference, and report exports with 100% pass rate.

---

## 📁 Modular Directory Structure

```text
SLOT C AI WEB/
├── app.py                     # Main application entry point & modular routing harness
├── requirements.txt           # Project Python dependencies
├── README.md                  # Project documentation & operational handbook
├── .gitignore                 # Git ignore rules for Python, virtual environments, and caches
├── styles/
│   └── theme.css              # Premium futuristic dark theme (Midnight Navy, Electric Blue, Cyan)
├── components/
│   ├── __init__.py
│   ├── top_navbar.py          # Top navigation bar (System status, Data source indicator, Live clock, Alerts)
│   ├── sidebar.py             # Collapsible sidebar navigation & tri-channel status matrix
│   └── kpi_cards.py           # Futuristic KPI metric cards with neon accents
├── pages_custom/              # 10 dedicated functional pages
│   ├── __init__.py
│   ├── p1_overview.py         # Dashboard Overview (KPI cards, Health gauge, Channel matrix, Live throughput)
│   ├── p2_live_signal.py      # Live Digital Signal Monitoring (TX/RX waveforms, eye metrics, bit correlation)
│   ├── p3_channel_analysis.py # Multi-Channel Analysis (CH1, CH2, CH3 radar charts, throughput comparisons)
│   ├── p4_fault_detection.py  # Fault Detection Centre (Interactive fault injection test bench & impact preview)
│   ├── p5_ai_prediction.py    # AI Prediction Centre (RF Classifier, Isolation Forest, Confusion matrix, Gini importances)
│   ├── p6_signal_analytics.py # Advanced Signal Analytics (Throughput, Loss, Latency, BER dynamics, Fault donut)
│   ├── p7_alert_centre.py     # Real-Time Alert Centre (Severity filters, Acknowledge & Resolve workflows)
│   ├── p8_historical_data.py  # Historical Data Explorer (Session logs, Search query, Telemetry archives)
│   ├── p9_reports.py          # Engineering Reports (CSV and multi-sheet styled Excel .xlsx exports)
│   └── p10_settings.py        # System Settings (Simulation vs Arduino Hardware mode, COM port, Baud, Thresholds)
├── core/
│   ├── __init__.py
│   ├── data_source.py         # BaseDataSource, SimulationDataSource & HardwareSerialDataSource
│   ├── serial_reader.py       # Non-blocking PySerial background daemon, queue.Queue, COM discovery
│   ├── packet_parser.py       # Robust NDJSON and binary frame parser with CRC verification
│   ├── packet_validator.py    # Multi-channel sequence tracking, missing packet detection, BER & resets
│   ├── signal_metrics.py      # Digital communication mathematical formulation (Loss, BER, Latency, Quality)
│   ├── signal_simulator.py    # Deterministic multi-channel simulation engine with fault synthesis
│   ├── signal_generator.py    # High-resolution square wave generator, slew rate distortion & Eye diagram synthesizer
│   ├── fault_injector.py      # Interactive fault injection state manager
│   ├── ai_engine.py           # Scikit-learn AI engine (Random Forest, Isolation Forest, real evaluation)
│   └── database.py            # SQLite database schema, historical seeding, and CRUD operations
├── docs/
│   ├── dashboard_audit.md     # Phase 1 comprehensive metric audit & classification documentation
│   ├── HARDWARE_PROTOCOL.md   # Serial protocol specification & ready-to-flash Arduino Nano C++ firmware
│   └── progress.md            # Phase tracking & verification milestone log
├── tests/
│   └── test_system.py         # Automated unit test suite (10/10 automated tests passing)
└── utils/
    ├── __init__.py
    ├── exporter.py            # CSV and OpenPyXL styled multi-sheet Excel generator
    └── formatters.py          # Scientific notation BER formatter, unit formatters, and HTML status badges
```

---

## 🛠️ Technology Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/) (v1.35+) with Custom CSS glassmorphic components
- **Interactive Visualizations**: [Plotly Graph Objects & Express](https://plotly.com/python/)
- **Machine Learning & Analytics**: [Scikit-learn](https://scikit-learn.org/) (Random Forest Classifier, Isolation Forest)
- **Data Engineering**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Hardware Serial Interface**: [PySerial](https://pyserial.readthedocs.io/)
- **Report Generation**: [OpenPyXL](https://openpyxl.readthedocs.io/) (Styled Multi-Tab Excel)
- **Database Engine**: [SQLite3](https://www.sqlite.org/) (Embedded persistent storage)

---

## ⚙️ How to Run the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```

Open your web browser and navigate to:
```text
http://localhost:8501
```

### 3. Run Automated Unit Test Suite
To verify all parsers, validators, formulas, AI engines, and hardware zero-fabrication rules:
```bash
python -m unittest tests/test_system.py
```

---

## 🔌 Hardware Serial Integration (Arduino Nano)

The platform is fully prepared to ingest real digital communication frames from physical microcontrollers:

- **Transmitter**: Arduino Nano 1 generating digital test bitstreams across logical channels `CH1`, `CH2`, and `CH3`.
- **Receiver**: Arduino Nano 2 receiving frames, verifying CRC checksums, recording timestamps, and forwarding telemetry over USB Serial (115200 bps) to the PC.
- **Protocol**: Newline-delimited JSON (NDJSON) or binary framed packets. Complete C++ firmware is provided in [`docs/HARDWARE_PROTOCOL.md`](docs/HARDWARE_PROTOCOL.md).

### Connecting to Live Hardware:
1. Flash **Arduino Nano 1** and **Arduino Nano 2** using the firmware in [`docs/HARDWARE_PROTOCOL.md`](docs/HARDWARE_PROTOCOL.md).
2. Plug the Receiver Arduino Nano into a USB port on your laptop/PC.
3. In the dashboard sidebar, select **Settings (Page 10)**.
4. Under **Data Source Configuration**, select:
   `HARDWARE (Arduino Nano USB Serial Port)`
5. Choose your detected COM port (e.g., `COM3`, `COM4`) and Baud Rate (`115200`).
6. Click **🔗 Connect**.
7. The dashboard immediately transitions from `"WAITING FOR HARDWARE DATA"` to live streaming of physical signals across all 10 pages!

---

## 📐 Mathematical Formulations

### 1. Packet Loss Percentage
$$\text{Expected} = \text{seq}_{\text{latest}} - \text{seq}_{\text{initial}} + 1$$
$$\text{Missing} = \text{Expected} - \text{Valid Received}$$
$$\text{Packet Loss \%} = \left(\frac{\text{Missing}}{\text{Expected}}\right) \times 100$$

### 2. Bit Error Rate (BER)
$$\text{BER} = \frac{\text{Total Incorrect Bits}}{\text{Total Compared Bits}}$$

### 3. Average Latency
$$\bar{\tau} = \frac{1}{N} \sum_{i=1}^{N} \tau_i \quad \text{where } \tau_i = \frac{t_{\text{rx}} - t_{\text{tx}}}{1000} \text{ ms}$$

### 4. Signal Quality Score ($\mathcal{Q} \in [0, 100]$)
$$\mathcal{Q} = \max\left(0, 100 - (\mathcal{L} \times 2.5) - \min\left(35, \frac{\text{BER}}{0.005} \times 35\right) - \min\left(25, \max(0, \bar{\tau} - 20) \times 0.35\right)\right)$$

---

## 📜 License
Developed for Final-Year Engineering Project Capstone. All rights reserved.
