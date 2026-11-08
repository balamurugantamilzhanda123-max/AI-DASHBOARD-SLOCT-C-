"""
==============================================================================
AI-Assisted Real-Time Digital Communication Signal Monitoring and Fault Detection System
Main Application Entrypoint & Modular Routing Harness
==============================================================================
Tech Stack: Python, Streamlit, Plotly, Scikit-learn, Pandas, NumPy, SQLite
Designed for Final-Year Engineering Project
Ready for Future Arduino Nano Serial Hardware Integration
"""

import streamlit as st
import os

# ------------------------------------------------------------------------------
# Vercel Serverless Function Entrypoint Compatibility
# Guarantees Vercel CLI discovers top-level "app", "application", and "handler"
# ------------------------------------------------------------------------------
try:
    from api.index import handler as _VercelHandler
    handler = _VercelHandler
    app = _VercelHandler
    application = _VercelHandler
except Exception:
    from http.server import BaseHTTPRequestHandler
    class _FallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"AI Digital Communication Signal Monitor & Fault Detection System")
    handler = _FallbackHandler
    app = _FallbackHandler
    application = _FallbackHandler

# ------------------------------------------------------------------------------
# Streamlit Interactive Dashboard Runtime Execution
# Executes only when running under Streamlit engine (local or Streamlit Cloud)
# ------------------------------------------------------------------------------
if st.runtime.exists():
    # 1. Streamlit Wide Layout & Branding Config
    st.set_page_config(
        page_title="AI Digital Communication Signal Monitor & Fault Detection",
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject Futuristic Dark Theme Custom CSS
    CSS_PATH = os.path.join(os.path.dirname(__file__), "styles", "theme.css")
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            st.html(f"<style>{f.read()}</style>")

    # 3. Initialize Core Database
    from core.database import init_database, get_setting
    init_database()

    # 4. Initialize Data Source Architecture
    from core.data_source import get_data_source, SimulationDataSource

    if "data_source_mode" not in st.session_state:
        st.session_state.data_source_mode = get_setting("data_source", "SIMULATION")

    if "data_source" not in st.session_state or st.session_state.data_source is None:
        st.session_state.data_source = get_data_source(st.session_state.data_source_mode)

    # Re-instantiate data source if mode changed in settings
    if st.session_state.data_source.get_source_type().startswith("HARDWARE") and st.session_state.data_source_mode == "SIMULATION":
        st.session_state.data_source = get_data_source("SIMULATION")
    elif "SIMULATION" in st.session_state.data_source.get_source_type() and st.session_state.data_source_mode == "HARDWARE":
        st.session_state.data_source = get_data_source("HARDWARE")

    # 5. Render Navigation Components
    from components.top_navbar import render_top_navbar
    from components.sidebar import render_sidebar

    render_top_navbar(data_source_mode=st.session_state.data_source_mode)
    selected_page = render_sidebar()

    # 6. Modular Page Routing Harness
    from pages_custom import (
        p1_overview,
        p2_live_signal,
        p3_channel_analysis,
        p4_fault_detection,
        p5_ai_prediction,
        p6_signal_analytics,
        p7_alert_centre,
        p8_historical_data,
        p9_reports,
        p10_settings
    )

    try:
        if "Dashboard Overview" in selected_page:
            p1_overview.render_page(st.session_state.data_source)
        elif "Live Signal Monitoring" in selected_page:
            p2_live_signal.render_page(st.session_state.data_source)
        elif "Channel Analysis" in selected_page:
            p3_channel_analysis.render_page(st.session_state.data_source)
        elif "Fault Detection Centre" in selected_page:
            p4_fault_detection.render_page(st.session_state.data_source)
        elif "AI Prediction Centre" in selected_page:
            p5_ai_prediction.render_page(st.session_state.data_source)
        elif "Signal Analytics" in selected_page:
            p6_signal_analytics.render_page(st.session_state.data_source)
        elif "Alert Centre" in selected_page:
            p7_alert_centre.render_page(st.session_state.data_source)
        elif "Historical Data" in selected_page:
            p8_historical_data.render_page(st.session_state.data_source)
        elif "Reports" in selected_page:
            p9_reports.render_page(st.session_state.data_source)
        elif "Settings" in selected_page:
            p10_settings.render_page(st.session_state.data_source)
        else:
            p1_overview.render_page(st.session_state.data_source)
    except Exception as e:
        st.error(f"Routing Exception encountered on {selected_page}: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
