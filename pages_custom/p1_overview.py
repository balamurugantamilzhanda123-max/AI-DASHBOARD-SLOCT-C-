"""
Page 1: Dashboard Overview
Executive telemetry overview displaying 8 KPI cards, system health gauge,
communication status, channel cards, recent fault events, and signal activity chart.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from components.kpi_cards import render_kpi_cards
from core.database import get_fault_events, get_telemetry_history
from utils.formatters import get_severity_badge_html, get_channel_badge_html, format_ber, format_number


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>📊 Executive Dashboard Overview</h2><div class="subtitle">Real-time digital communication health, channel telemetry, and fault telemetry</div></div><div class="sim-watermark">SIMULATION BENCHMARK ACTIVE</div></div>',
        unsafe_allow_html=True
    )

    # 1. Fetch system summary
    summary = data_source.get_system_summary()

    # 2. Render 8 KPI Cards
    render_kpi_cards(summary)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 3. System Health and Channel Status Cards
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:16px 18px;"><h4 style="margin:0 0 10px 0; color:#00f2fe; font-size:1.0rem; letter-spacing:0.5px;">SYSTEM HEALTH INDEX</h4>',
            unsafe_allow_html=True
        )

        health_score = summary.get("health_score", 96.5)
        gauge_color = "#00e676" if health_score >= 85 else ("#ffb300" if health_score >= 65 else "#ff1744")

        # Plotly Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            number={"suffix": "%", "font": {"size": 34, "color": "#ffffff", "family": "JetBrains Mono"}},
            title={"text": f"Status: {summary.get('comm_status')}", "font": {"size": 13, "color": gauge_color}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#1e3a8a"},
                "bar": {"color": gauge_color, "thickness": 0.28},
                "bgcolor": "rgba(15, 25, 48, 0.4)",
                "borderwidth": 1,
                "bordercolor": "#1e3a8a",
                "steps": [
                    {"range": [0, 65], "color": "rgba(255, 23, 68, 0.15)"},
                    {"range": [65, 85], "color": "rgba(255, 179, 0, 0.15)"},
                    {"range": [85, 100], "color": "rgba(0, 230, 118, 0.15)"}
                ],
                "threshold": {
                    "line": {"color": "#00f2fe", "width": 3},
                    "thickness": 0.75,
                    "value": health_score
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=180,
            margin=dict(l=15, r=15, t=10, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown(
            '<div style="font-size:0.75rem; color:#94a3b8; line-height:1.5; border-top:1px solid rgba(30,58,138,0.3); padding-top:8px;"><b>Evaluation Summary:</b> Channels operating under normal protocol constraints. Composite score computed from Bit Error Rate, Latency bounds, and Packet Acknowledgement ratio.</div></div>',
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #0066ff; border-radius:12px; padding:16px 18px; margin-bottom:14px;"><h4 style="margin:0 0 12px 0; color:#00f2fe; font-size:1.0rem; letter-spacing:0.5px;">LOGICAL COMMUNICATION CHANNELS MATRIX</h4></div>',
            unsafe_allow_html=True
        )

        ch_cols = st.columns(3)
        channels = summary.get("channels", {})

        for idx, (ch_name, ch_data) in enumerate(channels.items()):
            with ch_cols[idx]:
                f_type = ch_data.get("fault_type", "NORMAL")
                is_healthy = ch_data.get("is_healthy", True)
                status_color = "#00e676" if is_healthy else "#ff1744"
                border_color = "rgba(0, 230, 118, 0.4)" if is_healthy else "rgba(255, 23, 68, 0.5)"

                st.markdown(f'''<div style="background: rgba(11, 20, 39, 0.7); border: 1px solid {border_color}; border-radius: 8px; padding: 12px; font-family: 'JetBrains Mono', monospace;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;"><span style="font-size:1.1rem; font-weight:700; color:#00f2fe;">{ch_name}</span><span style="font-size:0.7rem; background:{status_color}22; color:{status_color}; border:1px solid {status_color}55; padding:2px 6px; border-radius:4px;">{f_type}</span></div><div style="font-size:0.75rem; color:#cbd5e1; line-height:1.7;"><div>TX Packets: <b style="color:#ffffff;">{format_number(ch_data.get('tx_packets', 0))}</b></div><div>RX Packets: <b style="color:#ffffff;">{format_number(ch_data.get('rx_packets', 0))}</b></div><div>Loss: <b style="color:{status_color};">{ch_data.get('packet_loss_pct', 0.0):.2f}%</b></div><div>Latency: <b style="color:#ffffff;">{ch_data.get('latency_ms', 0.0):.1f} ms</b></div><div>BER: <b style="color:#ffffff;">{format_ber(ch_data.get('ber', 0.0))}</b></div><div>Quality: <b style="color:#00e676;">{ch_data.get('signal_quality_pct', 0.0):.1f}%</b></div></div></div>''', unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 4. Signal Activity Chart and Recent Fault Events
    col_chart, col_events = st.columns([3, 2])

    with col_chart:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:12px 18px 6px 18px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem; letter-spacing:0.5px;">REAL-TIME SIGNAL TELEMETRY & THROUGHPUT</h4></div>',
            unsafe_allow_html=True
        )

        recent_telemetry = get_telemetry_history(limit=60)
        if recent_telemetry:
            df_hist = pd.DataFrame(recent_telemetry)
            df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"])
            df_hist = df_hist.sort_values("timestamp")

            fig_activity = go.Figure()
            channel_colors = {"CH1": "#00f2fe", "CH2": "#0066ff", "CH3": "#a855f7"}

            for ch, c_col in channel_colors.items():
                ch_df = df_hist[df_hist["channel"] == ch]
                if not ch_df.empty:
                    fig_activity.add_trace(go.Scatter(
                        x=ch_df["timestamp"],
                        y=ch_df["latency"],
                        name=f"{ch} Latency (ms)",
                        mode="lines+markers",
                        line=dict(color=c_col, width=2),
                        marker=dict(size=4)
                    ))

            fig_activity.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 25, 48, 0.4)",
                font=dict(color="#94a3b8", family="Outfit"),
                height=260,
                margin=dict(l=30, r=20, t=20, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=True, gridcolor="rgba(30,58,138,0.2)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(30,58,138,0.2)", title="Latency (ms)")
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        else:
            st.info("Generating telemetry stream...")

    with col_events:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #ff1744; border-radius:12px; padding:12px 18px 6px 18px;"><div style="display:flex; justify-content:space-between; align-items:center;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem; letter-spacing:0.5px;">RECENT FAULT EVENTS</h4><span style="font-size:0.75rem; color:#64748b;">LIVE LOG</span></div></div><div style="height:8px;"></div>',
            unsafe_allow_html=True
        )

        recent_faults = get_fault_events(limit=5)
        if recent_faults:
            for f in recent_faults:
                t_str = f["timestamp"].split("T")[1][:8] if "T" in f["timestamp"] else f["timestamp"]
                badge = get_severity_badge_html(f["severity"])
                ch_badge = get_channel_badge_html(f["channel"])
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between; align-items:center; padding:7px 10px; background:rgba(12,20,39,0.8); border-left:3px solid #ff1744; border-radius:4px; margin-bottom:6px; font-size:0.75rem;"><div>{ch_badge} <b style="color:#ffffff; margin-left:4px;">{f["fault_type"]}</b><div style="font-size:0.68rem; color:#94a3b8; margin-top:2px;">{f["description"]}</div></div><div style="text-align:right;">{badge}<div style="font-size:0.65rem; color:#64748b; font-family:monospace; margin-top:2px;">{t_str}</div></div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<p style='font-size:0.8rem; color:#64748b; text-align:center;'>No active fault events detected.</p>", unsafe_allow_html=True)
