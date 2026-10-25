import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re as _re

st.set_page_config(
    page_title="MedSimplify — Medical Report Explainer",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f0f4f8; }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    .hero {
        background: linear-gradient(135deg, #1a365d 0%, #2a69ac 100%);
        padding: 40px;
        border-radius: 16px;
        margin-bottom: 24px;
        text-align: center;
    }
    .hero h1 { font-size: 2.4em; font-weight: 700; margin: 0; letter-spacing: -0.5px; color: white !important; }
    .hero p { font-size: 1.05em; opacity: 0.85; margin-top: 8px; color: white !important; }
    .hero, .hero * { color: white !important; }

    .stTabs [data-baseweb="tab"] { color: #1a202c !important; font-weight: 600 !important; font-size: 1em !important; }
    .stTabs [data-baseweb="tab"] * { color: #1a202c !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #1a365d !important; border-bottom: 3px solid #2a69ac !important; }

    .metric-card { background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.08); color: #1a202c; }
    .metric-card .number { font-size: 2em; font-weight: 700; line-height: 1; color: #1a202c; }
    .metric-card .label { font-size: 0.8em; color: #1a202c; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }

    .finding-card { background: white; border-radius: 12px; padding: 16px 20px; margin: 10px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 5px solid #ccc; }
    .finding-card.abnormal { border-left-color: #e53e3e; }
    .finding-card.normal { border-left-color: #38a169; }
    .finding-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .finding-name { font-weight: 600; font-size: 1em; color: #1a202c; }

    .badge { padding: 3px 10px; border-radius: 20px; font-size: 0.72em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-normal { background: #c6f6d5; color: #276749 !important; }
    .badge-abnormal { background: #fed7d7; color: #9b2c2c !important; }
    .badge-low { background: #fed7d7; color: #9b2c2c !important; }
    .badge-high { background: #feebc8; color: #7b341e !important; }

    .finding-values { display: flex; gap: 20px; font-size: 0.85em; color: #1a202c; margin-bottom: 8px; }
    .finding-explanation { font-size: 0.88em; color: #1a202c; line-height: 1.5; }
    .finding-impact { font-size: 0.82em; color: #4a5568; margin-top: 4px; font-style: italic; }

    .section-header { font-size: 1.1em; font-weight: 600; color: #1a365d; margin: 20px 0 12px 0; padding-bottom: 6px; border-bottom: 2px solid #bee3f8; }
    .specialist-tag { display: inline-block; background: #ebf8ff; color: #2b6cb0 !important; border: 1px solid #90cdf4; padding: 6px 14px; border-radius: 20px; font-size: 0.85em; font-weight: 500; margin: 4px; }
    .disclaimer { background: #fffbeb; border: 1px solid #f6e05e; border-radius: 10px; padding: 12px 16px; font-size: 0.82em; color: #744210 !important; margin-top: 16px; }
    .upload-area { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .summary-box { background: #ebf8ff; border-radius: 10px; padding: 16px; font-size: 0.92em; color: #2c5282 !important; line-height: 1.6; margin-bottom: 16px; }
    .next-steps { background: #f0fff4; border: 1px solid #9ae6b4; border-radius: 10px; padding: 14px 16px; font-size: 0.9em; color: #276749 !important; line-height: 1.6; }

    .compare-header { background: linear-gradient(135deg, #1a365d 0%, #2a69ac 100%); padding: 16px 20px; border-radius: 12px; margin-bottom: 16px; text-align: center; font-weight: 600; font-size: 1.1em; }
    .compare-header, .compare-header * { color: white !important; }

    .better { background: #f0fff4; border: 1px solid #9ae6b4; border-radius: 8px; padding: 6px 12px; color: #276749 !important; font-size: 0.85em; font-weight: 600; }
    .worse { background: #fff5f5; border: 1px solid #fed7d7; border-radius: 8px; padding: 6px 12px; color: #9b2c2c !important; font-size: 0.85em; font-weight: 600; }
    .same { background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; color: #4a5568 !important; font-size: 0.85em; font-weight: 600; }

    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] h1,
    .stTabs [data-baseweb="tab-panel"] h2,
    .stTabs [data-baseweb="tab-panel"] h3,
    .stTabs [data-baseweb="tab-panel"] h4,
    .stTabs [data-baseweb="tab-panel"] label,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] div { color: #1a202c; }

    [data-testid="stFileUploader"] { background-color: white !important; border: 2px dashed #90cdf4 !important; border-radius: 10px !important; padding: 10px !important; }
    [data-testid="stFileUploader"] * { color: #1a202c !important; }
    [data-testid="stFileUploaderDropzone"] { background-color: white !important; }
    [data-testid="stFileUploaderDropzone"] * { color: #1a202c !important; }
    [data-testid="stFileUploaderFile"] { background-color: #ebf8ff !important; border-radius: 6px !important; }
    [data-testid="stFileUploaderFile"] * { color: #1a202c !important; }
    [data-testid="stBaseButton-secondary"] { background-color: white !important; color: #1a202c !important; border: 1px solid #90cdf4 !important; border-radius: 6px !important; }
    [data-testid="stBaseButton-secondary"] * { color: #1a202c !important; }

    .stButton > button { background-color: #2a69ac !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 1em !important; padding: 12px !important; }
    .stButton > button:hover { background-color: #1a365d !important; color: white !important; }
    .stButton > button p { color: white !important; }

    [data-testid="stDownloadButton"] button { background-color: #2a69ac !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 20px !important; width: 100% !important; }
    [data-testid="stDownloadButton"] button * { color: white !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── Helper ───────────────────────────────────────────────────────────────────
def extract_number(value_str):
    try:
        nums = _re.findall(r"[\d.]+", str(value_str))
        return float(nums[0]) if nums else 0
    except:
        return 0

def get_color(status):
    s = status.lower()
    if s == "normal": return "#38a169"
    elif s == "high": return "#e53e3e"
    elif s == "low": return "#3182ce"
    else: return "#dd6b20"

# ─── Session State ─────────────────────────────────────────────────────────────
if "report_history" not in st.session_state:
    st.session_state.report_history = []

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <span style='font-size:2.5em'>🏥</span>
        <div style='font-weight:700; font-size:1.1em; color:#1a365d; margin-top:6px;'>MedSimplify</div>
        <div style='font-size:0.75em; color:#718096;'>Medical Report Explainer</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**How to use**")
    st.markdown("""
    1. Upload your PDF report
    2. Wait ~15 seconds
    3. 🔴 Red = needs attention
    4. 🟢 Green = normal
    5. Compare reports in Compare tab
    """)
    st.divider()
    st.markdown("**Supported Reports**")
    st.markdown("🩸 Blood tests (CBC, LFT, KFT)")
    st.markdown("🧠 MRI / X-Ray reports")
    st.markdown("🏥 Discharge summaries")
    st.markdown("🫀 Thyroid / Lipid panels")
    st.divider()
    if st.session_state.report_history:
        st.markdown("**📋 Saved Reports**")
        for r in st.session_state.report_history:
            st.caption(f"📄 {r['patient_name']} — {r['date']}")
    st.caption("Built with LLaMA + Streamlit")

# ─── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🏥 MedSimplify</h1>
    <p>Upload your medical report and get a clear, plain-language explanation in seconds</p>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋 Analyze Report", "📊 Compare Reports"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALYZE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📂 Upload medical report (PDF)", type=["pdf"])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown('<div class="section-header">📋 Extracted Text</div>', unsafe_allow_html=True)
            with st.spinner("Reading your report..."):
                raw_text = extract_text_from_pdf(uploaded_file)
            if not raw_text:
                st.error("Could not extract text. Try a clearer scan.")
                st.stop()
            st.text_area("", raw_text, height=420, label_visibility="collapsed")

        with col2:
            st.markdown('<div class="section-header">🔍 AI Explanation</div>', unsafe_allow_html=True)
            with st.spinner("Analyzing with AI... ~15 seconds"):
                try:
                    result = analyze_report(raw_text)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.stop()

            findings = result.get("findings", [])
            abnormal = result.get("abnormal_count", 0)
            normal_count = len(findings) - abnormal
            patient_name = result.get("patient_name", "Unknown Patient")

            # Save to history
            report_entry = {
                "patient_name": patient_name,
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "result": result,
                "raw_text": raw_text
            }
            already_saved = any(
                r["patient_name"] == patient_name and r["date"] == report_entry["date"]
                for r in st.session_state.report_history
            )
            if not already_saved:
                st.session_state.report_history.append(report_entry)
            st.info(f"👤 Patient detected: **{patient_name}**")

            # Metric cards
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""<div class="metric-card"><div class="number" style="color:#2b6cb0">{len(findings)}</div><div class="label">Parameters</div></div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card"><div class="number" style="color:#38a169">{normal_count}</div><div class="label">Normal</div></div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card"><div class="number" style="color:#e53e3e">{abnormal}</div><div class="label">Abnormal</div></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if abnormal > 2:
                st.error(f"⚠️ {abnormal} values outside normal range. Please see a doctor soon.")
            elif abnormal > 0:
                st.warning(f"🔔 {abnormal} value(s) need attention. Follow up with your doctor.")
            else:
                st.success("✅ All values appear to be within normal range.")

            st.info(f"📁 **{result.get('report_type', 'Unknown')}**")

            st.markdown('<div class="section-header">📝 Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-box">{result.get("summary", "")}</div>', unsafe_allow_html=True)

        # ── Full width charts ──────────────────────────────────────────────────
        if findings:
            st.markdown('<div class="section-header">📊 Health Overview</div>', unsafe_allow_html=True)

            status_counts = {}
            for f in findings:
                s = f.get("status", "normal").capitalize()
                status_counts[s] = status_counts.get(s, 0) + 1

            colors_map = {"Normal": "#38a169", "High": "#e53e3e", "Low": "#3182ce", "Abnormal": "#dd6b20"}

            # Donut chart centered
            dcol1, dcol2, dcol3 = st.columns([1, 2, 1])
            with dcol2:
                fig_donut = go.Figure(data=[go.Pie(
                    labels=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    hole=0.55,
                    marker_colors=[colors_map.get(k, "#718096") for k in status_counts.keys()],
                    textinfo="label+value",
                    textposition="outside",
                    textfont=dict(size=13, color="black"),
                    hovertemplate="<b>%{label}</b><br>%{value} parameters (%{percent})<extra></extra>"
                )])
                fig_donut.update_layout(
                    title=dict(text="Overall Health Summary", font_size=15, x=0.5, font_color="black"),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color="black", size=12)),
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter", color="black"),
                    height=380,
                    margin=dict(t=50, b=60, l=20, r=20),
                    annotations=[dict(text=f"<b>{len(findings)}</b><br>Parameters", x=0.5, y=0.5, font=dict(size=18, color="black"), showarrow=False)]
                )
                st.plotly_chart(fig_donut, use_container_width=True, key="donut_main")

            # Full width bar chart
            param_names = [f.get("parameter", "") for f in findings]
            param_status = [f.get("status", "normal").lower() for f in findings]
            param_values = [f.get("value", "") for f in findings]
            param_numbers = [extract_number(v) for v in param_values]
            param_colors_list = [get_color(s) for s in param_status]
            bar_height = max(400, len(param_names) * 60)

            fig_params = go.Figure()
            fig_params.add_trace(go.Bar(
                name="Parameters",
                y=param_names,
                x=param_numbers,
                orientation="h",
                marker_color=param_colors_list,
                marker_line_width=0,
                text=[f"{s.upper()} | {v}" for s, v in zip(param_status, param_values)],
                textposition="outside",
                textfont=dict(color="black", size=11),
                hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"
            ))
            fig_params.update_layout(
                title=dict(text="Each Parameter at a Glance", font_size=15, x=0.5, font_color="black"),
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter", color="black"),
                height=bar_height,
                margin=dict(t=50, b=20, l=180, r=150),
                xaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=False, color="black", title="Value", tickfont=dict(color="black")),
                yaxis=dict(showgrid=False, color="black", tickfont=dict(color="black", size=12), autorange="reversed"),
                showlegend=False,
                bargap=0.25
            )
            st.plotly_chart(fig_params, use_container_width=True, key="params_main")

        # ── Parameter breakdown ────────────────────────────────────────────────
        st.markdown('<div class="section-header">🔬 Parameter Breakdown</div>', unsafe_allow_html=True)
        for f in findings:
            status = f.get("status", "normal").lower()
            card_class = "abnormal" if status in ["low", "high", "abnormal"] else "normal"
            icon = "🔴" if card_class == "abnormal" else "🟢"
            st.markdown(f"""
            <div class="finding-card {card_class}">
                <div class="finding-header">
                    <div class="finding-name">{icon} {f.get('parameter', '')}</div>
                    <span class="badge badge-{status}">{f.get('status', '').upper()}</span>
                </div>
                <div class="finding-values">
                    <span>📌 Value: <strong>{f.get('value', '')}</strong></span>
                    <span>📏 Normal: <strong>{f.get('normal_range', 'N/A')}</strong></span>
                </div>
                <div class="finding-explanation">💬 {f.get('plain_explanation', '')}</div>
                <div class="finding-impact">🏃 {f.get('impact', '')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">👨‍⚕️ Who to Consult</div>', unsafe_allow_html=True)
        specialists_html = "".join([f'<span class="specialist-tag">🩺 {s}</span>' for s in result.get("recommended_specialists", [])])
        st.markdown(specialists_html, unsafe_allow_html=True)

        st.markdown('<div class="section-header">✅ Next Steps</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="next-steps">📋 {result.get("next_steps", "")}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        report_output = f"""
MedSimplify Report
==================
Patient: {patient_name}
Date: {report_entry['date']}
Type: {result.get('report_type')}
Summary: {result.get('summary')}

Findings:
{chr(10).join([f"- {f['parameter']}: {f['value']} ({f['status'].upper()})" for f in findings])}

Specialists: {', '.join(result.get('recommended_specialists', []))}
Next Steps: {result.get('next_steps')}

DISCLAIMER: Educational only. Consult a doctor.
"""
        st.download_button("⬇️ Download Summary", report_output, f"{patient_name}_report.txt")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:


    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Compare Two Reports</div>', unsafe_allow_html=True)
    st.markdown("Upload two reports below to compare them side by side.")
    st.markdown("<br>", unsafe_allow_html=True)

    st.info("👤 Patient name will be automatically detected from the uploaded reports.")

    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("#### 📄 Report 1 (Older)")
        compare_file1 = st.file_uploader("Upload Report 1", type=["pdf"], key="compare_file1")
    with cc2:
        st.markdown("#### 📄 Report 2 (Newer)")
        compare_file2 = st.file_uploader("Upload Report 2", type=["pdf"], key="compare_file2")

    if st.button("🔍 Compare Reports", use_container_width=True):
        if not compare_file1:
            st.warning("⚠️ Please upload Report 1.")
        elif not compare_file2:
            st.warning("⚠️ Please upload Report 2.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<p style='color:#1a202c; font-weight:600; font-size:1.1em;'>📋 Extracting Report 1...</p>", unsafe_allow_html=True)
                with st.spinner("Reading Report 1..."):
                    raw1 = extract_text_from_pdf(compare_file1)
                if not raw1:
                    st.error("Could not extract text from Report 1.")
                    st.stop()
                st.markdown("<p style='color:#276749; font-weight:600;'>✅ Report 1 extracted successfully</p>", unsafe_allow_html=True)
            with col2:
                st.markdown("<p style='color:#1a202c; font-weight:600; font-size:1.1em;'>📋 Extracting Report 2...</p>", unsafe_allow_html=True)
                with st.spinner("Reading Report 2..."):
                    raw2 = extract_text_from_pdf(compare_file2)
                if not raw2:
                    st.error("Could not extract text from Report 2.")
                    st.stop()
                st.markdown("<p style='color:#276749; font-weight:600;'>✅ Report 2 extracted successfully</p>", unsafe_allow_html=True)

            with st.spinner("Analyzing both reports... ~30 seconds"):
                try:
                    result1 = analyze_report(raw1)
                    result2 = analyze_report(raw2)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.stop()

            compare_patient = result1.get("patient_name") or result2.get("patient_name") or "Unknown Patient"

            st.markdown("---")
            st.markdown(f"""
            <div class="compare-header">
                Comparing reports for: <strong>{compare_patient}</strong> | Report 1 vs Report 2
            </div>
            """, unsafe_allow_html=True)

            findings1 = {f["parameter"]: f for f in result1.get("findings", [])}
            findings2 = {f["parameter"]: f for f in result2.get("findings", [])}
            common_params = [p for p in findings1 if p in findings2]
            ab1 = result1.get("abnormal_count", 0)
            ab2 = result2.get("abnormal_count", 0)
            total1 = len(findings1)
            total2 = len(findings2)

            # Metric cards
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""<div class="metric-card"><div class="number" style="color:#2b6cb0">{total1}</div><div class="label">Report 1 Params</div></div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card"><div class="number" style="color:#2b6cb0">{total2}</div><div class="label">Report 2 Params</div></div>""", unsafe_allow_html=True)
            with m3:
                color = "#e53e3e" if ab1 > 0 else "#38a169"
                st.markdown(f"""<div class="metric-card"><div class="number" style="color:{color}">{ab1}</div><div class="label">Report 1 Abnormal</div></div>""", unsafe_allow_html=True)
            with m4:
                color = "#e53e3e" if ab2 > 0 else "#38a169"
                st.markdown(f"""<div class="metric-card"><div class="number" style="color:{color}">{ab2}</div><div class="label">Report 2 Abnormal</div></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Charts row 1
            ch1, ch2 = st.columns(2)
            with ch1:
                bar_colors = ["#e53e3e" if ab1 > 0 else "#38a169", "#38a169" if ab2 <= ab1 else "#e53e3e"]
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Bar(
                    x=["Report 1 (Older)", "Report 2 (Newer)"],
                    y=[ab1, ab2],
                    marker_color=bar_colors,
                    marker_line_width=0,
                    text=[f"{ab1} Abnormal", f"{ab2} Abnormal"],
                    textposition="outside",
                    textfont=dict(color="black", size=12)
                ))
                arrow = "📉 Improved!" if ab2 < ab1 else ("📈 Worsened" if ab2 > ab1 else "➡️ No Change")
                fig_trend.update_layout(
                    title=dict(text=f"Abnormal Count  {arrow}", font_size=14, x=0.5, font_color="black"),
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter", color="black"),
                    height=320,
                    margin=dict(t=50, b=20, l=20, r=20),
                    yaxis=dict(showgrid=True, gridcolor="#f0f0f0", color="black", title="No. of Abnormal Values"),
                    xaxis=dict(color="black")
                )
                st.plotly_chart(fig_trend, use_container_width=True, key="trend_compare")

            with ch2:
                score1 = round(((total1 - ab1) / total1) * 100) if total1 > 0 else 0
                score2 = round(((total2 - ab2) / total2) * 100) if total2 > 0 else 0
                fig_score = go.Figure()
                fig_score.add_trace(go.Bar(
                    x=["Report 1 (Older)", "Report 2 (Newer)"],
                    y=[score1, score2],
                    marker_color=["#3182ce", "#38a169" if score2 >= score1 else "#e53e3e"],
                    marker_line_width=0,
                    text=[f"{score1}%", f"{score2}%"],
                    textposition="outside",
                    textfont=dict(color="black", size=12)
                ))
                fig_score.update_layout(
                    title=dict(text="Health Score (% Normal)", font_size=14, x=0.5, font_color="black"),
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter", color="black"),
                    height=320,
                    margin=dict(t=50, b=20, l=20, r=20),
                    yaxis=dict(showgrid=True, gridcolor="#f0f0f0", color="black", range=[0, 110], title="% of Normal Parameters"),
                    xaxis=dict(color="black")
                )
                st.plotly_chart(fig_score, use_container_width=True, key="score_compare")


            # Parameter comparison chart
            if common_params:
                color_map_r1 = [get_color(findings1[p].get("status", "normal")) for p in common_params]
                color_map_r2 = [get_color(findings2[p].get("status", "normal")) for p in common_params]
                r1_values = [extract_number(findings1[p].get("value", "0")) for p in common_params]
                r2_values = [extract_number(findings2[p].get("value", "0")) for p in common_params]

                fig_compare = go.Figure()
                fig_compare.add_trace(go.Bar(
                    name="Report 1 (Older)",
                    y=common_params,
                    x=r1_values,
                    orientation="h",
                    marker_color=color_map_r1,
                    marker_line_width=0,
                    text=[findings1[p].get("status", "").upper() + " | " + findings1[p].get("value", "") for p in common_params],
                    textposition="outside",
                    textfont=dict(color="black", size=11),
                    hovertemplate="<b>%{y}</b><br>Report 1: %{text}<extra></extra>"
                ))
                fig_compare.add_trace(go.Bar(
                    name="Report 2 (Newer)",
                    y=common_params,
                    x=r2_values,
                    orientation="h",
                    marker_color=color_map_r2,
                    marker_line_width=0,
                    text=[findings2[p].get("status", "").upper() + " | " + findings2[p].get("value", "") for p in common_params],
                    textposition="outside",
                    textfont=dict(color="black", size=11),
                    hovertemplate="<b>%{y}</b><br>Report 2: %{text}<extra></extra>"
                ))
                bar_h = max(400, len(common_params) * 60)
                fig_compare.update_layout(
                    title=dict(text="Parameter Comparison: Report 1 vs Report 2", font_size=15, x=0.5, font_color="black"),
                    barmode="group",
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter", color="black"),
                    height=bar_h,
                    margin=dict(t=50, b=20, l=180, r=150),
                    xaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=False, color="black", title="Value", tickfont=dict(color="black")),
                    yaxis=dict(showgrid=False, color="black", tickfont=dict(color="black", size=12), autorange="reversed"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="black", size=12)),
                    bargap=0.25, bargroupgap=0.15
                )
                st.plotly_chart(fig_compare, use_container_width=True, key="compare_main")

                # Parameter cards
                st.markdown('<div class="section-header">🔬 Parameter by Parameter</div>', unsafe_allow_html=True)
                h1, h2, h3 = st.columns([2, 2, 1])
                with h1: st.markdown("**📄 Report 1 (Older)**")
                with h2: st.markdown("**📄 Report 2 (Newer)**")
                with h3: st.markdown("**Change**")

                for param in common_params:
                    f1 = findings1[param]
                    f2 = findings2[param]
                    s1 = f1.get("status", "normal").lower()
                    s2 = f2.get("status", "normal").lower()

                    if s1 in ["low", "high", "abnormal"] and s2 == "normal":
                        change, change_class = "✅ Improved", "better"
                    elif s1 == "normal" and s2 in ["low", "high", "abnormal"]:
                        change, change_class = "⚠️ Worsened", "worse"
                    elif s1 == s2:
                        change, change_class = "➡️ No Change", "same"
                    else:
                        change, change_class = "🔄 Changed", "same"

                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        icon1 = "🔴" if s1 in ["low", "high", "abnormal"] else "🟢"
                        st.markdown(f"""
                        <div class="finding-card {'abnormal' if s1 in ['low','high','abnormal'] else 'normal'}">
                            <div class="finding-name">{icon1} {param}</div>
                            <div class="finding-values"><span>Value: <strong>{f1.get('value', '')}</strong></span></div>
                            <span class="badge badge-{s1}">{s1.upper()}</span>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        icon2 = "🔴" if s2 in ["low", "high", "abnormal"] else "🟢"
                        st.markdown(f"""
                        <div class="finding-card {'abnormal' if s2 in ['low','high','abnormal'] else 'normal'}">
                            <div class="finding-name">{icon2} {param}</div>
                            <div class="finding-values"><span>Value: <strong>{f2.get('value', '')}</strong></span></div>
                            <span class="badge badge-{s2}">{s2.upper()}</span>
                        </div>""", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"""
                        <div style="height:100%; display:flex; align-items:center; justify-content:center; padding-top:20px;">
                            <span class="{change_class}">{change}</span>
                        </div>""", unsafe_allow_html=True)
            # Summaries
            st.markdown('<div class="section-header">📝 Summaries</div>', unsafe_allow_html=True)
            s1, s2 = st.columns(2)
            with s1:
                st.markdown("**Report 1**")
                st.markdown(f'<div class="summary-box">{result1.get("summary", "")}</div>', unsafe_allow_html=True)
            with s2:
                st.markdown("**Report 2**")
                st.markdown(f'<div class="summary-box">{result2.get("summary", "")}</div>', unsafe_allow_html=True)

            # Download
            st.markdown("<br>", unsafe_allow_html=True)
            comparison_output = f"""

MedSimplify Comparison Report
==============================
Patient: {compare_patient}

REPORT 1 SUMMARY:
{result1.get('summary', '')}
Abnormal Count: {ab1}

REPORT 2 SUMMARY:
{result2.get('summary', '')}
Abnormal Count: {ab2}

PARAMETER CHANGES:
{chr(10).join([f"- {p}: {findings1[p]['status'].upper()} → {findings2[p]['status'].upper()}" for p in common_params])}

DISCLAIMER: Educational only. Consult a doctor.
"""
            st.download_button("⬇️ Download Comparison Report", comparison_output, f"{compare_patient}_comparison.txt")
