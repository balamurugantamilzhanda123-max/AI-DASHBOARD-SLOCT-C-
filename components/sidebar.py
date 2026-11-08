"""
Sidebar Navigation Component
Provides collapsible sidebar navigation across all 10 dedicated system pages.
"""

import streamlit as st
from core.fault_injector import fault_injector


def render_sidebar():
    """Renders the sidebar navigation and returns selected page name."""
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><h2>NOC SIGNAL AI</h2><span>TELECOM ENGINE v2.4</span></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sim-watermark"><span>🧪 DATA SOURCE:</span> <b>SIMULATION</b></div>',
            unsafe_allow_html=True
        )

        pages = [
            "📊 Dashboard Overview",
            "⚡ Live Signal Monitoring",
            "📶 Channel Analysis",
            "🚨 Fault Detection Centre",
            "🧠 AI Prediction Centre",
            "📈 Signal Analytics",
            "🔔 Alert Centre",
            "📜 Historical Data",
            "📑 Reports",
            "⚙️ Settings"
        ]

        if "current_page" not in st.session_state:
            st.session_state.current_page = pages[0]

        selected_page = st.radio(
            "SYSTEM NAVIGATION",
            pages,
            index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
            key="nav_selection"
        )
        st.session_state.current_page = selected_page

        st.markdown("---")

        st.markdown("<p style='font-size:0.75rem; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;'>Channel Matrix Status</p>", unsafe_allow_html=True)
        active_faults = fault_injector.get_all_active_faults()
        
        for ch in ["CH1", "CH2", "CH3"]:
            fault = active_faults[ch]
            f_type = fault["type"]
            if f_type == "NORMAL":
                dot = '<span class="pulse-dot pulse-green"></span>'
                badge_style = 'color: #00e676;'
            elif f_type in ["BIT_CORRUPTION", "TRANSMISSION_DELAY"]:
                dot = '<span class="pulse-dot pulse-amber"></span>'
                badge_style = 'color: #ffb300;'
            else:
                dot = '<span class="pulse-dot pulse-red"></span>'
                badge_style = 'color: #ff1744;'

            st.markdown(
                f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 8px; background: rgba(17,30,56,0.5); border-radius: 6px; margin-bottom: 6px; font-size: 0.75rem; font-family: monospace;"><span>{dot} <b>{ch}</b></span><span style="{badge_style}">{f_type}</span></div>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown(
            '<div style="font-size: 0.68rem; color: #64748b; text-align: center; line-height: 1.4;">AI-Assisted Signal Monitor & Fault Detection<br>Engineering Capstone Project © 2026<br><i>Ready for Arduino Hardware</i></div>',
            unsafe_allow_html=True
        )

        return selected_page
