"""
Personality Intelligence Dashboard
===================================
Main entry point. Configures page layout, applies dark theme,
auto-generates data if missing, and renders the landing page.
"""

import streamlit as st
import pandas as pd
import os

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="Personality Intelligence Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auto-generate data if missing ──────────────────────────────────────────────
DATA_PATH = "data/employees.csv"

if not os.path.exists(DATA_PATH):
    os.makedirs("data", exist_ok=True)
    st.info("⚙️ First run detected — generating synthetic dataset...")
    import generate_data  # noqa: F401
    st.success("✅ Dataset generated. Reloading...")
    st.rerun()

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #0d0f14;
    color: #e8eaf0;
}
[data-testid="stSidebar"] {
    background-color: #13151c;
    border-right: 1px solid #1f2330;
}
[data-testid="stMetric"] {
    background: #1a1d27;
    border: 1px solid #252840;
    border-radius: 12px;
    padding: 16px;
}
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    letter-spacing: -0.02em;
}
hr { border-color: #1f2330; margin: 1.5rem 0; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2a2d3e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Personality Intel")
    st.markdown("---")
    st.markdown("### Navigation")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/01_org_overview.py", label="📊 Org Overview")
    st.page_link("pages/02_department_deep_dive.py", label="🔍 Department Deep Dive")
    st.page_link("pages/03_employee_profiles.py", label="👤 Employee Profiles")
    st.page_link("pages/04_cross_functional.py", label="🔗 Cross-Functional Map")
    st.page_link("pages/05_task_alignment.py", label="🎯 Task Alignment")
    st.markdown("---")
    df_all = pd.read_csv(DATA_PATH)
    all_depts = ["All Departments"] + sorted(df_all["Department"].unique().tolist())
    selected_dept = st.selectbox("🏢 Filter Department", all_depts, key="global_dept_filter")
    st.session_state["selected_dept"] = selected_dept
    st.markdown("---")
    st.caption("Synthetic data — for demonstration only.")

# ── Landing page ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 2rem 0 1rem 0'>
    <h1 style='font-size:2.6rem; margin-bottom:0.3rem'>
        🧠 Personality Intelligence Dashboard
    </h1>
    <p style='color:#8892b0; font-size:1.1rem; margin-top:0'>
        Understand team structures, communication patterns, and cross-functional fit.
    </p>
</div>
""", unsafe_allow_html=True)

df = pd.read_csv(DATA_PATH)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("👥 Total Employees", len(df))
with col2:
    st.metric("🏢 Departments", df["Department"].nunique())
with col3:
    st.metric("🧬 Archetypes", df["Personality_Archetype"].nunique())
with col4:
    st.metric("🤝 Avg Collaboration Score", round(df["Collaboration_Score"].mean(), 1))
with col5:
    high_stress = round((df["Stress_Risk_Level"] == "High").mean() * 100, 1)
    st.metric("⚠️ High Stress Risk", f"{high_stress}%")

st.markdown("---")
st.markdown("### 📌 How to use this dashboard")
cols = st.columns(3)
guides = [
    ("📊 Start with Org Overview", "Get a bird's eye view of personality archetypes, OCEAN distributions, and communication patterns across the whole organisation."),
    ("🔍 Drill into Departments", "Use Department Deep Dive to understand the personality mix, friction points, and operating norms specific to each team."),
    ("🎯 Find the Right People", "Use Task Alignment and Employee Profiles to identify who is best suited to cross-functional projects and leadership roles."),
]
for col, (title, desc) in zip(cols, guides):
    with col:
        st.markdown(f"**{title}**")
        st.markdown(f"<p style='color:#8892b0;font-size:0.9rem'>{desc}</p>", unsafe_allow_html=True)

st.markdown("---")
st.caption("All data is synthetic and generated for demonstration purposes. Not intended for actual HR decisions.")
