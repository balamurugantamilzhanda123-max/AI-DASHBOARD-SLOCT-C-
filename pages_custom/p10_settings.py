"""
Page 10: Settings
System configuration management.
Includes data source selection (Simulation vs Live Arduino Serial Hardware Mode),
dynamic COM port discovery, baud rate selection, connection lifecycle control,
sampling timing, fault thresholds, and UI preferences.
Persists settings directly to SQLite database.
"""

import streamlit as st
from core.database import get_setting, save_setting
from core.serial_reader import serial_reader
from core.data_source import get_data_source


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>⚙️ System Parameters & Configuration Settings</h2><div class="subtitle">Hardware serial interfaces, sampling timing, threshold triggers, and UI preferences</div></div><div class="sim-watermark">CONFIGURATION REGISTRY</div></div>',
        unsafe_allow_html=True
    )

    # 1. Data Source Architecture Settings
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:12px 18px 4px 18px; margin-bottom:12px;"><h4 style="margin:0 0 4px 0; color:#00f2fe; font-size:1.05rem;">DATA SOURCE CONFIGURATION</h4><p style="font-size:0.8rem; color:#94a3b8; margin:0;">Select between High-Fidelity Signal Simulation and Live Hardware Interface (Arduino Nano Transmitter / Receiver via USB Serial):</p></div>',
        unsafe_allow_html=True
    )

    curr_source = get_setting("data_source", "SIMULATION")
    source_choice = st.radio(
        "Active Telemetry Source",
        ["SIMULATION (Internal Physics Simulator)", "HARDWARE (Arduino Nano USB Serial Port)"],
        index=0 if "SIMULATION" in curr_source else 1,
        key="set_source_radio"
    )
    new_source_mode = "SIMULATION" if "SIMULATION" in source_choice else "HARDWARE"

    # Hardware Serial Settings Sub-Panel
    with st.expander("🔌 Hardware Serial Port Configuration (Arduino Nano Interface)", expanded=("HARDWARE" in source_choice)):
        st.markdown(
            '<div style="font-size:0.78rem; color:#cbd5e1; margin-bottom:10px;">Connect the Arduino Nano Receiver to any USB port. The non-blocking background reader ingests serial frames without blocking the dashboard interface.</div>',
            unsafe_allow_html=True
        )

        detected_ports = serial_reader.list_available_ports()
        default_port = get_setting("serial_port", "COM3")
        port_options = list(set(detected_ports + ["COM1", "COM2", "COM3", "COM4", "COM5", "/dev/ttyUSB0"]))
        port_options.sort()

        h_col1, h_col2, h_col3 = st.columns(3)
        with h_col1:
            port = st.selectbox(
                "Serial Port",
                port_options,
                index=port_options.index(default_port) if default_port in port_options else 0,
                key="set_serial_port"
            )
        with h_col2:
            baud_options = ["9600", "19200", "38400", "57600", "115200", "230400", "500000"]
            default_baud = get_setting("baud_rate", "115200")
            baud = st.selectbox(
                "Baud Rate",
                baud_options,
                index=baud_options.index(default_baud) if default_baud in baud_options else 4,
                key="set_baud_rate"
            )
        with h_col3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("🔗 Connect", key="btn_serial_connect", type="primary", use_container_width=True):
                    ok, msg = serial_reader.connect(port, int(baud))
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()
            with c_btn2:
                if st.button("🔌 Disconnect", key="btn_serial_disconnect", use_container_width=True):
                    serial_reader.disconnect()
                    st.info("Serial port disconnected.")
                    st.rerun()

        # Serial Diagnostics Status Card
        ser_info = serial_reader.get_status_info()
        status_color = "#00e676" if ser_info["status"] == "LIVE HARDWARE STREAMING" else ("#ffb300" if "WAITING" in ser_info["status"] else "#ff1744")
        st.markdown(
            f'''<div style="background:rgba(11,20,39,0.7); border:1px solid rgba(30,58,138,0.4); border-radius:8px; padding:10px 14px; margin-top:10px; font-family:\'JetBrains Mono\'; font-size:0.75rem;"><div style="display:flex; justify-content:space-between; align-items:center;"><div>DRIVER STATUS: <b style="color:{status_color};">{ser_info["status"]}</b></div><div>PORT: <b>{ser_info["port"]} @ {ser_info["baud_rate"]} bps</b></div></div><div style="color:#94a3b8; font-size:0.7rem; margin-top:4px;">Detail: {ser_info["status_detail"]}</div><div style="display:flex; gap:16px; margin-top:6px; color:#cbd5e1;"><span>Bytes RX: <b style="color:#00f2fe;">{ser_info["bytes_received"]}</b></span><span>Frames Parsed: <b style="color:#00e676;">{ser_info["frames_parsed"]}</b></span><span>Parse Errors: <b style="color:#ff1744;">{ser_info["parse_errors"]}</b></span><span>Queue: <b>{ser_info["queue_size"]}</b></span></div></div>''',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Timing and Sampling Parameters
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #0066ff; border-radius:12px; padding:12px 18px 4px 18px; margin-bottom:12px;"><h4 style="margin:0; color:#00f2fe; font-size:1.05rem;">SAMPLING & TIMING PARAMETERS</h4></div>',
        unsafe_allow_html=True
    )

    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        sampling_ms = st.selectbox(
            "Telemetry Sampling Rate",
            ["50 ms", "100 ms", "250 ms", "500 ms", "1000 ms"],
            index=1,
            key="set_sampling_ms"
        )
    with t_col2:
        update_sec = st.slider(
            "Signal Refresh Interval (s)",
            min_value=0.5,
            max_value=5.0,
            value=float(get_setting("signal_update_interval_sec", "1.0")),
            step=0.5,
            key="set_update_sec"
        )
    with t_col3:
        timeout_ms = st.number_input(
            "Packet Drop Timeout (ms)",
            min_value=100,
            max_value=2000,
            value=int(get_setting("packet_timeout_ms", "500")),
            step=50,
            key="set_timeout_ms"
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Fault Detection Thresholds
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #ffb300; border-radius:12px; padding:12px 18px 4px 18px; margin-bottom:12px;"><h4 style="margin:0; color:#00f2fe; font-size:1.05rem;">ANOMALY & THRESHOLD RULES</h4></div>',
        unsafe_allow_html=True
    )

    th_col1, th_col2, th_col3 = st.columns(3)
    with th_col1:
        ber_th = st.number_input(
            "Bit Error Rate (BER) Trigger",
            min_value=0.00001,
            max_value=0.1,
            value=float(get_setting("ber_threshold", "0.001")),
            format="%.5f",
            key="set_ber_th"
        )
    with th_col2:
        lat_th = st.number_input(
            "Latency Warning Threshold (ms)",
            min_value=10.0,
            max_value=500.0,
            value=float(get_setting("latency_threshold_ms", "50.0")),
            step=5.0,
            key="set_lat_th"
        )
    with th_col3:
        loss_th = st.number_input(
            "Packet Loss Critical Threshold (%)",
            min_value=1.0,
            max_value=50.0,
            value=float(get_setting("packet_loss_threshold_pct", "5.0")),
            step=1.0,
            key="set_loss_th"
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 4. Action Buttons: Save & Reset
    act_col1, act_col2, _ = st.columns([1.5, 1.5, 4])
    with act_col1:
        if st.button("💾 Save Settings", key="btn_save_settings", type="primary", use_container_width=True):
            save_setting("data_source", new_source_mode)
            save_setting("serial_port", port)
            save_setting("baud_rate", baud)
            save_setting("signal_update_interval_sec", str(update_sec))
            save_setting("packet_timeout_ms", str(timeout_ms))
            save_setting("ber_threshold", str(ber_th))
            save_setting("latency_threshold_ms", str(lat_th))
            save_setting("packet_loss_threshold_pct", str(loss_th))
            st.session_state.data_source_mode = new_source_mode
            st.session_state.data_source = get_data_source(new_source_mode)
            st.success("System configuration saved successfully!")
            st.rerun()

    with act_col2:
        if st.button("🔄 Reset Defaults", key="btn_reset_defaults", use_container_width=True):
            save_setting("data_source", "SIMULATION")
            save_setting("serial_port", "COM3")
            save_setting("baud_rate", "115200")
            save_setting("signal_update_interval_sec", "1.0")
            save_setting("packet_timeout_ms", "500")
            save_setting("ber_threshold", "0.001")
            save_setting("latency_threshold_ms", "50.0")
            save_setting("packet_loss_threshold_pct", "5.0")
            st.session_state.data_source_mode = "SIMULATION"
            st.session_state.data_source = get_data_source("SIMULATION")
            st.info("Configuration reset to factory defaults.")
            st.rerun()
