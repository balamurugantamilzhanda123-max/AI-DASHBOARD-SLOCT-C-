"""
Top Navigation Bar Component
Displays Project Name, Operational Status, Data Source Indicator, Timestamp,
Notification Alert count, and User Profile badge using st.html().
"""

import streamlit as st
from datetime import datetime
from core.database import get_alerts


def render_top_navbar(data_source_mode: str = "SIMULATION"):
    """Renders the futuristic top navigation bar using st.html for native HTML rendering."""
    now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    # Get active alert count
    active_alerts = get_alerts(status="ACTIVE")
    active_count = len(active_alerts)
    crit_count = sum(1 for a in active_alerts if a["severity"] == "CRITICAL")

    # Source chip styling
    if data_source_mode == "HARDWARE":
        source_label = "HARDWARE [STANDBY / COM3]"
        source_chip = "chip-hardware"
        pulse_color = "pulse-amber"
    else:
        source_label = "SIMULATION DATA [ACTIVE]"
        source_chip = "chip-simulated"
        pulse_color = "pulse-cyan"

    crit_badge = f'<span style="margin-left:6px; background:#ff1744; color:white; border-radius:10px; padding:1px 6px; font-size:0.65rem;">{crit_count} CRITICAL</span>' if crit_count > 0 else ''
    alert_badge_html = f'<div style="position: relative; display: inline-flex; align-items: center; padding: 4px 10px; background: rgba(255,23,68,0.15); border: 1px solid rgba(255,23,68,0.4); border-radius: 20px; font-size: 0.75rem; color: #ff1744; font-family: monospace;">🔔 ALERTS: <b style="margin-left: 4px;">{active_count}</b>{crit_badge}</div>'

    navbar_html = f'''<div class="top-nav-bar"><div class="brand-section"><div class="brand-logo-icon">📡</div><div class="brand-text"><h1 style="font-size:1.05rem; font-weight:700; margin:0; color:#ffffff; letter-spacing:0.5px; text-transform:uppercase;">AI Digital Communication Signal Monitor</h1><p style="font-size:0.72rem; color:#38bdf8; margin:0; letter-spacing:1px;">REAL-TIME FAULT DETECTION & TELEMETRY PLATFORM</p></div></div><div class="nav-badges"><div class="status-chip chip-operational"><span class="pulse-dot pulse-green"></span><span>SYSTEM ONLINE</span></div><div class="status-chip {source_chip}"><span class="pulse-dot {pulse_color}"></span><span>{source_label}</span></div>{alert_badge_html}<div class="user-pill"><span>⏱️ {now_str}</span></div><div class="user-pill"><span>👤 Lead Systems Engineer</span></div></div></div>'''
    st.html(navbar_html)
