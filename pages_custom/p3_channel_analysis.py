"""
Page 3: Channel Analysis (CH1, CH2, CH3)
Dedicated telemetry analysis for the three logical communication channels.
Includes individual channel status cards, comparative radar charts, throughput comparisons,
and automated channel health assessments.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.formatters import format_number, format_ber, get_channel_badge_html


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>📶 Multi-Channel Communication Performance Analysis</h2><div class="subtitle">Tri-channel logical bus comparison, throughput benchmarking, and health scoring</div></div><div class="sim-watermark">LOGICAL CHANNELS (CH1, CH2, CH3)</div></div>',
        unsafe_allow_html=True
    )

    telemetry = data_source.read_all_channels_telemetry()

    # Filter controls
    col_filter1, col_filter2 = st.columns([2, 4])
    with col_filter1:
        selected_ch = st.selectbox(
            "Channel Focus Filter",
            ["ALL CHANNELS", "CH1", "CH2", "CH3"],
            key="ch_analysis_filter"
        )

    # 1. Individual Channel Cards
    st.markdown("<h4 style='color:#00f2fe; margin:10px 0 12px 0;'>CHANNEL TELEMETRY PANELS</h4>", unsafe_allow_html=True)
    cards_col1, cards_col2, cards_col3 = st.columns(3)

    for idx, ch in enumerate(["CH1", "CH2", "CH3"]):
        ch_data = telemetry.get(ch, {})
        f_type = ch_data.get("fault_type", "NORMAL")
        is_healthy = ch_data.get("is_healthy", True)
        accent = "#00e676" if is_healthy else "#ff1744"
        tx_cnt = ch_data.get("tx_packets", 0)
        rx_cnt = ch_data.get("rx_packets", 0)
        loss = ch_data.get("packet_loss_pct", 0.0)
        lat = ch_data.get("latency_ms", 0.0)
        ber = ch_data.get("ber", 0.0)
        sq = ch_data.get("signal_quality_pct", 100.0)
        errs = ch_data.get("error_count", 0)

        opacity = "1.0" if (selected_ch == "ALL CHANNELS" or selected_ch == ch) else "0.35"

        with [cards_col1, cards_col2, cards_col3][idx]:
            st.markdown(
                f'''<div style="opacity:{opacity}; background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid {accent}; border-radius:12px; padding:14px 16px; margin-bottom:14px;"><div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(30,58,138,0.3); padding-bottom:8px; margin-bottom:10px;"><div><span style="font-size:1.2rem; font-weight:700; color:#00f2fe;">{ch}</span><span style="font-size:0.75rem; color:#94a3b8; margin-left:6px;">LOGICAL BUS</span></div><span style="background:{accent}22; color:{accent}; border:1px solid {accent}66; padding:2px 8px; border-radius:4px; font-size:0.72rem; font-weight:600;">{f_type}</span></div><div style="display:grid; grid-template-columns: 1fr 1fr; gap: 8px; font-family:\'JetBrains Mono\'; font-size:0.75rem;"><div style="background:rgba(11,20,39,0.6); padding:6px; border-radius:4px;"><span style="color:#64748b; font-size:0.68rem;">TX PACKETS</span><br><b style="color:#ffffff;">{format_number(tx_cnt)}</b></div><div style="background:rgba(11,20,39,0.6); padding:6px; border-radius:4px;"><span style="color:#64748b; font-size:0.68rem;">RX PACKETS</span><br><b style="color:#ffffff;">{format_number(rx_cnt)}</b></div><div style="background:rgba(11,20,39,0.6); padding:6px; border-radius:4px;"><span style="color:#64748b; font-size:0.68rem;">PACKET LOSS</span><br><b style="color:{accent};">{loss:.2f}%</b></div><div style="background:rgba(11,20,39,0.6); padding:6px; border-radius:4px;"><span style="color:#64748b; font-size:0.68rem;">LATENCY</span><br><b style="color:#ffffff;">{lat:.1f} ms</b></div><div style="background:rgba(11,20,39,0.6); padding:6px; border-radius:4px;"><span style="color:#64748b; font-size:0.68rem;">BIT ERRORS</span><br><b style="color:#ffb300;">{errs} err</b></div><div style="background:rgba(11,20,39,0.6); padding:6px; border-radius:4px;"><span style="color:#64748b; font-size:0.68rem;">SIGNAL QUALITY</span><br><b style="color:#00e676;">{sq:.1f}%</b></div></div><div style="margin-top:10px; font-size:0.72rem; color:#94a3b8; font-family:monospace;">BER: <span style="color:#00f2fe;">{format_ber(ber)}</span></div></div>''',
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 2. Channel Comparison Visualizations
    col_chart_left, col_chart_right = st.columns([1, 1])

    with col_chart_left:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:10px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">CHANNEL PERFORMANCE RADAR</h4></div>',
            unsafe_allow_html=True
        )

        categories = ["Signal Quality", "Low Latency Score", "Packet Delivery", "Low BER Score", "Jitter Stability"]
        fig_radar = go.Figure()
        colors = {"CH1": "#00f2fe", "CH2": "#0066ff", "CH3": "#a855f7"}

        for ch in ["CH1", "CH2", "CH3"]:
            c_data = telemetry.get(ch, {})
            sq = c_data.get("signal_quality_pct", 95.0)
            lat = max(0.0, 100.0 - c_data.get("latency_ms", 12.0) * 0.7)
            delivery = 100.0 - c_data.get("packet_loss_pct", 0.0)
            ber_val = c_data.get("ber", 1e-5)
            ber_score = max(0.0, 100.0 - (ber_val * 10000.0))
            jitter_score = 90.0 if c_data.get("fault_type") == "NORMAL" else 55.0

            r_vals = [sq, lat, delivery, ber_score, jitter_score]
            r_vals.append(r_vals[0])

            fig_radar.add_trace(go.Scatterpolar(
                r=r_vals,
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor=f"{colors[ch]}22",
                line=dict(color=colors[ch], width=2),
                name=ch
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#64748b", gridcolor="rgba(30,58,138,0.25)"),
                angularaxis=dict(color="#cbd5e1", gridcolor="rgba(30,58,138,0.25)")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=35, r=35, t=25, b=25),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_chart_right:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #0066ff; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:10px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">THROUGHPUT & PACKET LOSS COMPARISON</h4></div>',
            unsafe_allow_html=True
        )

        ch_names = ["CH1", "CH2", "CH3"]
        tx_vals = [telemetry[c]["tx_packets"] for c in ch_names]
        rx_vals = [telemetry[c]["rx_packets"] for c in ch_names]

        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(
            name="Transmitted (TX)",
            x=ch_names,
            y=tx_vals,
            marker_color="#0066ff"
        ))
        fig_bars.add_trace(go.Bar(
            name="Received (RX)",
            x=ch_names,
            y=rx_vals,
            marker_color="#00f2fe"
        ))

        fig_bars.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 25, 48, 0.4)",
            font=dict(color="#cbd5e1", family="Outfit"),
            height=300,
            margin=dict(l=40, r=20, t=25, b=30),
            xaxis=dict(gridcolor="rgba(30,58,138,0.2)"),
            yaxis=dict(gridcolor="rgba(30,58,138,0.2)", title="Total Packets"),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_bars, use_container_width=True)

    # 3. Channel Assessment Table
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:12px 16px 6px 16px; margin-bottom:12px;"><h4 style="margin:0 0 6px 0; color:#00f2fe; font-size:1.0rem;">CHANNEL HEALTH ASSESSMENT & OPTIMIZATION RECOMMENDATIONS</h4><div style="font-size:0.8rem; color:#94a3b8;">Automated rule engine evaluation for high-speed digital communications bus:</div></div>',
        unsafe_allow_html=True
    )

    eval_data = []
    for ch in ["CH1", "CH2", "CH3"]:
        d = telemetry[ch]
        loss = d["packet_loss_pct"]
        lat = d["latency_ms"]
        fault = d["fault_type"]

        if fault == "NORMAL":
            status_desc = "Optimal Channel Stability"
            rec = "No mitigation required. Signal within normal NRZ specification."
            rank = "A+ (Excellent)"
        elif fault == "PACKET_LOSS":
            status_desc = "Severe Packet Drop / Timeout"
            rec = "Verify receiver FIFO buffer size; initiate packet retransmission request."
            rank = "D (Degraded)"
        elif fault == "BIT_CORRUPTION":
            status_desc = "Single/Double Bit Parity Failure"
            rec = "Increase SNR margin; inspect channel capacitive load; enable CRC-16 retry."
            rank = "C (Attention Required)"
        elif fault == "TRANSMISSION_DELAY":
            status_desc = "Propagation Lag Spikes"
            rec = "Reduce buffer queue length; check for serial baud-rate clock drift."
            rank = "B- (Moderate)"
        else:
            status_desc = "Impulse Noise Burst Cluster"
            rec = "Apply Reed-Solomon forward error correction; check grounding."
            rank = "F (Critical)"

        eval_data.append({
            "Channel": ch,
            "Operating State": fault,
            "Health Grade": rank,
            "Latency": f"{lat:.1f} ms",
            "Packet Loss": f"{loss:.2f}%",
            "Engineering Assessment": status_desc,
            "Recommended Action": rec
        })

    df_eval = pd.DataFrame(eval_data)
    st.dataframe(df_eval, use_container_width=True, hide_index=True)
