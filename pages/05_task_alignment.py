"""
pages/05_task_alignment.py
==========================
Task-to-employee fit recommendations.
Find who is best suited to any task type, view archetype×seniority grids,
and explore the full task suitability landscape.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import (
    load_data, filter_df, DEPT_COLORS, ARCHETYPE_COLORS,
)
from utils.chart_helpers import top_employees_bar, stacked_bar, donut_chart
from utils.analysis_engine import recommend_task_assignments

st.set_page_config(page_title="Task Alignment", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Space Grotesk',sans-serif; background:#0d0f14; color:#e8eaf0; }
[data-testid="stMetric"] { background:#1a1d27; border:1px solid #252840; border-radius:12px; padding:14px; }
.task-card { background:#1a1d27; border:1px solid #252840; border-radius:10px; padding:14px 16px; margin:6px 0; }
.tag { display:inline-block; background:#1f2330; color:#8892b0; border-radius:6px; padding:3px 8px; font-size:11px; margin:2px; }
hr { border-color:#1f2330; }
</style>
""", unsafe_allow_html=True)

df_all = load_data()

st.markdown("## 🎯 Task Alignment")
st.markdown("<p style='color:#8892b0'>Match employees to tasks based on personality archetype, scores, and suitability ratings.</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Task type taxonomy ─────────────────────────────────────────────────────────
TASK_CATEGORIES = {
    "🔍 Quality Assurance":        "Quality Assurance",
    "📊 Data Analysis":            "Data Analysis",
    "🤝 Stakeholder Management":   "Stakeholder Management",
    "💡 Ideation & Strategy":      "Ideation",
    "⚡ Project Delivery":         "Project Delivery",
    "🛡️ Risk Assessment":          "Risk Assessment",
    "🌱 Coaching & Culture":       "Coaching",
    "🔗 Cross-functional Projects":"Cross-functional",
    "📣 Client Relations":         "Client Relations",
    "🔥 Crisis Response":          "Crisis Response",
    "📋 Compliance & Reporting":   "Compliance",
    "🧩 Process Design":           "Process Design",
}

# ── Row 1: Task Finder ─────────────────────────────────────────────────────────
st.markdown("### 🔎 Find Best-Fit Employees for a Task")

col_l, col_r = st.columns([1, 2])
with col_l:
    task_label   = st.selectbox("Select Task Type", list(TASK_CATEGORIES.keys()), key="task_select")
    task_keyword = TASK_CATEGORIES[task_label]

    dept_filter = st.selectbox("Filter by Department (optional)", ["All"] + sorted(df_all["Department"].unique().tolist()), key="task_dept_filter")
    sen_filter  = st.selectbox("Filter by Seniority (optional)", ["All", "Junior", "Mid-level", "Senior", "Lead/Manager"], key="task_sen_filter")

with col_r:
    matches = recommend_task_assignments(df_all, task_keyword)
    if dept_filter != "All":
        matches = matches[matches["Department"] == dept_filter]
    if sen_filter != "All":
        matches = matches[matches["Seniority_Level"] == sen_filter]

    st.markdown(f"##### {len(matches)} employees suited for **{task_label}**")

    if not matches.empty:
        # Score bars
        fig_task = top_employees_bar(
            df_all[df_all["Employee_ID"].isin(matches["Employee_ID"])],
            "Collaboration_Score",
            title=f"Top Matches — {task_label}",
            n=min(12, len(matches)),
        )
        st.plotly_chart(fig_task, use_container_width=True)
    else:
        st.info("No employees found matching these filters.")

if not matches.empty:
    with st.expander("📋 Full Match Table"):
        display_cols = ["Employee_ID","Name","Department","Personality_Archetype",
                        "Seniority_Level","Collaboration_Score","Leadership_Potential_Score","Task_Suitability"]
        st.dataframe(matches[display_cols].reset_index(drop=True), use_container_width=True)

st.markdown("---")

# ── Row 2: Archetype × Seniority Grid ────────────────────────────────────────
st.markdown("### 🧩 Archetype × Seniority Heatmap")
st.markdown("<p style='color:#8892b0; font-size:0.9rem'>Count of employees per archetype and seniority level — shows talent distribution across the org.</p>", unsafe_allow_html=True)

pivot = df_all.groupby(["Personality_Archetype", "Seniority_Level"], observed=True).size().unstack(fill_value=0)
seniority_order = ["Junior", "Mid-level", "Senior", "Lead/Manager"]
pivot = pivot.reindex(columns=[c for c in seniority_order if c in pivot.columns])

fig_grid = go.Figure(go.Heatmap(
    z=pivot.values,
    x=pivot.columns.tolist(),
    y=pivot.index.tolist(),
    colorscale=[[0,"#0d0f14"],[0.3,"#2d2060"],[0.7,"#7c6ff7"],[1.0,"#c4b5fd"]],
    text=pivot.values,
    texttemplate="%{text}",
    textfont=dict(size=13, color="#e8eaf0"),
    hovertemplate="<b>%{y}</b><br>%{x}: <b>%{z}</b> employees<extra></extra>",
    showscale=True,
    colorbar=dict(
        thickness=12, len=0.8,
        tickfont=dict(color="#8892b0", size=10),
        bgcolor="#13151c", bordercolor="#1f2330",
    ),
))
fig_grid.update_layout(
    paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
    font=dict(family="Space Grotesk, sans-serif", color="#e8eaf0"),
    height=380, margin=dict(l=220, r=20, t=50, b=40),
    xaxis=dict(tickfont=dict(color="#e8eaf0", size=12)),
    yaxis=dict(tickfont=dict(color="#e8eaf0", size=11)),
    title=dict(text="Employee Count: Archetype × Seniority", font=dict(size=14, color="#e8eaf0"), x=0.01),
)
st.plotly_chart(fig_grid, use_container_width=True)

st.markdown("""
<div style='background:#1a1d27; border-left:3px solid #7c6ff7; border-radius:8px; padding:12px 16px; margin:6px 0'>
<b>📋 Descriptive:</b> Brighter cells = more employees in that archetype+seniority combination.
<br><b>🔍 Diagnostic:</b> If a high-value archetype (e.g., "People-oriented Connector") has 0 Leads/Managers,
the org lacks senior-level relationship leadership — a gap that will surface in key account and stakeholder management.
Rows with all-Junior distribution signal a succession planning risk.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: Task coverage map — which archetypes cover which tasks ─────────────
st.markdown("### 🗺️ Task Coverage by Department")
st.markdown("<p style='color:#8892b0; font-size:0.9rem'>How well is each task type covered by each department's current archetype mix?</p>", unsafe_allow_html=True)

task_coverage = {}
for task_lbl, keyword in TASK_CATEGORIES.items():
    for dept in sorted(df_all["Department"].unique()):
        dept_df = df_all[df_all["Department"] == dept]
        count   = dept_df["Task_Suitability"].str.contains(keyword, case=False, na=False).sum()
        task_coverage.setdefault(task_lbl, {})[dept] = count

coverage_df = pd.DataFrame(task_coverage).T
coverage_df.columns.name = "Department"

fig_cov = go.Figure(go.Heatmap(
    z=coverage_df.values,
    x=coverage_df.columns.tolist(),
    y=[t.split(" ", 1)[1] if " " in t else t for t in coverage_df.index.tolist()],
    colorscale=[[0,"#0d0f14"],[0.3,"#0c3320"],[0.7,"#10b981"],[1.0,"#6ee7b7"]],
    text=coverage_df.values,
    texttemplate="%{text}",
    textfont=dict(size=11, color="#e8eaf0"),
    hovertemplate="<b>%{y}</b><br>%{x}: <b>%{z}</b> suited employees<extra></extra>",
    showscale=True,
    colorbar=dict(
        thickness=12, len=0.8,
        tickfont=dict(color="#8892b0", size=10),
        bgcolor="#13151c", bordercolor="#1f2330",
        title=dict(text="Count", font=dict(color="#8892b0", size=10)),
    ),
))
fig_cov.update_layout(
    paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
    font=dict(family="Space Grotesk, sans-serif", color="#e8eaf0"),
    height=500, margin=dict(l=200, r=20, t=50, b=80),
    xaxis=dict(tickfont=dict(color="#e8eaf0", size=11)),
    yaxis=dict(tickfont=dict(color="#e8eaf0", size=11)),
    title=dict(text="Task Coverage — Suited Employees per Department", font=dict(size=14, color="#e8eaf0"), x=0.01),
)
st.plotly_chart(fig_cov, use_container_width=True)

st.markdown("""
<div style='background:#1a1d27; border-left:3px solid #10b981; border-radius:8px; padding:12px 16px; margin:6px 0'>
<b>📋 Descriptive:</b> Green = more people suited to this task in this department. Dark = gap.
<br><b>🔍 Diagnostic:</b> Dark cells represent task coverage gaps. If "Ideation" shows dark for Operations and Finance,
those departments lack creative/innovative profiles — they will need to pull in Marketing or IT for those phases.
Use this as a staffing map for cross-functional project teams.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Row 4: Archetype descriptions ────────────────────────────────────────────
st.markdown("### 📖 Archetype Reference Guide")

archetype_guide = {
    "Detail-focused Executor": {
        "icon": "📋", "color": "#7c6ff7",
        "traits": "High Conscientiousness, Low Openness, Low Extraversion",
        "strengths": "Precision, reliability, process adherence, documentation",
        "risks": "Slow to adapt, may over-engineer, can be rigid under ambiguity",
        "best_for": "QA, compliance, reporting, audit, process documentation",
        "pair_well_with": "Idea-driven Innovators (they execute the ideas), People-oriented Connectors (they handle communication)",
    },
    "People-oriented Connector": {
        "icon": "🤝", "color": "#06b6d4",
        "traits": "High Extraversion, High Agreeableness",
        "strengths": "Relationship building, empathy, stakeholder communication, team cohesion",
        "risks": "May avoid difficult conversations, can over-prioritise harmony over results",
        "best_for": "Client relations, onboarding, mediation, cross-team facilitation",
        "pair_well_with": "Analytical Specialists (analytical rigour + relational warmth)",
    },
    "Idea-driven Innovator": {
        "icon": "💡", "color": "#f59e0b",
        "traits": "High Openness, High Extraversion",
        "strengths": "Creative thinking, conceptual flexibility, strategic framing",
        "risks": "Low execution discipline, moves on before completion, impatient with process",
        "best_for": "Strategy, ideation, product concepting, innovation sprints",
        "pair_well_with": "Detail-focused Executors (to implement the vision)",
    },
    "Analytical Specialist": {
        "icon": "🔬", "color": "#10b981",
        "traits": "High Conscientiousness, Low Extraversion, Moderate-High Openness",
        "strengths": "Data rigor, systems thinking, technical depth, risk identification",
        "risks": "May over-analyse, can be hard to engage verbally, needs written specs",
        "best_for": "Data analysis, technical reviews, risk assessment, architecture",
        "pair_well_with": "Action-oriented Drivers (speed + precision balance)",
    },
    "Action-oriented Driver": {
        "icon": "⚡", "color": "#ef4444",
        "traits": "High Extraversion, Moderate-Low Conscientiousness",
        "strengths": "Urgency, momentum, results focus, negotiation",
        "risks": "Skips process, creates friction with structured teams, short-term focus",
        "best_for": "Sales, project delivery, crisis response, change execution",
        "pair_well_with": "Detail-focused Executors (to clean up the trail they leave)",
    },
    "Empathetic Supporter": {
        "icon": "🌱", "color": "#ec4899",
        "traits": "High Agreeableness, Low-Moderate Extraversion",
        "strengths": "Emotional intelligence, conflict de-escalation, mentoring, wellbeing",
        "risks": "Can be overlooked in competitive environments, absorbs others' stress",
        "best_for": "Coaching, culture programs, wellbeing, conflict resolution",
        "pair_well_with": "Action-oriented Drivers (softens the impact, handles the human side)",
    },
    "Balanced Generalist": {
        "icon": "⚖️", "color": "#94a3b8",
        "traits": "Moderate scores across all OCEAN dimensions",
        "strengths": "Adaptability, versatility, cross-context effectiveness",
        "risks": "May lack deep specialisation, can be overlooked for specific roles",
        "best_for": "Cross-functional projects, coordination, change management, facilitation",
        "pair_well_with": "Any archetype — acts as connective tissue",
    },
}

for arch, info in archetype_guide.items():
    with st.expander(f"{info['icon']} {arch}"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div style='background:#1a1d27; border-radius:8px; padding:14px'>
                <p style='color:#8892b0; font-size:12px; margin:0 0 4px'>OCEAN Profile</p>
                <p style='margin:0 0 10px'><code>{info['traits']}</code></p>
                <p style='color:#8892b0; font-size:12px; margin:0 0 4px'>Strengths</p>
                <p style='margin:0 0 10px'>{info['strengths']}</p>
                <p style='color:#8892b0; font-size:12px; margin:0 0 4px'>Risks</p>
                <p style='margin:0'>{info['risks']}</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style='background:#1a1d27; border-radius:8px; padding:14px'>
                <p style='color:#8892b0; font-size:12px; margin:0 0 4px'>Best Suited For</p>
                <p style='margin:0 0 10px; color:{info["color"]}'><b>{info['best_for']}</b></p>
                <p style='color:#8892b0; font-size:12px; margin:0 0 4px'>Pairs Well With</p>
                <p style='margin:0'>{info['pair_well_with']}</p>
            </div>
            """, unsafe_allow_html=True)
        # Show employees with this archetype
        arch_members = df_all[df_all["Personality_Archetype"] == arch][
            ["Name", "Department", "Seniority_Level", "Collaboration_Score", "Leadership_Potential_Score"]
        ].sort_values("Collaboration_Score", ascending=False).reset_index(drop=True)
        st.markdown(f"**{len(arch_members)} employees with this archetype:**")
        st.dataframe(arch_members, use_container_width=True, height=180)
