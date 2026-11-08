"""
Page 8: Historical Data
Professional historical data explorer featuring session archives,
telemetry records, historical fault occurrences, and AI prediction audit logs.
Includes search, date filtering, and record sorting.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from core.database import (
    get_all_sessions,
    get_telemetry_history,
    get_fault_events,
    get_ai_predictions
)
from utils.formatters import format_number, format_ber, get_severity_badge_html


def render_page(data_source):
    st.markdown("""
    <div class="section-header">
        <div>
            <h2>📜 Historical Telemetry & Session Records</h2>
            <div class="subtitle">Searchable telemetry archives, prior communication sessions, and AI classification logs</div>
        </div>
        <div class="sim-watermark">DATABASE AUDIT ARCHIVE</div>
    </div>
    """, unsafe_allow_html=True)

    # Search and Filter Bar
    s_col1, s_col2, s_col3 = st.columns([3, 2, 1.5])
    with s_col1:
        search_query = st.text_input("🔍 Search Telemetry & Faults", placeholder="Filter by Session ID, Fault Type, or Channel...", key="hist_search")
    with s_col2:
        sessions = get_all_sessions()
        session_choices = ["ALL SESSIONS"] + [s["session_id"] for s in sessions]
        selected_sess = st.selectbox("Select Session", session_choices, key="hist_sess_filter")
    with s_col3:
        record_limit = st.selectbox("Record Limit", [50, 100, 250, 500], index=1, key="hist_limit")

    sess_filter = None if selected_sess == "ALL SESSIONS" else selected_sess

    # Tabbed Interface
    tab_sessions, tab_telemetry, tab_faults, tab_ai = st.tabs([
        "📁 Communication Sessions",
        "📊 Telemetry History",
        "🚨 Fault History",
        "🧠 AI Prediction Log"
    ])

    # 1. Sessions Archive Tab
    with tab_sessions:
        st.markdown("<h4 style='color:#00f2fe; margin-top:8px;'>COMMUNICATION SESSION LOGS</h4>", unsafe_allow_html=True)
        if sessions:
            df_sess = pd.DataFrame(sessions)
            if search_query:
                df_sess = df_sess[df_sess["session_id"].str.contains(search_query, case=False, na=False)]
            
            df_sess["total_packets"] = df_sess["total_packets"].apply(format_number)
            st.dataframe(df_sess, use_container_width=True, hide_index=True)
        else:
            st.info("No session records found.")

    # 2. Telemetry History Tab
    with tab_telemetry:
        st.markdown("<h4 style='color:#00f2fe; margin-top:8px;'>CHANNEL TELEMETRY DATA POINTS</h4>", unsafe_allow_html=True)
        telemetry = get_telemetry_history(session_id=sess_filter, limit=record_limit)
        if telemetry:
            df_telem = pd.DataFrame(telemetry)
            if search_query:
                mask = (
                    df_telem["session_id"].str.contains(search_query, case=False, na=False) |
                    df_telem["channel"].str.contains(search_query, case=False, na=False) |
                    df_telem["fault_state"].str.contains(search_query, case=False, na=False)
                )
                df_telem = df_telem[mask]

            df_telem["ber"] = df_telem["ber"].apply(format_ber)
            df_telem["packet_loss"] = df_telem["packet_loss"].apply(lambda x: f"{x:.2f}%")
            df_telem["signal_quality"] = df_telem["signal_quality"].apply(lambda x: f"{x:.1f}%")
            df_telem["latency"] = df_telem["latency"].apply(lambda x: f"{x:.1f} ms")

            st.dataframe(df_telem, use_container_width=True, hide_index=True)
        else:
            st.info("No telemetry matching the criteria.")

    # 3. Fault History Tab
    with tab_faults:
        st.markdown("<h4 style='color:#00f2fe; margin-top:8px;'>FAULT EVENT ARCHIVE</h4>", unsafe_allow_html=True)
        faults = get_fault_events(session_id=sess_filter, limit=record_limit)
        if faults:
            df_faults = pd.DataFrame(faults)
            if search_query:
                mask = (
                    df_faults["fault_type"].str.contains(search_query, case=False, na=False) |
                    df_faults["description"].str.contains(search_query, case=False, na=False) |
                    df_faults["channel"].str.contains(search_query, case=False, na=False)
                )
                df_faults = df_faults[mask]

            st.dataframe(df_faults, use_container_width=True, hide_index=True)
        else:
            st.info("No fault records found.")

    # 4. AI Prediction History Tab
    with tab_ai:
        st.markdown("<h4 style='color:#00f2fe; margin-top:8px;'>AI INFERENCE & ANOMALY LOGS</h4>", unsafe_allow_html=True)
        preds = get_ai_predictions(limit=record_limit)
        if preds:
            df_preds = pd.DataFrame(preds)
            if search_query:
                mask = (
                    df_preds["channel"].str.contains(search_query, case=False, na=False) |
                    df_preds["predicted_fault"].str.contains(search_query, case=False, na=False)
                )
                df_preds = df_preds[mask]

            df_preds["confidence"] = df_preds["confidence"].apply(lambda x: f"{x * 100:.1f}%")
            df_preds["is_anomaly"] = df_preds["is_anomaly"].apply(lambda x: "⚠️ ANOMALY" if x == 1 else "✅ NORMAL")
            st.dataframe(df_preds, use_container_width=True, hide_index=True)
        else:
            st.info("No AI predictions recorded yet.")

