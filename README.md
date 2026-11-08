# AI-Assisted Real-Time Digital Communication Signal Monitoring and Fault Detection System

An industrial-grade, futuristic AI-powered digital communications monitoring and telemetry analysis platform designed for a Final-Year Engineering Capstone Project. 

Inspired by modern **Network Operations Center (NOC)** platforms, **Industrial IoT diagnostic systems**, and **deep-learning cyber-physical signal analyzers**, this application provides comprehensive real-time waveform inspection, logical bus matrix comparison (CH1, CH2, CH3), interactive fault injection, scikit-learn machine learning fault classification & anomaly detection, historical session auditing, and multi-format reporting.

---

## 🚀 Key Highlights & Architectural Strengths

- **Future-Ready Modular Architecture**: Built with a decoupled `BaseDataSource` contract allowing immediate plug-and-play integration with physical **Arduino Nano Transmitter / Receiver** units and USB Serial (PySerial) without altering any user interface components.
- **Genuine Machine Learning Pipelines**: Powered by genuine scikit-learn models (**Random Forest Classifier** with 100 decision trees + **Isolation Forest Anomaly Detector**), trained and evaluated on holdout partitions with genuine confusion matrices, accuracy, precision, recall, and F1 scores.
- **Rich Interactive Visualizations**: Plotly-driven multi-row digital oscilloscope views (TX vs RX correlation, bit discrepancy detection, clock markers), polar radar health charts, and latency/BER trendlines.
- **SQLite Persistence**: Complete session database storing multi-channel telemetry, fault occurrences, alert incident tickets with acknowledgement workflows, and persistent configuration settings.

---

## 📁 Modular Directory Structure

```text
SLOT C AI WEB/
├── app.py                     # Main application entry point and modular routing harness
├── requirements.txt           # Project Python dependencies
├── README.md                  # Project documentation & operational handbook
├── signal_monitor.db          # SQLite persistent database (sessions, telemetry, faults, alerts, settings)
├── styles/
│   └── theme.css              # Premium futuristic dark theme (Deep Navy, Electric Blue, Cyan, Glowing Accents)
├── components/
│   ├── __init__.py
│   ├── top_navbar.py          # Top navigation bar (System status, Data source indicator, Live time, Alerts)
│   ├── sidebar.py             # Collapsible sidebar with channel matrix status
│   └── kpi_cards.py           # Futuristic KPI metric cards with neon accents
├── pages_custom/              # 10 dedicated functional pages
│   ├── __init__.py
│   ├── p1_overview.py         # Dashboard Overview (KPI cards, Health gauge, Channel matrix, Live log)
│   ├── p2_live_signal.py      # Live Digital Signal Monitoring (TX/RX waveforms, eye metrics, bit correlation)
│   ├── p3_channel_analysis.py # Multi-Channel Analysis (CH1, CH2, CH3 radar charts, throughput comparisons)
│   ├── p4_fault_detection.py  # Fault Detection Centre (Interactive fault injection test bench & impact preview)
│   ├── p5_ai_prediction.py    # AI Prediction Centre (RF Classifier, Isolation Forest, Confusion matrix, Gini importances)
│   ├── p6_signal_analytics.py # Advanced Signal Analytics (Throughput, Loss, Latency, BER dynamics, Fault donut)
│   ├── p7_alert_centre.py     # Real-Time Alert Centre (Severity filters, Acknowledge & Resolve workflows)
│   ├── p8_historical_data.py  # Historical Data Explorer (Session logs, Search query, Telemetry archives)
│   ├── p9_reports.py          # Engineering Reports (CSV and multi-sheet styled Excel .xlsx exports)
│   └── p10_settings.py        # System Settings (Simulation vs Arduino Hardware mode, Port, Baud, Thresholds)
├── core/
│   ├── __init__.py
│   ├── data_source.py         # BaseDataSource, SimulationDataSource & HardwareSerialDataSource placeholder
│   ├── signal_generator.py    # Realistic digital square wave & physical channel distortion synthesizer
│   ├── fault_injector.py      # Interactive fault injection logic (Packet Loss, Bit Corruption, Delays, Bursts)
│   ├── ai_engine.py           # Scikit-learn AI engine (Random Forest, Isolation Forest, real evaluation)
│   └── database.py            # SQLite database schema, historical seeding, and CRUD operations
└── utils/
    ├── __init__.py
    ├── exporter.py            # CSV and OpenPyXL styled multi-sheet Excel generator
    └── formatters.py          # Scientific notation BER formatter, unit formatters, and HTML status badges
```

---

## 🛠️ Technology Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/) (v1.35+) with Custom CSS glassmorphic components
- **Interactive Visualizations**: [Plotly Graph Objects & Express](https://plotly.com/python/)
- **Machine Learning & Analytics**: [Scikit-learn](https://scikit-learn.org/) (Random Forest, Isolation Forest)
- **Data Engineering**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
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

---

## 🖥️ Detailed Page Functionality

### 1. Dashboard Overview
- **8 Primary KPI Metrics**: Total Transmitted Packets, Total Received Packets, Packet Loss (%), Signal Quality (%), Average Latency (ms), Bit Error Rate (BER), Detected Faults, and System Uptime.
- **System Health Index Gauge**: Composite percentage calculation factoring in signal degradation, packet loss, and latency bounds.
- **Tri-Channel Status Matrix**: Live status cards for logical channels **CH1**, **CH2**, and **CH3**.
- **Real-Time Throughput Timeline**: Synchronized time-series plotting of channel propagation latency.
- **Recent Fault Events**: Immediate incident ticker displaying active anomalies.

### 2. Live Digital Signal Monitoring
- **Three-Row Synchronized Oscilloscope**:
  - Row 1: Transmitted Signal (TX) clean digital logic levels (0 and 1) with clock annotations.
  - Row 2: Received Signal (RX) exhibiting physical channel effects (rise/fall slew rates, Gaussian noise, jitter, and fault dropouts).
  - Row 3: Discrepancy Error Magnitude ($|TX - RX|$) with highlighted bit inversion flags.
- **Signal Quality Metrics**: Real-time SNR (dB), Timing Jitter (ns), Eye Opening Height (%), and Bit Discrepancy counters.
- **Frame Bitstream Correlation Matrix**: Interactive bit-by-bit comparator displaying TX vs RX bits with red highlighting on corrupted bits.
- **Interactive Controls**: `Start`, `Pause`, `Resume`, `Stop`, `Clear Graph`, Channel Selector (CH1/CH2/CH3), and Frame Length Selector (8, 16, 24, 32 bits).

### 3. Channel Analysis
- Dedicated panels for logical communication channels **CH1**, **CH2**, and **CH3**.
- **Performance Radar Chart**: 5-axis polar analysis comparing Signal Quality, Low Latency Score, Packet Delivery, Low BER Score, and Jitter Stability.
- **Throughput Grouped Bar Chart**: Transmitted vs Received packet volume comparisons.
- **Automated Health Assessment Matrix**: Automated grading (A+ to F) with engineering mitigation recommendations.

### 4. Fault Detection Centre
- **Fault Categories Supported**:
  - `NORMAL`: Nominal baseline protocol operation.
  - `BIT_CORRUPTION`: Pseudorandom bit inversions & CRC check failures.
  - `PACKET_LOSS`: Carrier dropouts & receiver frame drops.
  - `TRANSMISSION_DELAY`: Buffer lag & propagation delay spikes.
  - `BURST_ERROR`: Clustered consecutive bit corruptions with high-density noise.
- **Interactive Test Bench**: Select Target Channel, Fault Category, Severity (Low, Medium, High, Critical), and Duration (10s, 20s, 30s, 60s, or Persistent).
- **Instant Impact Preview**: Real-time oscilloscope preview showing distorted signal waveform immediately upon injection.

### 5. AI Prediction Centre
- **Machine Learning Architecture**:
  - Supervised Classification: **Random Forest Classifier** (100 Estimators) trained on physical metrics vector: `[latency_ms, jitter_ns, snr_db, ber, packet_loss_pct, eye_opening_pct]`.
  - Unsupervised Anomaly Detection: **Isolation Forest** calculating decision function anomaly scores.
- **Real-Time Channel Inference**: Live fault classification with class probability distribution bar chart and out-of-distribution anomaly flag.
- **Genuine Model Evaluation**: Real holdout validation partition metrics (Accuracy, Weighted Precision, Recall, and F1-score).
- **Confusion Matrix Heatmap**: Interactive Plotly heatmap displaying multi-class prediction accuracy.
- **Gini Feature Importances**: Relative significance of physical metrics in fault categorization.
- **Retrain Benchmark Button**: One-click retraining and re-evaluation on fresh synthetic telemetry corpora.

### 6. Signal Analytics
- Multi-dimensional Plotly analytical charts:
  - Packet Transmission & Loss Trend with secondary y-axis.
  - Latency Analysis with 50ms warning threshold indicators.
  - Bit Error Rate (BER) dynamics on logarithmic scale with $10^{-3}$ critical threshold.
  - Fault Category Distribution donut chart.
  - Fault Frequency by Severity and Channel histogram.
- Granular session and channel filtering.

### 7. Alert Centre
- Categorized Incident Tickets: `INFO`, `WARNING`, and `CRITICAL`.
- Incident Management Actions:
  - Working **Acknowledge** button per alert.
  - Working **Mark Resolved** button per alert.
  - Bulk **Acknowledge All Active Alerts** button.
- Status, Severity, and Channel dropdown filters.

### 8. Historical Data
- Comprehensive archive pre-seeded with realistic multi-day communication sessions.
- Tabbed exploration: Sessions Archive, Telemetry Data Points, Fault History, and AI Inference Logs.
- Interactive text search across Session IDs, Channels, and Fault descriptions.

### 9. Reports
- 5 Dedicated Report Templates:
  1. *Communication Performance Report*
  2. *Packet Loss Report*
  3. *Fault Detection & Incident Audit Report*
  4. *Channel Comparison & Bus Matrix Report*
  5. *AI Model Benchmark & Evaluation Report*
- Instant **CSV Export** and styled **Excel (.xlsx)** workbooks with custom headers and tabbed sheets.

### 10. Settings
- **Modular Data Source Selector**: Toggle between `SIMULATION DATA` and `HARDWARE (USB SERIAL / ARDUINO)`.
- **Serial Interface Parameters**: Configurable COM Port (`COM1`-`COM5`, `/dev/ttyUSB0`), Baud Rate (`9600`-`500000`), and connection probe tool.
- **Sampling & Threshold Configurations**: Telemetry sampling interval, signal refresh speed, packet timeout, BER threshold, latency threshold, and packet loss threshold.
- Persistent save and reset to factory defaults via SQLite.

---

## 🔌 Future Hardware Integration (Arduino Nano)

The codebase has been designed so that future physical hardware can be integrated seamlessly:
1. In `core/data_source.py`, the `HardwareSerialDataSource` class implements the exact same `BaseDataSource` abstract interface as `SimulationDataSource`.
2. Connect your **Arduino Nano Transmitter** and **Arduino Nano Receiver** over USB.
3. Configure serial frame parsing inside `HardwareSerialDataSource.read_channel_telemetry()` using `pyserial`.
4. Navigate to the **Settings** page in the dashboard and switch **Active Telemetry Source** to **HARDWARE**.
5. All 10 dashboard pages will display live physical Arduino signals without any modification to the user interface!

