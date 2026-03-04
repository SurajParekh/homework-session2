"""
pages/02_department_deep_dive.py
================================
Per-department personality deep dive with drilldown donuts,
OCEAN radar, diagnostic callouts, and norm recommendations.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_data, DEPT_COLORS, ARCHETYPE_COLORS,
    COMM_COLORS, CONFLICT_COLORS, STRESS_COLORS, FRICTION_COLORS,
)
from utils.chart_helpers import (
    ocean_radar, donut_chart, stacked_bar, ocean_boxplot, top_employees_bar,
)
from utils.analysis_engine import (
    describe_department, diagnose_department, prescribe_team_norms,
)

st.set_page_config(page_title="Department Deep Dive", page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Space Grotesk',sans-serif; background:#0d0f14; color:#e8eaf0; }
[data-testid="stMetric"] { background:#1a1d27; border:1px solid #252840; border-radius:12px; padding:14px; }
.insight-info     { background:#1a1d27; border-left:3px solid #7c6ff7; border-radius:8px; padding:12px 16px; margin:6px 0; }
.insight-warning  { background:#1a1501; border-left:3px solid #f59e0b; border-radius:8px; padding:12px 16px; margin:6px 0; }
.insight-critical { background:#1f0707; border-left:3px solid #ef4444; border-radius:8px; padding:12px 16px; margin:6px 0; }
.norm-item        { background:#0f1420; border:1px solid #1f2330; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:0.9rem; }
hr { border-color:#1f2330; }
</style>
""", unsafe_allow_html=True)

df_all = load_data()

# ── Department selector ────────────────────────────────────────────────────────
st.markdown("## 🔍 Department Deep Dive")

dept = st.selectbox(
    "Select Department",
    sorted(df_all["Department"].unique().tolist()),
    key="dept_deep_dive_select"
)

df_dept = df_all[df_all["Department"] == dept].copy()
desc    = describe_department(df_all, dept)
st.markdown(f"<p style='color:#8892b0'>{dept} · {desc['headcount']} employees · Avg tenure {desc['tenure_mean']} years</p>", unsafe_allow_html=True)
st.markdown("---")

# ── KPI row ────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
metrics = [
    ("👥 Headcount",         desc["headcount"],                  None),
    ("🧬 Top Archetype",     desc["dominant_archetype"].split()[0], None),
    ("🤝 Avg Collab",        f"{desc['avg_collab']}/10",          None),
    ("🎯 Avg Leadership",    f"{desc['avg_leadership']}/10",      None),
    ("⚠️ High Stress",       f"{desc['high_stress_n']} people",   None),
    ("🔥 High Friction",     f"{desc['high_friction_n']} people", None),
]
for col, (label, val, d) in zip([c1,c2,c3,c4,c5,c6], metrics):
    with col:
        st.metric(label, val, d)

st.markdown("---")

# ── Row 1: OCEAN Radar + Archetype donut ──────────────────────────────────────
st.markdown("### 🧭 OCEAN Profile & Archetype Mix")
col_l, col_r = st.columns([1, 1])

with col_l:
    # Build radar data comparing this dept to org average
    org_ocean   = {t: round(df_all[t].mean(), 1) for t in ["Openness","Conscientiousness","Extraversion","Agreeableness","Neuroticism"]}
    dept_ocean  = {t: round(df_dept[t].mean(), 1) for t in ["Openness","Conscientiousness","Extraversion","Agreeableness","Neuroticism"]}
    radar_data  = {dept: dept_ocean, "Org Average": org_ocean}
    fig_radar   = ocean_radar(radar_data, title=f"{dept} vs Org Average — OCEAN Radar")
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown(f"""
    <div class='insight-info'>
    <b>📋 Descriptive:</b> Purple = {dept} profile. Grey = org average.
    Where {dept} extends beyond the org average, that trait is a department strength (or risk, depending on context).
    Highest trait: <b>{desc['highest_trait']}</b> ({desc['ocean_means'][desc['highest_trait']]:.0f}).
    Lowest trait: <b>{desc['lowest_trait']}</b> ({desc['ocean_means'][desc['lowest_trait']]:.0f}).
    </div>
    """, unsafe_allow_html=True)

with col_r:
    fig_arch = donut_chart(
        df_dept["Personality_Archetype"], ARCHETYPE_COLORS,
        title=f"{dept} — Archetype Distribution",
    )
    st.plotly_chart(fig_arch, use_container_width=True)

    # Drilldown: click archetype → see members
    st.markdown("#### 🔍 Drilldown: Archetype → Members")
    arch_opts = ["— All —"] + df_dept["Personality_Archetype"].unique().tolist()
    drill_arch = st.selectbox("Filter by archetype", arch_opts, key="dept_arch_drill")
    subset = df_dept if drill_arch == "— All —" else df_dept[df_dept["Personality_Archetype"] == drill_arch]
    st.dataframe(
        subset[["Name","Seniority_Level","Communication_Style","Collaboration_Score","Leadership_Potential_Score"]]
        .sort_values("Collaboration_Score", ascending=False)
        .reset_index(drop=True),
        use_container_width=True, height=180,
    )

st.markdown("---")

# ── Row 2: Comm + Conflict Donut Drilldowns ────────────────────────────────────
st.markdown("### 💬 Communication & Conflict Style")
col_l, col_r = st.columns(2)

with col_l:
    fig_comm = donut_chart(
        df_dept["Communication_Style"], COMM_COLORS,
        title="Communication Style", height=340,
    )
    st.plotly_chart(fig_comm, use_container_width=True)

    drill_comm = st.selectbox("Drilldown: Comm Style → Members", ["— All —"] + list(COMM_COLORS.keys()), key="comm_drill")
    if drill_comm != "— All —":
        st.dataframe(
            df_dept[df_dept["Communication_Style"] == drill_comm][
                ["Name","Personality_Archetype","Conflict_Resolution_Style","Sync_Async_Preference","Collaboration_Score"]
            ].reset_index(drop=True),
            use_container_width=True, height=160,
        )

with col_r:
    fig_conf = donut_chart(
        df_dept["Conflict_Resolution_Style"], CONFLICT_COLORS,
        title="Conflict Resolution Style", height=340,
    )
    st.plotly_chart(fig_conf, use_container_width=True)

    drill_conf = st.selectbox("Drilldown: Conflict Style → Members",
        ["— All —","Collaborative","Avoidant","Competitive","Compromising"], key="conf_drill")
    if drill_conf != "— All —":
        st.dataframe(
            df_dept[df_dept["Conflict_Resolution_Style"] == drill_conf][
                ["Name","Personality_Archetype","Communication_Style","Stress_Risk_Level","Friction_Risk"]
            ].reset_index(drop=True),
            use_container_width=True, height=160,
        )

st.markdown("---")

# ── Row 3: Work style donuts ──────────────────────────────────────────────────
st.markdown("### ⚙️ Work Style Preferences")
c1, c2, c3 = st.columns(3)

with c1:
    fig_pace = donut_chart(
        df_dept["Work_Pace_Preference"],
        {"Structured": "#7c6ff7", "Flexible": "#f59e0b"},
        title="Work Pace", height=300,
    )
    st.plotly_chart(fig_pace, use_container_width=True)

with c2:
    fig_sync = donut_chart(
        df_dept["Sync_Async_Preference"],
        {"Sync (Meetings)": "#06b6d4", "Async (Written)": "#10b981"},
        title="Sync vs Async", height=300,
    )
    st.plotly_chart(fig_sync, use_container_width=True)

with c3:
    fig_dec = donut_chart(
        df_dept["Decision_Making_Style"],
        {"Data-driven": "#7c6ff7", "Intuitive": "#f59e0b"},
        title="Decision Style", height=300,
    )
    st.plotly_chart(fig_dec, use_container_width=True)

st.markdown("---")

# ── Row 4: Stress & Friction ──────────────────────────────────────────────────
st.markdown("### ⚠️ Stress & Friction Risk")
c1, c2 = st.columns(2)

with c1:
    fig_stress = donut_chart(
        df_dept["Stress_Risk_Level"], STRESS_COLORS,
        title="Stress Risk Level", height=300,
    )
    st.plotly_chart(fig_stress, use_container_width=True)

with c2:
    fig_fric = donut_chart(
        df_dept["Friction_Risk"], FRICTION_COLORS,
        title="Friction Risk Level", height=300,
    )
    st.plotly_chart(fig_fric, use_container_width=True)

st.markdown("---")

# ── Row 5: Diagnostic Callouts ────────────────────────────────────────────────
st.markdown("### 🔍 Diagnostic Insights")
insights = diagnose_department(df_all, dept)
for ins in insights:
    css_class = f"insight-{ins['severity']}"
    icon = "⚠️" if ins["severity"] == "warning" else ("🚨" if ins["severity"] == "critical" else "ℹ️")
    st.markdown(f"""
    <div class='{css_class}'>
        <b>{icon} {ins['title']}</b><br>
        <span style='font-size:0.9rem'>{ins['body']}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Row 6: Prescriptive Norms ─────────────────────────────────────────────────
st.markdown("### ✅ Recommended Team Norms")
norms = prescribe_team_norms(insights)
for norm in norms:
    st.markdown(f"<div class='norm-item'>{norm}</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 7: Top employees ──────────────────────────────────────────────────────
st.markdown(f"### 🏆 Top Performers — {dept}")
score_col = st.selectbox("Rank by", ["Collaboration_Score","Leadership_Potential_Score","Meeting_Effectiveness_Score"], key="dept_top_score")
fig_top = top_employees_bar(df_dept, score_col, n=min(10, len(df_dept)))
st.plotly_chart(fig_top, use_container_width=True)

# Full employee table
with st.expander("📋 Full Department Employee Table"):
    st.dataframe(
        df_dept[[
            "Employee_ID","Name","Seniority_Level","Tenure_Years",
            "Personality_Archetype","Communication_Style","Conflict_Resolution_Style",
            "Work_Pace_Preference","Sync_Async_Preference","Decision_Making_Style",
            "Collaboration_Score","Leadership_Potential_Score","Stress_Risk_Level","Friction_Risk"
        ]].reset_index(drop=True),
        use_container_width=True,
    )
