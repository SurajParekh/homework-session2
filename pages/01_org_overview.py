"""
pages/01_org_overview.py
========================
Org-wide personality landscape.
Charts: OCEAN heatmap, archetype treemap + donut drilldown,
sunburst (dept → archetype → comm style), stress/friction distributions,
scatter (collab vs leadership), grouped bar OCEAN comparison.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_data, filter_df, dept_summary, ocean_heatmap_data,
    DEPT_COLORS, ARCHETYPE_COLORS, STRESS_COLORS, FRICTION_COLORS,
    COMM_COLORS, CONFLICT_COLORS,
)
from utils.chart_helpers import (
    ocean_heatmap, ocean_grouped_bar, donut_chart, sunburst_chart,
    stacked_bar, scatter_collab_leadership, treemap_archetype_dept,
    top_employees_bar,
)
from utils.analysis_engine import describe_org

st.set_page_config(page_title="Org Overview", page_icon="📊", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; background:#0d0f14; color:#e8eaf0; }
[data-testid="stMetric"] { background:#1a1d27; border:1px solid #252840; border-radius:12px; padding:14px; }
.insight-box { background:#1a1d27; border-left:3px solid #7c6ff7; border-radius:8px; padding:14px 16px; margin:8px 0; }
.insight-box.warning { border-left-color:#f59e0b; }
.insight-box.critical { border-left-color:#ef4444; }
hr { border-color:#1f2330; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
df_all  = load_data()
dept_sel= st.session_state.get("selected_dept", "All Departments")
df      = filter_df(df_all, dept_sel)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Org Overview")
st.markdown(f"<p style='color:#8892b0'>{'All Departments' if dept_sel == 'All Departments' else dept_sel} · {len(df)} employees</p>", unsafe_allow_html=True)
st.markdown("---")

# ── KPIs ───────────────────────────────────────────────────────────────────────
org = describe_org(df)
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    ("👥 Headcount",          org["total_employees"],                   None),
    ("🧬 Top Archetype",      org["dominant_archetype"].split()[0],     None),
    ("🤝 Avg Collaboration",  f"{org['avg_collab']}/10",                None),
    ("🎯 Avg Leadership",     f"{org['avg_leadership']}/10",            None),
    ("⚠️ High Stress",        f"{org['high_stress_pct']}%",             None),
    ("🔥 High Friction",      f"{org['high_friction_pct']}%",           None),
]
for col, (label, val, delta) in zip([c1,c2,c3,c4,c5,c6], kpis):
    with col:
        st.metric(label, val, delta)

st.markdown("---")

# ── Row 1: OCEAN Heatmap + Grouped Bar ────────────────────────────────────────
st.markdown("### 🌡️ OCEAN Personality Dimensions")
col_l, col_r = st.columns([1.2, 1])

with col_l:
    heatmap_data = ocean_heatmap_data(df_all if dept_sel == "All Departments" else df_all)
    fig_heat = ocean_heatmap(heatmap_data, "OCEAN Scores by Department — Heatmap")
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("""
    <div class='insight-box'>
    <b>📋 Descriptive:</b> Each cell shows the department's mean score (0–100) for that OCEAN dimension.
    Darker purple = higher score. Scan rows to identify department personality signatures.
    </div>
    """, unsafe_allow_html=True)

with col_r:
    trait = st.selectbox("Select OCEAN trait to compare", ["Openness","Conscientiousness","Extraversion","Agreeableness","Neuroticism"], key="heatmap_trait")
    from utils.chart_helpers import ocean_boxplot
    fig_box = ocean_boxplot(df_all, trait=trait)
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown(f"""
    <div class='insight-box'>
    <b>📋 Descriptive:</b> Distribution spread of <b>{trait}</b> within each department.
    Wide boxes = high internal diversity. The line inside = median; 'sd' markers show standard deviation.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Row 2: Sunburst + Archetype Donut ─────────────────────────────────────────
st.markdown("### 🧬 Personality Archetypes & Communication Styles")
col_l, col_r = st.columns([1.4, 1])

with col_l:
    fig_sun = sunburst_chart(df_all if dept_sel == "All Departments" else df, "Department → Archetype → Communication Style")
    st.plotly_chart(fig_sun, use_container_width=True)
    st.markdown("""
    <div class='insight-box'>
    <b>📋 Descriptive:</b> Three-level sunburst. Inner ring = departments, middle = archetypes within each dept,
    outer = communication styles within each archetype. Click segments to zoom in.
    <br><b>🔍 Diagnostic:</b> Where you see a single colour dominating the outer ring within a department,
    that team has low communication diversity — a potential blind spot.
    </div>
    """, unsafe_allow_html=True)

with col_r:
    fig_arch = donut_chart(
        df["Personality_Archetype"],
        ARCHETYPE_COLORS,
        title="Archetype Distribution",
        height=420,
    )
    st.plotly_chart(fig_arch, use_container_width=True)

    # Drilldown — click an archetype to see the employees
    st.markdown("#### 🔍 Archetype Drilldown")
    selected_arch = st.selectbox(
        "Select an archetype to see members",
        ["— All —"] + df["Personality_Archetype"].unique().tolist(),
        key="arch_drill"
    )
    if selected_arch != "— All —":
        arch_members = df[df["Personality_Archetype"] == selected_arch][
            ["Name", "Department", "Seniority_Level", "Collaboration_Score", "Leadership_Potential_Score"]
        ].sort_values("Collaboration_Score", ascending=False)
        st.dataframe(arch_members.reset_index(drop=True), use_container_width=True, height=200)

st.markdown("---")

# ── Row 3: Treemap ────────────────────────────────────────────────────────────
st.markdown("### 🗺️ Archetype Treemap — Proportional Size by Department")
fig_tree = treemap_archetype_dept(df_all if dept_sel == "All Departments" else df)
st.plotly_chart(fig_tree, use_container_width=True)
st.markdown("""
<div class='insight-box'>
<b>📋 Descriptive:</b> Box size = headcount. Hover for exact counts.
The org skews heavily toward <b>Detail-focused Executors</b> and <b>Balanced Generalists</b>
— typical of operations-heavy SMEs. Creative and connector profiles are underrepresented at the org level.
<br><b>🔍 Diagnostic:</b> If a single archetype occupies >35% of an org, it may create systemic blind spots
in that archetype's weak areas (e.g., too many Executors → slow innovation; too many Innovators → poor delivery discipline).
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Row 4: Style distributions ────────────────────────────────────────────────
st.markdown("### 💬 Communication, Conflict & Work Style Distributions")
c1, c2 = st.columns(2)

with c1:
    fig_comm = stacked_bar(
        df_all if dept_sel == "All Departments" else df,
        "Department", "Communication_Style", COMM_COLORS,
        title="Communication Style by Department (%)", normalise=True,
    )
    st.plotly_chart(fig_comm, use_container_width=True)

with c2:
    fig_conf = stacked_bar(
        df_all if dept_sel == "All Departments" else df,
        "Department", "Conflict_Resolution_Style", CONFLICT_COLORS,
        title="Conflict Style by Department (%)", normalise=True,
    )
    st.plotly_chart(fig_conf, use_container_width=True)

st.markdown("""
<div class='insight-box warning'>
<b>🔍 Diagnostic:</b> Where a department is >40% Avoidant conflict style, expect suppressed disagreement
and hidden friction. This is the leading predictor of retrospective complaints and quiet disengagement.
Finance teams with high Avoidance + high Conscientiousness will avoid raising concerns about quality
until they become critical issues.
</div>
""", unsafe_allow_html=True)

c3, c4 = st.columns(2)
with c3:
    fig_pace = stacked_bar(
        df_all if dept_sel == "All Departments" else df,
        "Department", "Work_Pace_Preference",
        {"Structured": "#7c6ff7", "Flexible": "#f59e0b"},
        title="Work Pace Preference by Department (%)", normalise=True,
    )
    st.plotly_chart(fig_pace, use_container_width=True)

with c4:
    fig_sync = stacked_bar(
        df_all if dept_sel == "All Departments" else df,
        "Department", "Sync_Async_Preference",
        {"Sync (Meetings)": "#06b6d4", "Async (Written)": "#10b981"},
        title="Sync vs Async Preference by Department (%)", normalise=True,
    )
    st.plotly_chart(fig_sync, use_container_width=True)

st.markdown("---")

# ── Row 5: Scatter + Stress/Friction ──────────────────────────────────────────
st.markdown("### 🎯 Collaboration & Leadership Landscape")
col_l, col_r = st.columns([1.4, 1])

with col_l:
    color_by = st.radio("Colour by", ["Department", "Personality_Archetype"], horizontal=True, key="scatter_color")
    fig_scatter = scatter_collab_leadership(df_all if dept_sel == "All Departments" else df, color_by=color_by)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("""
    <div class='insight-box'>
    <b>📋 Descriptive:</b> Each dot = one employee. Bubble size = tenure. Top-right quadrant = high collaboration AND high leadership potential.
    <br><b>🔍 Diagnostic:</b> Employees isolated in the bottom-left are low on both scores — check for role fit or engagement issues.
    Employees with high Leadership but low Collaboration may be effective individual contributors but poor cross-functional partners.
    </div>
    """, unsafe_allow_html=True)

with col_r:
    fig_stress = donut_chart(
        df["Stress_Risk_Level"], STRESS_COLORS,
        title="Stress Risk Distribution", height=280,
    )
    st.plotly_chart(fig_stress, use_container_width=True)

    fig_friction = donut_chart(
        df["Friction_Risk"], FRICTION_COLORS,
        title="Friction Risk Distribution", height=280,
    )
    st.plotly_chart(fig_friction, use_container_width=True)

st.markdown("---")

# ── Row 6: Top employees ──────────────────────────────────────────────────────
st.markdown("### 🏆 Top Employees by Score")
score_option = st.selectbox(
    "Rank by",
    ["Collaboration_Score", "Leadership_Potential_Score", "Meeting_Effectiveness_Score"],
    key="top_score_select"
)
fig_top = top_employees_bar(df, score_option, n=10)
st.plotly_chart(fig_top, use_container_width=True)
