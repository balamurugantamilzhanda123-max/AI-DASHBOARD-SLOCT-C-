"""
Page 5: AI Prediction Centre
Dedicated AI analytics suite powered by scikit-learn Random Forest Classifier and
Isolation Forest Anomaly Detector. Features genuine test set evaluation metrics,
confusion matrix heatmap, feature importance analysis, and live real-time inference.
Clearly labelled: SIMULATED PREDICTIONS & BENCHMARK TRAINED.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from core.ai_engine import ai_engine
from utils.formatters import get_severity_badge_html


def render_page(data_source):
    st.markdown(
        '<div class="section-header"><div><h2>🧠 AI Fault Prediction & Machine Learning Analytics</h2><div class="subtitle">Ensemble Random Forest Classification & Unsupervised Isolation Forest Anomaly Detection</div></div><div class="sim-watermark">TRAINED ON SIMULATED COMMUNICATIONS DATASET</div></div>',
        unsafe_allow_html=True
    )

    # 1. Model Retrain and Benchmark Control Bar
    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.markdown(
            '<div style="font-size:0.8rem; color:#94a3b8; line-height:1.5;"><b>Active Architecture:</b> Dual-Model Pipeline: <b>Random Forest (100 Trees)</b> for supervised fault classification + <b>Isolation Forest</b> for unsupervised out-of-distribution anomaly scoring.</div>',
            unsafe_allow_html=True
        )

    with top_c2:
        if st.button("🔄 Retrain AI Benchmark", key="btn_retrain_ai", use_container_width=True):
            with st.spinner("Training Random Forest & Isolation Forest on synthetic communications corpus..."):
                ai_engine.train_and_evaluate()
            st.success("AI Models retrained and evaluated on fresh holdout partition!")
            st.rerun()

    # Fetch latest evaluation results
    eval_res = ai_engine.evaluation_results

    # 2. Real-Time Inference Card (Testing on Live Channel)
    st.markdown("<h4 style='color:#00f2fe; margin:10px 0;'>REAL-TIME CHANNEL INFERENCE</h4>", unsafe_allow_html=True)

    col_target_ch, col_run = st.columns([2, 5])
    with col_target_ch:
        pred_ch = st.selectbox("Inspect Channel Inference", ["CH1", "CH2", "CH3"], key="ai_pred_channel")

    ch_telemetry = data_source.read_channel_telemetry(pred_ch)
    waveform_data = data_source.get_waveform_data(channel=pred_ch, num_bits=16)
    wf_metrics = waveform_data["metrics"]

    # Run AI inference
    prediction = ai_engine.predict_realtime(ch_telemetry, wf_metrics)

    pred_cat = prediction["predicted_fault"]
    confidence = prediction["confidence"]
    probabilities = prediction["probabilities"]
    anomaly_score = prediction["anomaly_score"]
    is_anomaly = prediction["is_anomaly"]
    pred_sev = prediction["severity"]

    # Display Live Inference Card
    c_pred1, c_pred2, c_pred3 = st.columns([1.2, 1.8, 1.5])

    with c_pred1:
        st.markdown(
            f'''<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid {'#00e676' if pred_cat == 'NORMAL' else '#ff1744'}; border-radius:12px; padding:14px 16px;"><div style="color:#64748b; font-size:0.7rem; font-family:monospace;">PREDICTED FAULT CATEGORY</div><div style="font-size:1.35rem; font-weight:700; color:{'#00e676' if pred_cat == 'NORMAL' else '#ff1744'}; margin:6px 0;">{pred_cat}</div><div style="margin-bottom:8px;">{get_severity_badge_html(pred_sev)}</div><div style="font-size:0.75rem; color:#94a3b8;">Confidence: <b style="color:#00f2fe;">{confidence * 100:.1f}%</b></div></div>''',
            unsafe_allow_html=True
        )

    with c_pred2:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:10px 14px 2px 14px; margin-bottom:4px;"><div style="color:#64748b; font-size:0.7rem; font-family:monospace;">MODEL CLASS PROBABILITY DISTRIBUTION</div></div>',
            unsafe_allow_html=True
        )

        prob_df = pd.DataFrame(list(probabilities.items()), columns=["Class", "Probability"])
        fig_prob = go.Figure(go.Bar(
            x=prob_df["Probability"],
            y=prob_df["Class"],
            orientation="h",
            marker=dict(
                color=["#00e676" if c == "NORMAL" else "#ff1744" for c in prob_df["Class"]],
                line=dict(color="#1e3a8a", width=1)
            )
        ))
        fig_prob.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 25, 48, 0.4)",
            font=dict(color="#cbd5e1", size=10, family="Outfit"),
            height=130,
            margin=dict(l=10, r=20, t=5, b=10),
            xaxis=dict(range=[0, 1.0], showgrid=True, gridcolor="rgba(30,58,138,0.2)"),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_prob, use_container_width=True)

    with c_pred3:
        anom_color = "#ff1744" if is_anomaly else "#00e676"
        st.markdown(
            f'''<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid {anom_color}; border-radius:12px; padding:14px 16px;"><div style="color:#64748b; font-size:0.7rem; font-family:monospace;">ISOLATION FOREST ANOMALY STATUS</div><div style="font-size:1.15rem; font-weight:700; color:{anom_color}; margin:6px 0;">{'⚠️ ANOMALY DETECTED' if is_anomaly else '✅ IN-DISTRIBUTION (NOMINAL)'}</div><div style="font-size:0.75rem; color:#cbd5e1; line-height:1.6;"><div>Score: <b style="color:#ffffff;">{anomaly_score:.4f}</b></div><div style="font-size:0.68rem; color:#64748b;">(Negative value indicates outlier)</div><div>Status: <b style="color:#00f2fe;">ACTIVE INFERENCE</b></div></div></div>''',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Model Evaluation Results Ribbon (Genuine Scikit-Learn Metrics)
    st.markdown("<h4 style='color:#00f2fe;'>HOLDOUT VALIDATION PERFORMANCE METRICS</h4>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Accuracy Score</span><span>🎯</span></div><div class="kpi-value kpi-value-green">{eval_res.get("accuracy", 0.0) * 100:.2f}%</div><div class="kpi-subtitle"><span>Holdout Test Split (25%)</span></div></div>''',
            unsafe_allow_html=True
        )

    with m_col2:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Weighted Precision</span><span>⚖️</span></div><div class="kpi-value kpi-value-cyan">{eval_res.get("precision", 0.0) * 100:.2f}%</div><div class="kpi-subtitle"><span>Multi-class Harmonic</span></div></div>''',
            unsafe_allow_html=True
        )

    with m_col3:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>Weighted Recall</span><span>🔍</span></div><div class="kpi-value kpi-value-cyan">{eval_res.get("recall", 0.0) * 100:.2f}%</div><div class="kpi-subtitle"><span>Sensitivity Across Classes</span></div></div>''',
            unsafe_allow_html=True
        )

    with m_col4:
        st.markdown(
            f'''<div class="kpi-card"><div class="kpi-title"><span>F1-Score</span><span>⚡</span></div><div class="kpi-value kpi-value-green">{eval_res.get("f1_score", 0.0) * 100:.2f}%</div><div class="kpi-subtitle"><span>Precision-Recall Balance</span></div></div>''',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 4. Confusion Matrix and Feature Importances
    eval_c1, eval_c2 = st.columns([1, 1])

    with eval_c1:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #00f2fe; border-radius:12px; padding:10px 14px 2px 14px; margin-bottom:8px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">MODEL CONFUSION MATRIX (HOLDOUT TEST SET)</h4></div>',
            unsafe_allow_html=True
        )

        cm = eval_res.get("confusion_matrix", [])
        classes = eval_res.get("classes", [])

        if cm:
            fig_cm = px.imshow(
                cm,
                x=classes,
                y=classes,
                labels=dict(x="Predicted Class", y="Actual Class", color="Count"),
                color_continuous_scale="Blues",
                text_auto=True
            )
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 25, 48, 0.4)",
                font=dict(color="#cbd5e1", family="Outfit", size=10),
                height=300,
                margin=dict(l=40, r=20, t=10, b=30),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_cm, use_container_width=True)

    with eval_c2:
        st.markdown(
            '<div style="background:rgba(15,25,48,0.75); border:1px solid rgba(30,58,138,0.35); border-left:4px solid #0066ff; border-radius:12px; padding:10px 14px 2px 14px; margin-bottom:8px;"><h4 style="margin:0; color:#00f2fe; font-size:1.0rem;">RANDOM FOREST FEATURE IMPORTANCES (GINI)</h4></div>',
            unsafe_allow_html=True
        )

        feat_imp = eval_res.get("feature_importances", {})
        if feat_imp:
            feat_df = pd.DataFrame(list(feat_imp.items()), columns=["Feature", "Importance"])
            feat_df = feat_df.sort_values("Importance", ascending=True)

            fig_feat = go.Figure(go.Bar(
                x=feat_df["Importance"],
                y=feat_df["Feature"],
                orientation="h",
                marker=dict(color="#00f2fe", line=dict(color="#1e3a8a", width=1))
            ))
            fig_feat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 25, 48, 0.4)",
                font=dict(color="#cbd5e1", family="Outfit", size=11),
                height=300,
                margin=dict(l=40, r=20, t=10, b=30),
                xaxis=dict(showgrid=True, gridcolor="rgba(30,58,138,0.2)", title="Relative Importance")
            )
            st.plotly_chart(fig_feat, use_container_width=True)
