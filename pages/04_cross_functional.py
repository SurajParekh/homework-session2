"""
pages/04_cross_functional.py
=============================
Inter-team friction matrix, collaboration heatmap,
pairwise diagnostic analysis, and cross-functional team builder.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import (
    load_data, friction_matrix, dept_summary, DEPT_COLORS,
)
from utils.chart_helpers import (
    friction_heatmap, stacked_bar, scatter_collab_leadership,
)
from utils.analysis_engine import (
    diagnose_cross_functional_pair, recommend_task_assignments,
)

st.set_page_config(page_title="Cross-Functional Map", page_icon="🔗", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Space Grotesk',sans-serif; background:#0d0f14; color:#e8eaf0; }
[data-testid="stMetric"] { background:#1a1d27; border:1px solid #252840; border-radius:12px; padding:14px; }
.insight-info     { background:#1a1d27; border-left:3px solid #7c6ff7; border-radius:8px; padding:12px 16px; margin:6px 0; }
.insight-warning  { background:#1a1501; border-left:3px solid #f59e0b; border-radius:8px; padding:12px 16px; margin:6px 0; }
.insight-critical { background:#1f0707; border-left:3px solid #ef4444; border-radius:8px; padding:12px 16px; margin:6px 0; }
hr { border-color:#1f2330; }
</style>
""", unsafe_allow_html=True)

df_all = load_data()
depts  = sorted(df_all["Department"].unique().tolist())

st.markdown("## 🔗 Cross-Functional Collaboration Map")
st.markdown("<p style='color:#8892b0'>Understand friction potential and collaboration fit between departments</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Row 1: Friction Heatmap ────────────────────────────────────────────────────
st.markdown("### 🌡️ Inter-Department Friction Matrix")
st.markdown("<p style='color:#8892b0; font-size:0.9rem'>Score = mean absolute OCEAN difference between department pairs, normalised 0–10. Higher = more potential friction.</p>", unsafe_allow_html=True)

fric_mat = friction_matrix(df_all)
fig_fric = friction_heatmap(fric_mat, "Inter-Department Friction Potential (OCEAN-based)")
st.plotly_chart(fig_fric, use_container_width=True)

st.markdown("""
<div class='insight-info'>
<b>📋 Descriptive:</b> Each cell = OCEAN distance score between the row and column department.
Dark red = high personality divergence = higher friction potential.
Diagonal is always 0 (same department).
<br><b>🔍 Diagnostic:</b> The highest-friction pairings are usually between departments with opposing
Conscientiousness and Extraversion profiles — e.g., Operations (high C, low E) vs Marketing (low C, high E).
These teams optimise for different variables and will clash without explicit interface protocols.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Row 2: Collaboration Score Heatmap (avg collab score between dept pairs) ──
st.markdown("### 🤝 Average Collaboration Score by Department")

dept_avg_collab = df_all.groupby("Department", observed=True)["Collaboration_Score"].mean().round(2)

fig_collab = go.Figure(go.Bar(
    x=dept_avg_collab.index.tolist(),
    y=dept_avg_collab.values,
    marker_color=[DEPT_COLORS.get(d, "#7c6ff7") for d in dept_avg_collab.index],
    text=dept_avg_collab.values.round(1),
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Avg Collaboration Score: %{y:.2f}<extra></extra>",
))
fig_collab.update_layout(
    paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
    font=dict(family="Space Grotesk, sans-serif", color="#e8eaf0"),
    title=dict(text="Average Collaboration Score by Department", font=dict(size=14, color="#e8eaf0"), x=0.01),
    xaxis=dict(tickfont=dict(color="#e8eaf0"), gridcolor="#1f2330"),
    yaxis=dict(tickfont=dict(color="#e8eaf0"), gridcolor="#1f2330", range=[0, 11]),
    height=360, margin=dict(l=40, r=20, t=50, b=40),
    showlegend=False,
)
st.plotly_chart(fig_collab, use_container_width=True)

st.markdown("---")

# ── Row 3: Style comparison between two departments ──────────────────────────
st.markdown("### 🔍 Pairwise Department Analysis")
col_l, col_r = st.columns(2)

with col_l:
    dept1 = st.selectbox("Department A", depts, index=0, key="pair_dept1")
with col_r:
    dept2 = st.selectbox("Department B", [d for d in depts if d != dept1], index=2, key="pair_dept2")

d1 = df_all[df_all["Department"] == dept1]
d2 = df_all[df_all["Department"] == dept2]

# OCEAN comparison radar
from utils.chart_helpers import ocean_radar, DARK_BG, CARD_BG, BORDER_COLOR, TEXT_COLOR

ocean_data = {
    dept1: {t: round(d1[t].mean(), 1) for t in ["Openness","Conscientiousness","Extraversion","Agreeableness","Neuroticism"]},
    dept2: {t: round(d2[t].mean(), 1) for t in ["Openness","Conscientiousness","Extraversion","Agreeableness","Neuroticism"]},
}
fig_compare = ocean_radar(ocean_data, title=f"{dept1} vs {dept2} — OCEAN Comparison")
st.plotly_chart(fig_compare, use_container_width=True)

# Style comparison bars
col_l2, col_r2 = st.columns(2)

pair_df = df_all[df_all["Department"].isin([dept1, dept2])].copy()

with col_l2:
    fig_pace = stacked_bar(
        pair_df, "Department", "Work_Pace_Preference",
        {"Structured": "#7c6ff7", "Flexible": "#f59e0b"},
        title="Work Pace Comparison (%)", normalise=True, height=280,
    )
    st.plotly_chart(fig_pace, use_container_width=True)

with col_r2:
    fig_sync = stacked_bar(
        pair_df, "Department", "Sync_Async_Preference",
        {"Sync (Meetings)": "#06b6d4", "Async (Written)": "#10b981"},
        title="Sync vs Async Comparison (%)", normalise=True, height=280,
    )
    st.plotly_chart(fig_sync, use_container_width=True)

col_l3, col_r3 = st.columns(2)
with col_l3:
    fig_conf2 = stacked_bar(
        pair_df, "Department", "Conflict_Resolution_Style",
        {"Collaborative": "#10b981", "Avoidant": "#94a3b8", "Competitive": "#ef4444", "Compromising": "#f59e0b"},
        title="Conflict Style Comparison (%)", normalise=True, height=280,
    )
    st.plotly_chart(fig_conf2, use_container_width=True)

with col_r3:
    fig_dec2 = stacked_bar(
        pair_df, "Department", "Decision_Making_Style",
        {"Data-driven": "#7c6ff7", "Intuitive": "#f59e0b"},
        title="Decision Style Comparison (%)", normalise=True, height=280,
    )
    st.plotly_chart(fig_dec2, use_container_width=True)

# Pairwise diagnostic insights
st.markdown(f"#### 🔍 Diagnostic: {dept1} ↔ {dept2}")
pair_insights = diagnose_cross_functional_pair(df_all, dept1, dept2)
for ins in pair_insights:
    css_class = f"insight-{ins['severity']}"
    icon = "⚠️" if ins["severity"] == "warning" else ("🚨" if ins["severity"] == "critical" else "ℹ️")
    st.markdown(f"""
    <div class='{css_class}'>
        <b>{icon} {ins['title']}</b><br>
        <span style='font-size:0.9rem'>{ins['body']}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Row 4: Cross-Functional Team Builder ──────────────────────────────────────
st.markdown("### 🏗️ Cross-Functional Team Builder")
st.markdown("<p style='color:#8892b0'>Select departments to include → view the combined personality profile of a cross-functional team.</p>", unsafe_allow_html=True)

selected_depts = st.multiselect("Include departments", depts, default=depts[:3], key="xfunc_depts")

if len(selected_depts) >= 2:
    xf_df = df_all[df_all["Department"].isin(selected_depts)].copy()

    col_l4, col_r4 = st.columns([1.2, 1])
    with col_l4:
        ocean_xf = {d: {t: round(xf_df[xf_df["Department"]==d][t].mean(),1) for t in ["Openness","Conscientiousness","Extraversion","Agreeableness","Neuroticism"]} for d in selected_depts}
        fig_xf = ocean_radar(ocean_xf, title="Combined Team OCEAN Profiles")
        st.plotly_chart(fig_xf, use_container_width=True)

    with col_r4:
        st.markdown("##### Combined Team Stats")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("👥 Team Size", len(xf_df))
            st.metric("🤝 Avg Collab", round(xf_df["Collaboration_Score"].mean(), 1))
        with c2:
            st.metric("🎯 Avg Leadership", round(xf_df["Leadership_Potential_Score"].mean(), 1))
            high_fric_pct = round((xf_df["Friction_Risk"] == "High").mean() * 100, 1)
            st.metric("🔥 High Friction %", f"{high_fric_pct}%")

        # Top 5 collaborators from this combined team
        st.markdown("##### Top 5 Collaborators in this Team")
        top5 = xf_df.nlargest(5, "Collaboration_Score")[
            ["Name", "Department", "Collaboration_Score", "Personality_Archetype"]
        ].reset_index(drop=True)
        st.dataframe(top5, use_container_width=True, height=200)

    # Style distribution of combined team
    fig_comm_xf = stacked_bar(
        xf_df, "Department", "Communication_Style",
        {"Direct": "#ef4444", "Analytical": "#7c6ff7", "Diplomatic": "#06b6d4", "Expressive": "#f59e0b"},
        title="Communication Style Mix in Cross-Functional Team (%)", normalise=True,
    )
    st.plotly_chart(fig_comm_xf, use_container_width=True)

else:
    st.info("Select at least 2 departments to build a cross-functional team view.")

st.markdown("---")

# ── Row 5: Org Scatter ────────────────────────────────────────────────────────
st.markdown("### 📍 Collaboration vs Leadership — Full Org View")
fig_sc = scatter_collab_leadership(df_all)
st.plotly_chart(fig_sc, use_container_width=True)
