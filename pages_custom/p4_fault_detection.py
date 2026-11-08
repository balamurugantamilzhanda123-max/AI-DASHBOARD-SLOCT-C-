"""
Page 4: Fault Detection Centre
Comprehensive fault management, interactive fault injection test bench,
fault impact visualization, and fault occurrence telemetry.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from core.fault_injector import fault_injector
from core.database import get_fault_events
from utils.formatters import get_severity_badge_html, get_channel_badge_html


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>🚨 Fault Detection & Injection Control Centre</h2><div class="subtitle">Diagnostic fault classification, interactive stress testing, and real-time impact analysis</div></div><div class="sim-watermark">FAULT INJECTION BENCH ACTIVE</div></div>',
        unsafe_allow_html=True
    )

    # 1. Interactive Fault Injection Console
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(255,23,68,0.4); border-left:4px solid #ff1744; border-radius:12px; padding:14px 18px 8px 18px; margin-bottom:12px;"><div style="display:flex; justify-content:space-between; align-items:center;"><h4 style="margin:0; color:#ff1744; font-size:1.05rem; letter-spacing:0.5px;">⚡ INTERACTIVE FAULT INJECTION TEST BENCH</h4><span style="font-size:0.75rem; color:#f87171; font-family:monospace;">SIMULATION TESTING HARNESS</span></div><p style="font-size:0.8rem; color:#94a3b8; margin:6px 0 0 0;">Inject controlled signal anomalies to evaluate physical layer degradation, AI detection response, and alert propagation:</p></div>',
        unsafe_allow_html=True
    )

    inj_col1, inj_col2, inj_col3, inj_col4 = st.columns([1.5, 2.5, 1.5, 1.5])

    with inj_col1:
        target_ch = st.selectbox(
            "Target Channel",
            ["CH1", "CH2", "CH3", "ALL"],
            key="inj_target_ch"
        )

    with inj_col2:
        fault_choice = st.selectbox(
            "Fault Category",
            [
                "BIT_CORRUPTION (Single/Double Bit Flips)",
                "PACKET_LOSS (Carrier Dropout / Frame Drops)",
                "TRANSMISSION_DELAY (Phase Lag & Buffer Bloat)",
                "BURST_ERROR (High-Density Clustered Inversions)",
                "NORMAL (Nominal Baseline Protocol)"
            ],
            key="inj_fault_cat"
        )
        selected_fault_type = fault_choice.split(" ")[0]

    with inj_col3:
        severity_choice = st.selectbox(
            "Severity Level",
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            index=2,
            key="inj_sev_level"
        )

    with inj_col4:
        duration_choice = st.selectbox(
            "Duration",
            [10, 20, 30, 60, 0],
            format_func=lambda x: f"{x} seconds" if x > 0 else "Persistent (Manual Clear)",
            index=1,
            key="inj_duration"
        )

    btn_col1, btn_col2, _ = st.columns([2, 2, 4])
    with btn_col1:
        if st.button("🔥 Inject Test Fault", key="btn_trigger_fault", type="primary", use_container_width=True):
            fault_injector.inject_fault(
                channel=target_ch,
                fault_type=selected_fault_type,
                severity=severity_choice,
                duration_sec=duration_choice
            )
            st.success(f"Injected {selected_fault_type} on {target_ch} ({severity_choice})!")
            st.rerun()

    with btn_col2:
        if st.button("🔄 Restore Normal Baseline", key="btn_clear_all_faults", use_container_width=True):
            fault_injector.clear_fault("ALL")
            st.info("Restored nominal baseline across all channels.")
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Real-Time Fault Impact Comparison View
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:12px 18px 4px 18px; margin-bottom:12px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">LIVE FAULT IMPACT ON DIGITAL SIGNAL & BUS METRICS</h4></div>',
        unsafe_allow_html=True
    )

    active_faults = fault_injector.get_all_active_faults()
    target_inspect = target_ch if target_ch != "ALL" else "CH1"
    curr_fault = active_faults.get(target_inspect, {"type": "NORMAL"})

    desc_col1, desc_col2 = st.columns([1, 2])
    with desc_col1:
        st.markdown(f'''<div style="background:rgba(11,20,39,0.8); border:1px solid rgba(30,58,138,0.4); border-radius:8px; padding:12px; font-size:0.8rem;"><div style="color:#64748b; font-size:0.7rem;">CURRENT TARGET:</div><div style="font-size:1.1rem; font-weight:700; color:#00f2fe; margin-bottom:8px;">{target_inspect}</div><div>Active Condition: <b style="color:#ffffff;">{curr_fault["type"]}</b></div><div>Severity: <b style="color:#ffb300;">{curr_fault.get("severity", "INFO")}</b></div><div style="margin-top:6px; color:#cbd5e1; font-size:0.75rem;"><b>Physical Manifestation:</b> {curr_fault.get("description", "Operating within tolerances.")}</div></div>''', unsafe_allow_html=True)

    with desc_col2:
        wf = data_source.get_waveform_data(channel=target_inspect, num_bits=12)
        fig_preview = go.Figure()
        fig_preview.add_trace(go.Scatter(
            x=wf["time_ms"], y=wf["tx_voltage"],
            name="TX Expected",
            mode="lines",
            line=dict(color="#0066ff", width=1.5, dash="dash")
        ))
        fig_preview.add_trace(go.Scatter(
            x=wf["time_ms"], y=wf["rx_voltage"],
            name="RX Distorted",
            mode="lines",
            line=dict(color="#00f2fe" if curr_fault["type"] == "NORMAL" else "#ff1744", width=2.0)
        ))
        fig_preview.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 25, 48, 0.4)",
            height=160,
            margin=dict(l=20, r=20, t=10, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_preview, use_container_width=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Fault Events History Table with Filtering
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:12px 18px 6px 18px; margin-bottom:12px;"><div style="display:flex; justify-content:space-between; align-items:center;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">FAULT DETECTION AUDIT LOG</h4><span style="font-size:0.75rem; color:#94a3b8;">FILTERABLE DATABASE AUDIT</span></div></div>',
        unsafe_allow_html=True
    )

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        f_channel = st.selectbox("Channel Filter", ["ALL", "CH1", "CH2", "CH3"], key="audit_filter_ch")
    with f_col2:
        f_sev = st.selectbox("Severity Filter", ["ALL", "CRITICAL", "WARNING", "INFO"], key="audit_filter_sev")
    with f_col3:
        f_limit = st.selectbox("Record Limit", [20, 50, 100], key="audit_filter_limit")

    events = get_fault_events(channel=f_channel, severity=f_sev, limit=f_limit)

    if events:
        df_events = pd.DataFrame(events)
        df_display = df_events[["id", "timestamp", "channel", "fault_type", "severity", "description", "ai_detected"]]
        df_display = df_display.rename(columns={
            "id": "Fault ID",
            "timestamp": "Timestamp",
            "channel": "Channel",
            "fault_type": "Fault Type",
            "severity": "Severity",
            "description": "Engineering Description",
            "ai_detected": "AI Verified"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No fault records found matching current filter.")
