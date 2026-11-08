"""
Page 2: Live Digital Signal Monitoring & Signal Integrity Oscilloscope
Real-time digital waveform visualization, TX vs RX comparison, binary state levels (0 and 1),
clock sync, transition edge visualization, signal quality metrics, interactive controls,
and digital communications Eye Diagram visualizer.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>⚡ Live Digital Signal Monitoring & Waveform Analysis</h2><div class="subtitle">High-resolution physical & logic layer waveform inspection with TX/RX correlation & Eye Diagram</div></div><div class="sim-watermark">SIMULATION HARDWARE ENGINE ACTIVE</div></div>',
        unsafe_allow_html=True
    )

    if "monitoring_state" not in st.session_state:
        st.session_state.monitoring_state = "RUNNING"
    if "waveform_channel" not in st.session_state:
        st.session_state.waveform_channel = "CH1"
    if "num_bits_inspect" not in st.session_state:
        st.session_state.num_bits_inspect = 16
    if "waveform_history_cleared" not in st.session_state:
        st.session_state.waveform_history_cleared = False
    if "auto_stream" not in st.session_state:
        st.session_state.auto_stream = False

    # Top Control Bar
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5, ctrl_col6 = st.columns([1.2, 1.2, 1.2, 1.2, 1.5, 2.5])

    with ctrl_col1:
        if st.button("▶ Start", key="btn_start_monitor", use_container_width=True):
            st.session_state.monitoring_state = "RUNNING"
            st.session_state.waveform_history_cleared = False
            st.rerun()

    with ctrl_col2:
        if st.button("⏸ Pause", key="btn_pause_monitor", use_container_width=True):
            st.session_state.monitoring_state = "PAUSED"
            st.rerun()

    with ctrl_col3:
        if st.button("⏯ Resume", key="btn_resume_monitor", use_container_width=True):
            st.session_state.monitoring_state = "RUNNING"
            st.rerun()

    with ctrl_col4:
        if st.button("⏹ Stop", key="btn_stop_monitor", use_container_width=True):
            st.session_state.monitoring_state = "STOPPED"
            st.rerun()

    with ctrl_col5:
        if st.button("🗑 Clear Graph", key="btn_clear_graph", use_container_width=True):
            st.session_state.waveform_history_cleared = True
            st.rerun()

    with ctrl_col6:
        col_ch, col_bits = st.columns(2)
        with col_ch:
            st.session_state.waveform_channel = st.selectbox(
                "Channel",
                ["CH1", "CH2", "CH3"],
                index=["CH1", "CH2", "CH3"].index(st.session_state.waveform_channel),
                label_visibility="collapsed"
            )
        with col_bits:
            st.session_state.num_bits_inspect = st.selectbox(
                "Bits",
                [8, 16, 24, 32],
                index=[8, 16, 24, 32].index(st.session_state.num_bits_inspect),
                label_visibility="collapsed"
            )

    # Status Banner & Streaming Toggle
    state_badges = {
        "RUNNING": '<span class="status-chip chip-operational"><span class="pulse-dot pulse-green"></span> LIVE ACQUISITION ACTIVE</span>',
        "PAUSED": '<span class="status-chip chip-hardware"><span class="pulse-dot pulse-amber"></span> ACQUISITION PAUSED</span>',
        "STOPPED": '<span class="status-chip chip-simulated"><span class="pulse-dot pulse-red"></span> MONITORING HALTED</span>'
    }

    stat_col1, stat_col2 = st.columns([3, 1])
    with stat_col1:
        st.markdown(
            f'<div style="background:rgba(15,25,48,0.5); border:1px solid rgba(30,58,138,0.3); border-radius:8px; padding:7px 14px; font-size:0.8rem; display:flex; justify-content:space-between; align-items:center;"><div>INSPECTION TARGET: <b style="color:#00f2fe;">{st.session_state.waveform_channel}</b> | FRAME LENGTH: <b>{st.session_state.num_bits_inspect} BITS</b></div><div>{state_badges.get(st.session_state.monitoring_state, "")}</div></div>',
            unsafe_allow_html=True
        )
    with stat_col2:
        auto_refresh = st.toggle("⚡ Continuous Stream", value=st.session_state.auto_stream, key="toggle_auto_stream")
        st.session_state.auto_stream = auto_refresh

    if st.session_state.waveform_history_cleared or st.session_state.monitoring_state == "STOPPED":
        st.markdown(
            '<div style="text-align:center; padding:60px 20px; background:rgba(15,25,48,0.3); border:1px dashed rgba(30,58,138,0.4); border-radius:12px; margin:20px 0;"><h3 style="color:#64748b; margin-bottom:8px;">Signal Acquisition Idle</h3><p style="color:#94a3b8; font-size:0.85rem;">Graph buffer has been cleared or monitoring stopped. Click <b>"Start"</b> or <b>"Resume"</b> above to acquire real-time frames.</p></div>',
            unsafe_allow_html=True
        )
        return

    # Fragment container for continuous streaming without whole-page flicker
    if st.session_state.auto_stream and st.session_state.monitoring_state == "RUNNING":
        _render_waveform_streaming_fragment(data_source, run_every=2)
    else:
        _render_waveform_content(data_source)


def _render_waveform_streaming_fragment(data_source, run_every=2):
    """Wrapped in st.fragment to stream live signal frames every N seconds."""
    @st.fragment(run_every=f"{run_every}s")
    def _streaming_inner():
        _render_waveform_content(data_source)
    _streaming_inner()


def _render_waveform_content(data_source):
    waveform_data = data_source.get_waveform_data(
        channel=st.session_state.waveform_channel,
        num_bits=st.session_state.num_bits_inspect
    )

    t = waveform_data["time_ms"]
    tx_v = waveform_data["tx_voltage"]
    rx_v = waveform_data["rx_voltage"]
    tx_bits = waveform_data["tx_bits"]
    rx_bits = waveform_data["rx_bits"]
    discrepancies = waveform_data["discrepancies"]
    metrics = waveform_data["metrics"]
    eye_data = waveform_data.get("eye_diagram", {})

    # Signal Quality KPI Ribbon
    q_col1, q_col2, q_col3, q_col4, q_col5 = st.columns(5)
    with q_col1:
        st.metric("Signal Quality", f"{metrics['signal_quality']}%", delta=None)
    with q_col2:
        st.metric("SNR (Signal-to-Noise)", f"{metrics['snr_db']} dB")
    with q_col3:
        st.metric("Timing Jitter", f"{metrics['jitter_ns']} ns")
    with q_col4:
        st.metric("Eye Opening Height", f"{metrics['eye_opening_pct']}%")
    with q_col5:
        st.metric("Bit Discrepancies", f"{len(discrepancies)} bits", delta=f"{'-' if discrepancies else '0'} err")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Tabs: Time-Domain Waveforms vs Eye Diagram
    tab_time, tab_eye = st.tabs([
        "📈 Time-Domain Multi-Trace Oscilloscope",
        "👁️ High-Speed Eye Diagram & Noise Margin Analysis"
    ])

    with tab_time:
        # Multi-Row Synchronized Digital Waveform Visualizer
        fig_signal = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=(
                f"TRANSMITTED SIGNAL (TX) — Clean Logic Levels (0 / 1)",
                f"RECEIVED SIGNAL (RX) — Channel Physics, Slew Rate & Jitter",
                f"DIFFERENTIAL CORRELATION & BIT DISCREPANCY DETECTION"
            )
        )

        # 1. TX Ideal Waveform
        fig_signal.add_trace(
            go.Scatter(
                x=t, y=tx_v,
                name="TX Signal",
                mode="lines",
                line=dict(color="#00f2fe", width=2.5, shape="hv"),
                fill="tozeroy",
                fillcolor="rgba(0, 242, 254, 0.08)"
            ),
            row=1, col=1
        )

        # 2. RX Waveform with Channel Distortion
        rx_color = "#00e676" if not discrepancies else "#ff1744"
        fig_signal.add_trace(
            go.Scatter(
                x=t, y=rx_v,
                name="RX Physical Signal",
                mode="lines",
                line=dict(color=rx_color, width=2.0)
            ),
            row=2, col=1
        )

        # 3. Discrepancy & Difference Curve
        diff = np.abs(np.array(tx_v) - np.array(rx_v))
        fig_signal.add_trace(
            go.Scatter(
                x=t, y=diff,
                name="Error Magnitude (|TX - RX|)",
                mode="lines",
                line=dict(color="#f59e0b", width=1.5),
                fill="tozeroy",
                fillcolor="rgba(245, 158, 11, 0.15)"
            ),
            row=3, col=1
        )

        # Annotate bit values on TX Waveform
        samples_per_bit = len(t) // len(tx_bits)
        for i, b in enumerate(tx_bits):
            mid_idx = min(int((i + 0.5) * samples_per_bit), len(t) - 1)
            t_mid = t[mid_idx]
            bit_color = "#ffffff" if i not in discrepancies else "#ff1744"
            fig_signal.add_annotation(
                x=t_mid, y=1.15,
                text=f"<b>{b}</b>",
                showarrow=False,
                font=dict(size=11, color=bit_color, family="JetBrains Mono"),
                row=1, col=1
            )

        # Annotate discrepancies on RX Waveform
        for d_idx in discrepancies:
            mid_idx = min(int((d_idx + 0.5) * samples_per_bit), len(t) - 1)
            t_mid = t[mid_idx]
            fig_signal.add_annotation(
                x=t_mid, y=0.5,
                text="⚠️ BIT CORRUPT",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#ff1744",
                font=dict(size=9, color="#ff1744", family="JetBrains Mono"),
                bgcolor="rgba(255,23,68,0.2)",
                bordercolor="#ff1744",
                row=2, col=1
            )

        fig_signal.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 25, 48, 0.5)",
            font=dict(color="#cbd5e1", family="Outfit"),
            height=560,
            margin=dict(l=40, r=20, t=35, b=35),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        fig_signal.update_xaxes(showgrid=True, gridcolor="rgba(30,58,138,0.25)", row=3, col=1, title="Time (ms)")
        fig_signal.update_yaxes(showgrid=True, gridcolor="rgba(30,58,138,0.25)", row=1, col=1, range=[-0.2, 1.4], title="TX (V)")
        fig_signal.update_yaxes(showgrid=True, gridcolor="rgba(30,58,138,0.25)", row=2, col=1, range=[-0.3, 1.4], title="RX (V)")
        fig_signal.update_yaxes(showgrid=True, gridcolor="rgba(30,58,138,0.25)", row=3, col=1, range=[0.0, 1.5], title="Diff (V)")

        st.plotly_chart(fig_signal, use_container_width=True)

        # Frame Bit Sequence Comparison
        bit_cards_html = []
        for i, (tx_b, rx_b) in enumerate(zip(tx_bits, rx_bits)):
            is_mismatch = (tx_b != rx_b)
            border_c = "#ff1744" if is_mismatch else "#1e3a8a"
            bg_c = "rgba(255,23,68,0.2)" if is_mismatch else "rgba(11,20,39,0.7)"
            rx_c = "#ff1744" if is_mismatch else "#00e676"
            card = f'<div style="flex:1; min-width:32px; text-align:center; background:{bg_c}; border:1px solid {border_c}; border-radius:4px; padding:4px 2px; font-family:\'JetBrains Mono\';"><div style="font-size:0.65rem; color:#64748b;">#{i}</div><div style="font-size:0.85rem; font-weight:700; color:#00f2fe;">{tx_b}</div><div style="font-size:0.85rem; font-weight:700; color:{rx_c};">{rx_b}</div></div>'
            bit_cards_html.append(card)

        all_cards = "".join(bit_cards_html)
        st.markdown(
            f'<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:14px 18px;"><h4 style="margin:0 0 10px 0; color:#00f2fe; font-size:0.95rem;">FRAME BITSTREAM CORRELATION MATRIX</h4><div style="display:flex; gap:6px; overflow-x:auto; padding-bottom:6px;">{all_cards}</div><div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.75rem; color:#94a3b8;"><span>Top: Bit Index | Middle: TX Bit | Bottom: Demodulated RX Bit</span><span style="color:#00f2fe;">Cyan: Transmitted</span><span style="color:#00e676;">Green: Demodulated Match</span><span style="color:#ff1744;">Red: Inversion Error</span></div></div>',
            unsafe_allow_html=True
        )

    with tab_eye:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #a855f7; border-radius:12px; padding:12px 18px 4px 18px; margin-bottom:12px;"><h4 style="margin:0; color:#a855f7; font-size:1.0rem;">DIGITAL COMMUNICATIONS EYE DIAGRAM PERSISTENCE OVERLAY</h4><p style="font-size:0.8rem; color:#94a3b8; margin:4px 0 0 0;">Superimposes multiple symbol intervals over a 2-bit Unit Interval (UI) window to evaluate inter-symbol interference (ISI), rise/fall jitter, and noise margins.</p></div>',
            unsafe_allow_html=True
        )

        eye_traces = eye_data.get("traces", [])
        time_ui = eye_data.get("time_ui", [])

        if eye_traces and time_ui:
            fig_eye = go.Figure()
            # Overlay all 2-bit symbol traces with semi-transparent cyan styling
            for idx, trace in enumerate(eye_traces):
                trace_color = "rgba(0, 242, 254, 0.28)" if not discrepancies else "rgba(255, 23, 68, 0.35)"
                fig_eye.add_trace(go.Scatter(
                    x=time_ui,
                    y=trace,
                    mode="lines",
                    line=dict(color=trace_color, width=1.8),
                    showlegend=False,
                    hoverinfo="skip"
                ))

            # Add reference threshold lines
            fig_eye.add_hline(y=0.5, line_dash="dash", line_color="#f59e0b", annotation_text="Decision Threshold (0.5V)")
            fig_eye.add_vline(x=1.0, line_dash="dot", line_color="#0066ff", annotation_text="Optimum Sampling Strobe (1.0 UI)")

            fig_eye.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 25, 48, 0.5)",
                font=dict(color="#cbd5e1", family="Outfit"),
                height=420,
                margin=dict(l=40, r=20, t=30, b=35),
                xaxis=dict(title="Symbol Time (Unit Intervals, UI)", range=[0.0, 2.0], showgrid=True, gridcolor="rgba(30,58,138,0.25)"),
                yaxis=dict(title="Normalized Receiver Amplitude (V)", range=[-0.25, 1.35], showgrid=True, gridcolor="rgba(30,58,138,0.25)")
            )
            st.plotly_chart(fig_eye, use_container_width=True)

            # Eye Metrics Summary
            eye_col1, eye_col2, eye_col3 = st.columns(3)
            with eye_col1:
                st.markdown(f'<div style="background:rgba(11,20,39,0.7); border:1px solid rgba(30,58,138,0.3); border-radius:8px; padding:10px; font-size:0.8rem;"><span style="color:#64748b; font-size:0.7rem;">EYE OPENING HEIGHT</span><br><b style="font-size:1.2rem; color:#00e676;">{metrics["eye_opening_pct"]}%</b><div style="font-size:0.72rem; color:#94a3b8; margin-top:2px;">Proportional to Noise Margin</div></div>', unsafe_allow_html=True)
            with eye_col2:
                st.markdown(f'<div style="background:rgba(11,20,39,0.7); border:1px solid rgba(30,58,138,0.3); border-radius:8px; padding:10px; font-size:0.8rem;"><span style="color:#64748b; font-size:0.7rem;">HORIZONTAL EYE JITTER</span><br><b style="font-size:1.2rem; color:#00f2fe;">{metrics["jitter_ns"]} ns</b><div style="font-size:0.72rem; color:#94a3b8; margin-top:2px;">Zero-Crossing Time Dispersion</div></div>', unsafe_allow_html=True)
            with eye_col3:
                st.markdown(f'<div style="background:rgba(11,20,39,0.7); border:1px solid rgba(30,58,138,0.3); border-radius:8px; padding:10px; font-size:0.8rem;"><span style="color:#64748b; font-size:0.7rem;">MEAN RISE / FALL SLEW</span><br><b style="font-size:1.2rem; color:#ffffff;">{metrics["rise_time_us"]} µs</b><div style="font-size:0.72rem; color:#94a3b8; margin-top:2px;">10% to 90% Voltage Slew Rate</div></div>', unsafe_allow_html=True)
        else:
            st.info("Insufficient samples to construct persistence overlay.")
