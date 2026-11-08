"""
KPI Cards Component
Renders the 8 primary executive KPI metric cards with futuristic neon accents.
"""

import streamlit as st
from utils.formatters import format_number, format_ber


def render_kpi_cards(summary: dict):
    """
    Renders 8 KPI metric cards in two neat responsive rows of 4 columns.
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Total TX Packets</span><span>📤</span></div><div class="kpi-value kpi-value-cyan">{format_number(summary.get('total_tx', 0))}</div><div class="kpi-subtitle"><span>Simulated Ingress Stream</span></div></div>''',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Total RX Packets</span><span>📥</span></div><div class="kpi-value kpi-value-green">{format_number(summary.get('total_rx', 0))}</div><div class="kpi-subtitle"><span>Demodulated & Verified</span></div></div>''',
            unsafe_allow_html=True
        )

    with col3:
        loss = summary.get('packet_loss_pct', 0.0)
        val_cls = "kpi-value-green" if loss < 1.0 else ("kpi-value-amber" if loss < 5.0 else "kpi-value-red")
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Packet Loss</span><span>📉</span></div><div class="kpi-value {val_cls}">{loss:.2f}%</div><div class="kpi-subtitle"><span>Target &lt; 2.0%</span></div></div>''',
            unsafe_allow_html=True
        )

    with col4:
        sq = summary.get('signal_quality_pct', 98.0)
        val_cls = "kpi-value-green" if sq >= 90.0 else ("kpi-value-amber" if sq >= 75.0 else "kpi-value-red")
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Signal Quality</span><span>📶</span></div><div class="kpi-value {val_cls}">{sq:.1f}%</div><div class="kpi-subtitle"><span>SNR / Eye Index</span></div></div>''',
            unsafe_allow_html=True
        )

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        lat = summary.get('avg_latency_ms', 12.0)
        val_cls = "kpi-value-green" if lat < 25.0 else ("kpi-value-amber" if lat < 70.0 else "kpi-value-red")
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Avg Latency</span><span>⏱️</span></div><div class="kpi-value {val_cls}">{lat:.2f} ms</div><div class="kpi-subtitle"><span>Loopback Propagation</span></div></div>''',
            unsafe_allow_html=True
        )

    with col6:
        ber = summary.get('avg_ber', 1e-5)
        val_cls = "kpi-value-green" if ber < 1e-4 else ("kpi-value-amber" if ber < 1e-3 else "kpi-value-red")
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Bit Error Rate (BER)</span><span>🔬</span></div><div class="kpi-value {val_cls}">{format_ber(ber)}</div><div class="kpi-subtitle"><span>Statistical Ratio</span></div></div>''',
            unsafe_allow_html=True
        )

    with col7:
        faults = summary.get('total_faults_detected', 0)
        val_cls = "kpi-value-green" if faults == 0 else "kpi-value-red"
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Detected Faults</span><span>⚠️</span></div><div class="kpi-value {val_cls}">{faults} ACTIVE</div><div class="kpi-subtitle"><span>Real-time Anomaly Engine</span></div></div>''',
            unsafe_allow_html=True
        )

    with col8:
        uptime = summary.get('uptime_str', '04h 32m 18s')
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>System Uptime</span><span>⏳</span></div><div class="kpi-value kpi-value-cyan">{uptime}</div><div class="kpi-subtitle"><span>Session Continuous</span></div></div>''',
            unsafe_allow_html=True
        )
