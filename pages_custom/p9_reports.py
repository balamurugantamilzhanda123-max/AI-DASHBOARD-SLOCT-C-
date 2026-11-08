"""
Page 9: Reports
Comprehensive engineering report generator.
Generates and downloads:
1. Communication Performance Report
2. Packet Loss Report
3. Fault Detection Report
4. Channel Comparison Report
5. AI Model Evaluation Report
Supports both CSV and multi-sheet styled Excel (.xlsx) formats.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from core.database import (
    get_all_sessions,
    get_telemetry_history,
    get_fault_events,
    get_alerts
)
from core.ai_engine import ai_engine
from utils.exporter import generate_csv, generate_excel_report
from utils.formatters import format_number, format_ber


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>📑 Engineering Reports & Telemetry Export</h2><div class="subtitle">Compliance auditing, statistical summaries, and export to CSV / Excel (.xlsx)</div></div><div class="sim-watermark">REPORTING & AUDIT ENGINE</div></div>',
        unsafe_allow_html=True
    )

    # Report Selector
    report_types = [
        "1. Communication Performance Report",
        "2. Packet Loss Report",
        "3. Fault Detection & Incident Report",
        "4. Channel Comparison & Bus Matrix Report",
        "5. AI Model Benchmark & Evaluation Report"
    ]

    sel_report = st.selectbox("Select Report Template", report_types, key="report_sel_template")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 1. Communication Performance Report
    if "1." in sel_report:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:12px 18px 6px 18px; margin-bottom:12px;"><h4 style="margin:0 0 6px 0; color:#00f2fe; font-size:1.05rem;">COMMUNICATION PERFORMANCE REPORT</h4><p style="font-size:0.8rem; color:#94a3b8; margin:0;">Aggregates global throughput, channel latency bounds, Bit Error Rate, and overall communication efficiency.</p></div>',
            unsafe_allow_html=True
        )

        telemetry = get_telemetry_history(limit=250)
        df_telem = pd.DataFrame(telemetry) if telemetry else pd.DataFrame()

        if not df_telem.empty:
            summary_stats = {
                "Metric": ["Total Telemetry Samples", "Mean Latency (ms)", "Max Latency (ms)", "Mean Signal Quality", "Mean BER"],
                "Value": [
                    len(df_telem),
                    f"{df_telem['latency'].mean():.2f} ms",
                    f"{df_telem['latency'].max():.2f} ms",
                    f"{df_telem['signal_quality'].mean():.2f}%",
                    format_ber(df_telem['ber'].mean())
                ]
            }
            st.dataframe(pd.DataFrame(summary_stats), use_container_width=True, hide_index=True)

            csv_bytes = generate_csv(df_telem)
            excel_bytes = generate_excel_report("Performance Report", {"Telemetry_History": df_telem})

            col_d1, col_d2, _ = st.columns([1.5, 1.5, 3])
            with col_d1:
                st.download_button("📥 Download CSV", data=csv_bytes, file_name="Communication_Performance_Report.csv", mime="text/csv", use_container_width=True)
            with col_d2:
                st.download_button("📊 Download Excel (.xlsx)", data=excel_bytes, file_name="Communication_Performance_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    # 2. Packet Loss Report
    elif "2." in sel_report:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #ff1744; border-radius:12px; padding:12px 18px 6px 18px; margin-bottom:12px;"><h4 style="margin:0 0 6px 0; color:#00f2fe; font-size:1.05rem;">PACKET LOSS & TRANSMISSION INTEGRITY REPORT</h4><p style="font-size:0.8rem; color:#94a3b8; margin:0;">Detailed analysis of packet drop ratios, retry occurrences, and channel loss distributions.</p></div>',
            unsafe_allow_html=True
        )

        telemetry = get_telemetry_history(limit=250)
        df_telem = pd.DataFrame(telemetry) if telemetry else pd.DataFrame()

        if not df_telem.empty:
            df_loss = df_telem[["timestamp", "channel", "tx_packets", "rx_packets", "packet_loss", "fault_state"]].copy()
            df_loss = df_loss.rename(columns={"packet_loss": "packet_loss_pct"})

            st.dataframe(df_loss.head(15), use_container_width=True, hide_index=True)

            csv_bytes = generate_csv(df_loss)
            excel_bytes = generate_excel_report("Packet Loss Report", {"Packet_Loss_Data": df_loss})

            col_d1, col_d2, _ = st.columns([1.5, 1.5, 3])
            with col_d1:
                st.download_button("📥 Download CSV", data=csv_bytes, file_name="Packet_Loss_Report.csv", mime="text/csv", use_container_width=True)
            with col_d2:
                st.download_button("📊 Download Excel (.xlsx)", data=excel_bytes, file_name="Packet_Loss_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    # 3. Fault Detection & Incident Report
    elif "3." in sel_report:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #ffb300; border-radius:12px; padding:12px 18px 6px 18px; margin-bottom:12px;"><h4 style="margin:0 0 6px 0; color:#00f2fe; font-size:1.05rem;">FAULT DETECTION & INCIDENT AUDIT REPORT</h4><p style="font-size:0.8rem; color:#94a3b8; margin:0;">Logs all detected signal anomalies, severity levels, channel disruptions, and mitigation recommendations.</p></div>',
            unsafe_allow_html=True
        )

        faults = get_fault_events(limit=200)
        alerts = get_alerts()
        df_faults = pd.DataFrame(faults) if faults else pd.DataFrame()
        df_alerts = pd.DataFrame(alerts) if alerts else pd.DataFrame()

        if not df_faults.empty:
            st.dataframe(df_faults.head(15), use_container_width=True, hide_index=True)

            csv_bytes = generate_csv(df_faults)
            excel_bytes = generate_excel_report("Fault Incident Report", {
                "Detected_Faults": df_faults,
                "Alert_Log": df_alerts
            })

            col_d1, col_d2, _ = st.columns([1.5, 1.5, 3])
            with col_d1:
                st.download_button("📥 Download CSV", data=csv_bytes, file_name="Fault_Detection_Report.csv", mime="text/csv", use_container_width=True)
            with col_d2:
                st.download_button("📊 Download Excel (.xlsx)", data=excel_bytes, file_name="Fault_Detection_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    # 4. Channel Comparison Report
    elif "4." in sel_report:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #0066ff; border-radius:12px; padding:12px 18px 6px 18px; margin-bottom:12px;"><h4 style="margin:0 0 6px 0; color:#00f2fe; font-size:1.05rem;">CHANNEL COMPARISON & BUS MATRIX REPORT</h4><p style="font-size:0.8rem; color:#94a3b8; margin:0;">Comparative metrics evaluating CH1, CH2, and CH3 reliability, throughput, and error density.</p></div>',
            unsafe_allow_html=True
        )

        telemetry = data_source.read_all_channels_telemetry()
        ch_rows = []
        for ch, d in telemetry.items():
            ch_rows.append({
                "Channel": ch,
                "Status": d["status"],
                "TX Packets": d["tx_packets"],
                "RX Packets": d["rx_packets"],
                "Packet Loss (%)": d["packet_loss_pct"],
                "Mean Latency (ms)": d["latency_ms"],
                "Bit Error Rate": format_ber(d["ber"]),
                "Signal Quality (%)": d["signal_quality_pct"]
            })
        df_ch = pd.DataFrame(ch_rows)
        st.dataframe(df_ch, use_container_width=True, hide_index=True)

        csv_bytes = generate_csv(df_ch)
        excel_bytes = generate_excel_report("Channel Comparison", {"Channel_Matrix": df_ch})

        col_d1, col_d2, _ = st.columns([1.5, 1.5, 3])
        with col_d1:
            st.download_button("📥 Download CSV", data=csv_bytes, file_name="Channel_Comparison_Report.csv", mime="text/csv", use_container_width=True)
        with col_d2:
            st.download_button("📊 Download Excel (.xlsx)", data=excel_bytes, file_name="Channel_Comparison_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    # 5. AI Model Evaluation Report
    elif "5." in sel_report:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #a855f7; border-radius:12px; padding:12px 18px 6px 18px; margin-bottom:12px;"><h4 style="margin:0 0 6px 0; color:#00f2fe; font-size:1.05rem;">AI MODEL EVALUATION & BENCHMARK REPORT</h4><p style="font-size:0.8rem; color:#94a3b8; margin:0;">Comprehensive verification metrics: Accuracy, Precision, Recall, F1-Score, Confusion Matrix, and Gini Feature Importance.</p></div>',
            unsafe_allow_html=True
        )

        eval_res = ai_engine.evaluation_results
        metric_summary = pd.DataFrame({
            "Evaluation Metric": ["Accuracy", "Weighted Precision", "Weighted Recall", "F1-Score", "Evaluation Timestamp", "Dataset Source"],
            "Result": [
                f"{eval_res.get('accuracy', 0.0) * 100:.2f}%",
                f"{eval_res.get('precision', 0.0) * 100:.2f}%",
                f"{eval_res.get('recall', 0.0) * 100:.2f}%",
                f"{eval_res.get('f1_score', 0.0) * 100:.2f}%",
                eval_res.get("trained_timestamp", str(datetime.now())),
                "Synthetic Digital Communications Physical Distribution"
            ]
        })
        st.dataframe(metric_summary, use_container_width=True, hide_index=True)

        feat_df = pd.DataFrame(list(eval_res.get("feature_importances", {}).items()), columns=["Feature", "Gini Importance"])
        st.markdown("<h5 style='color:#cbd5e1; margin-top:10px;'>Feature Importances</h5>", unsafe_allow_html=True)
        st.dataframe(feat_df, use_container_width=True, hide_index=True)

        csv_bytes = generate_csv(metric_summary)
        excel_bytes = generate_excel_report("AI Model Evaluation", {
            "Model_Metrics": metric_summary,
            "Feature_Importances": feat_df
        })

        col_d1, col_d2, _ = st.columns([1.5, 1.5, 3])
        with col_d1:
            st.download_button("📥 Download CSV", data=csv_bytes, file_name="AI_Model_Evaluation_Report.csv", mime="text/csv", use_container_width=True)
        with col_d2:
            st.download_button("📊 Download Excel (.xlsx)", data=excel_bytes, file_name="AI_Model_Evaluation_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
