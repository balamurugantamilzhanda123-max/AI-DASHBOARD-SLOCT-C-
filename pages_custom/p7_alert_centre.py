"""
Page 7: Alert Centre
Advanced notification and alert management interface.
Displays alerts by severity (INFO, WARNING, CRITICAL), provides functional
acknowledgement and resolution workflows, and offers granular filtering.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from core.database import get_alerts, update_alert_status
from utils.formatters import get_severity_badge_html, get_channel_badge_html


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>🔔 Real-Time Alert Centre & Incident Management</h2><div class="subtitle">Threshold monitoring, active telemetry triggers, and alert acknowledgement queue</div></div><div class="sim-watermark">INCIDENT OPERATIONS QUEUE</div></div>',
        unsafe_allow_html=True
    )

    # 1. Alert Summary KPIs
    all_alerts = get_alerts()
    active_alerts = [a for a in all_alerts if a["status"] == "ACTIVE"]
    crit_count = sum(1 for a in active_alerts if a["severity"] == "CRITICAL")
    warn_count = sum(1 for a in active_alerts if a["severity"] in ["WARNING", "MEDIUM", "HIGH"])
    ack_count = sum(1 for a in all_alerts if a["status"] == "ACKNOWLEDGED")
    res_count = sum(1 for a in all_alerts if a["status"] == "RESOLVED")

    k_col1, k_col2, k_col3, k_col4 = st.columns(4)

    with k_col1:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Active Alerts</span><span>🚨</span></div><div class="kpi-value {'kpi-value-red' if len(active_alerts) > 0 else 'kpi-value-green'}">{len(active_alerts)}</div><div class="kpi-subtitle"><span>Requiring Operator Action</span></div></div>''',
            unsafe_allow_html=True
        )

    with k_col2:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Critical Incidents</span><span>💥</span></div><div class="kpi-value {'kpi-value-red' if crit_count > 0 else 'kpi-value-green'}">{crit_count}</div><div class="kpi-subtitle"><span>Burst Errors / Packet Loss</span></div></div>''',
            unsafe_allow_html=True
        )

    with k_col3:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Acknowledged</span><span>👁️</span></div><div class="kpi-value kpi-value-amber">{ack_count}</div><div class="kpi-subtitle"><span>Under Investigation</span></div></div>''',
            unsafe_allow_html=True
        )

    with k_col4:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Resolved Incidents</span><span>✅</span></div><div class="kpi-value kpi-value-green">{res_count}</div><div class="kpi-subtitle"><span>Restored to Nominal</span></div></div>''',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Filter & Bulk Action Toolbar
    st.markdown(
        '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:10px 16px 2px 16px; margin-bottom:12px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">ALERT FILTERS & OPERATIONAL ACTIONS</h4></div>',
        unsafe_allow_html=True
    )

    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1.5, 2.5])
    with f1:
        sel_status = st.selectbox("Status Filter", ["ALL", "ACTIVE", "ACKNOWLEDGED", "RESOLVED"], index=1, key="alt_status_filter")
    with f2:
        sel_sev = st.selectbox("Severity Filter", ["ALL", "CRITICAL", "WARNING", "INFO"], key="alt_sev_filter")
    with f3:
        sel_ch = st.selectbox("Channel Filter", ["ALL", "CH1", "CH2", "CH3"], key="alt_ch_filter")

    with f4:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("✔️ Acknowledge All Active Alerts", key="btn_ack_all", use_container_width=True):
            for a in active_alerts:
                update_alert_status(a["id"], "ACKNOWLEDGED")
            st.success(f"Acknowledged {len(active_alerts)} alerts!")
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Filtered Alert Incident Stream
    filtered_alerts = get_alerts(status=sel_status, severity=sel_sev, channel=sel_ch)

    if filtered_alerts:
        st.markdown("<h4 style='color:#00f2fe; margin-bottom:10px;'>INCIDENT NOTIFICATION STREAM</h4>", unsafe_allow_html=True)

        for a in filtered_alerts:
            a_id = a["id"]
            status = a["status"]
            sev = a["severity"]
            ch = a["channel"]
            f_type = a["fault_type"]
            msg = a["message"]
            t_stamp = a["timestamp"].replace("T", " ")[:19]

            status_style = {
                "ACTIVE": "color:#ff1744; font-weight:700;",
                "ACKNOWLEDGED": "color:#ffb300; font-weight:600;",
                "RESOLVED": "color:#00e676; font-weight:600;"
            }.get(status, "color:#94a3b8;")

            col_info, col_actions = st.columns([4, 1.5])

            with col_info:
                st.markdown(
                    f'''<div style="background:rgba(11,20,39,0.7); border:1px solid {'rgba(255,23,68,0.4)' if status == 'ACTIVE' else 'rgba(30,58,138,0.3)'}; border-left:4px solid {'#ff1744' if sev == 'CRITICAL' else ('#ffb300' if sev == 'WARNING' else '#0066ff')}; border-radius:6px; padding:10px 14px; margin-bottom:10px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;"><div><span style="font-family:monospace; font-weight:700; color:#00f2fe; margin-right:8px;">{a_id}</span>{get_channel_badge_html(ch)}<b style="color:#ffffff; margin-left:6px;">{f_type}</b></div><div>{get_severity_badge_html(sev)}<span style="margin-left:8px; font-size:0.75rem; font-family:monospace; {status_style}">[{status}]</span></div></div><div style="font-size:0.8rem; color:#cbd5e1; margin-top:4px;">{msg}</div><div style="font-size:0.68rem; color:#64748b; font-family:monospace; margin-top:6px;">LOGGED: {t_stamp}</div></div>''',
                    unsafe_allow_html=True
                )

            with col_actions:
                st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                if status == "ACTIVE":
                    if st.button("👁️ Acknowledge", key=f"btn_ack_{a_id}", use_container_width=True):
                        update_alert_status(a_id, "ACKNOWLEDGED")
                        st.rerun()
                elif status == "ACKNOWLEDGED":
                    if st.button("✅ Mark Resolved", key=f"btn_res_{a_id}", use_container_width=True):
                        update_alert_status(a_id, "RESOLVED")
                        st.rerun()
                else:
                    st.markdown("<p style='font-size:0.75rem; color:#00e676; text-align:center; padding-top:8px;'>Incident Closed</p>", unsafe_allow_html=True)
    else:
        st.info("No alert incidents match the selected filtering criteria.")
