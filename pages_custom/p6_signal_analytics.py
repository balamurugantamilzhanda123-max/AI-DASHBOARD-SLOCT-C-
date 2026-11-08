"""
Page 6: Signal Analytics
Advanced Plotly data visualizations: packet trends, loss trends, latency analysis,
BER distributions, signal quality tracking, and fault frequency over time.
Supports multi-channel filtering and session date filtering.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from core.database import get_telemetry_history, get_fault_events, get_all_sessions


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>📈 Advanced Signal Analytics & Telemetry Distributions</h2><div class="subtitle">Multi-dimensional trend analysis, BER spectrum, jitter distributions, and historical telemetry</div></div><div class="sim-watermark">SIGNAL ANALYTICS ENGINE</div></div>',
        unsafe_allow_html=True
    )

    # Filter Bar
    sessions = get_all_sessions()
    session_options = ["ALL SESSIONS"] + [s["session_id"] for s in sessions]

    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        selected_session = st.selectbox("Telemetry Session", session_options, key="analytics_sess_filter")
    with f_col2:
        selected_channel = st.selectbox("Channel Focus", ["ALL", "CH1", "CH2", "CH3"], key="analytics_ch_filter")
    with f_col3:
        sample_limit = st.selectbox("Data Points to Sample", [100, 250, 500, 1000], index=1, key="analytics_limit")

    # Fetch telemetry
    sess_arg = None if selected_session == "ALL SESSIONS" else selected_session
    telemetry_rows = get_telemetry_history(session_id=sess_arg, channel=selected_channel, limit=sample_limit)

    if not telemetry_rows:
        st.warning("No telemetry records found for current filter selection.")
        return

    df = pd.DataFrame(telemetry_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # 1. Packet Transmission vs Reception & Loss Trend
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:8px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">PACKET TRANSMISSION THROUGHPUT & LOSS TREND</h4></div>',
        unsafe_allow_html=True
    )

    fig_packets = make_subplots(specs=[[{"secondary_y": True}]])

    fig_packets.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["tx_packets"],
            name="TX Packets",
            mode="lines",
            line=dict(color="#0066ff", width=2)
        ),
        secondary_y=False
    )
    fig_packets.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["rx_packets"],
            name="RX Packets",
            mode="lines",
            line=dict(color="#00f2fe", width=2, dash="dot")
        ),
        secondary_y=False
    )
    fig_packets.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["packet_loss"],
            name="Packet Loss (%)",
            mode="lines",
            line=dict(color="#ff1744", width=2),
            fill="tozeroy",
            fillcolor="rgba(255, 23, 68, 0.12)"
        ),
        secondary_y=True
    )

    fig_packets.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 25, 48, 0.4)",
        font=dict(color="#cbd5e1", family="Outfit"),
        height=300,
        margin=dict(l=30, r=30, t=10, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_packets.update_xaxes(showgrid=True, gridcolor="rgba(30,58,138,0.2)")
    fig_packets.update_yaxes(title_text="Packet Volume", showgrid=True, gridcolor="rgba(30,58,138,0.2)", secondary_y=False)
    fig_packets.update_yaxes(title_text="Packet Loss (%)", range=[0, max(25, df['packet_loss'].max() + 5)], showgrid=False, secondary_y=True)

    st.plotly_chart(fig_packets, use_container_width=True)

    # 2. Latency & Bit Error Rate (BER) Analysis
    col_lat, col_ber = st.columns([1, 1])

    with col_lat:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:8px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">TRANSMISSION LATENCY ANALYSIS (ms)</h4></div>',
            unsafe_allow_html=True
        )

        fig_lat = px.line(
            df, x="timestamp", y="latency", color="channel",
            color_discrete_map={"CH1": "#00f2fe", "CH2": "#0066ff", "CH3": "#a855f7"},
            labels={"latency": "Latency (ms)"}
        )
        fig_lat.add_hline(y=50.0, line_dash="dash", line_color="#ffb300", annotation_text="Warning Threshold (50ms)")
        fig_lat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 25, 48, 0.4)",
            font=dict(color="#cbd5e1", family="Outfit"),
            height=280,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    with col_ber:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #0066ff; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:8px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">BIT ERROR RATE (BER) DYNAMICS</h4></div>',
            unsafe_allow_html=True
        )

        fig_ber = px.line(
            df, x="timestamp", y="ber", color="channel",
            color_discrete_map={"CH1": "#00f2fe", "CH2": "#0066ff", "CH3": "#a855f7"},
            labels={"ber": "BER (Log Scale)"},
            log_y=True
        )
        fig_ber.add_hline(y=1e-3, line_dash="dash", line_color="#ff1744", annotation_text="Critical BER (10⁻³)")
        fig_ber.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 25, 48, 0.4)",
            font=dict(color="#cbd5e1", family="Outfit"),
            height=280,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ber, use_container_width=True)

    # 3. Fault Category Distribution & Frequency Over Time
    col_dist, col_freq = st.columns([1, 1])
    fault_records = get_fault_events(session_id=sess_arg, channel=selected_channel, limit=200)

    with col_dist:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #ff1744; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:8px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">FAULT CATEGORY DISTRIBUTION</h4></div>',
            unsafe_allow_html=True
        )

        if fault_records:
            df_faults = pd.DataFrame(fault_records)
            fault_counts = df_faults["fault_type"].value_counts().reset_index()
            fault_counts.columns = ["Fault Type", "Count"]

            fig_donut = px.pie(
                fault_counts, values="Count", names="Fault Type",
                hole=0.55,
                color_discrete_sequence=["#ff1744", "#ffb300", "#0066ff", "#00f2fe", "#a855f7"]
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#cbd5e1", family="Outfit"),
                height=260,
                margin=dict(l=20, r=20, t=10, b=10)
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No recorded faults in selected scope.")

    with col_freq:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #ffb300; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:8px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">FAULT FREQUENCY BY SEVERITY & CHANNEL</h4></div>',
            unsafe_allow_html=True
        )

        if fault_records:
            df_faults = pd.DataFrame(fault_records)
            fig_hist = px.histogram(
                df_faults, x="channel", color="severity",
                barmode="group",
                color_discrete_map={"CRITICAL": "#ff1744", "WARNING": "#ffb300", "INFO": "#00f2fe"}
            )
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 25, 48, 0.4)",
                font=dict(color="#cbd5e1", family="Outfit"),
                height=260,
                margin=dict(l=20, r=20, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No fault counts to aggregate.")
