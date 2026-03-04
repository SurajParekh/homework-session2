"""
pages/03_employee_profiles.py
==============================
Individual employee profile cards with OCEAN radar, scores,
personality breakdown, task suitability, and comparison mode.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_data, filter_df, get_employee, score_color,
    DEPT_COLORS, ARCHETYPE_COLORS, STRESS_COLORS, FRICTION_COLORS,
)
from utils.chart_helpers import ocean_radar, gauge_chart
from utils.analysis_engine import describe_employee

st.set_page_config(page_title="Employee Profiles", page_icon="👤", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Space Grotesk',sans-serif; background:#0d0f14; color:#e8eaf0; }
.profile-card { background:#1a1d27; border:1px solid #252840; border-radius:14px; padding:20px 24px; }
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; margin:3px 2px; }
.trait-row { display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #1f2330; }
.trait-bar-bg { background:#1f2330; border-radius:4px; height:8px; flex:1; margin:0 12px; }
.tag { display:inline-block; background:#1f2330; color:#8892b0; border-radius:6px; padding:3px 8px; font-size:11px; margin:2px; }
hr { border-color:#1f2330; }
</style>
""", unsafe_allow_html=True)

df_all = load_data()

st.markdown("## 👤 Employee Profiles")
st.markdown("---")

# ── Filters ────────────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    dept_f = st.selectbox("Department", ["All"] + sorted(df_all["Department"].unique().tolist()), key="profile_dept")
with col_f2:
    arch_f = st.selectbox("Archetype", ["All"] + sorted(df_all["Personality_Archetype"].unique().tolist()), key="profile_arch")
with col_f3:
    sen_f  = st.selectbox("Seniority", ["All", "Junior", "Mid-level", "Senior", "Lead/Manager"], key="profile_sen")

filtered = df_all.copy()
if dept_f != "All": filtered = filtered[filtered["Department"] == dept_f]
if arch_f != "All": filtered = filtered[filtered["Personality_Archetype"] == arch_f]
if sen_f  != "All": filtered = filtered[filtered["Seniority_Level"] == sen_f]

# ── Employee selector ──────────────────────────────────────────────────────────
emp_options = filtered["Employee_ID"] + " — " + filtered["Name"] + " (" + filtered["Department"] + ")"
selected_str = st.selectbox("Select Employee", emp_options.tolist(), key="emp_select")
emp_id = selected_str.split(" — ")[0] if selected_str else None

# ── Compare mode ───────────────────────────────────────────────────────────────
compare_mode = st.checkbox("Compare with another employee", key="compare_toggle")
if compare_mode:
    other_options = filtered[filtered["Employee_ID"] != emp_id]["Employee_ID"] + " — " + filtered[filtered["Employee_ID"] != emp_id]["Name"] + " (" + filtered[filtered["Employee_ID"] != emp_id]["Department"] + ")"
    compare_str = st.selectbox("Compare with", other_options.tolist(), key="compare_select")
    compare_id  = compare_str.split(" — ")[0] if compare_str else None
else:
    compare_id = None

st.markdown("---")

# ── Helper: render single profile ─────────────────────────────────────────────
def render_profile(emp_id: str, df: pd.DataFrame):
    row = get_employee(df, emp_id)
    if row is None:
        st.warning("Employee not found.")
        return

    p = describe_employee(row)
    dept_color    = DEPT_COLORS.get(p["dept"], "#7c6ff7")
    arch_color    = ARCHETYPE_COLORS.get(p["archetype"], "#7c6ff7")
    stress_color  = STRESS_COLORS.get(p["stress_risk"], "#94a3b8")
    friction_color= FRICTION_COLORS.get(p["friction_risk"], "#94a3b8")

    # Profile header card
    st.markdown(f"""
    <div class='profile-card'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start'>
            <div>
                <h2 style='margin:0; font-size:1.6rem'>{p['name']}</h2>
                <p style='color:#8892b0; margin:4px 0 10px'>
                    {p['seniority']} · {p['dept']} · {p['tenure']} yr{'' if p['tenure']==1 else 's'} tenure
                </p>
                <span class='badge' style='background:{arch_color}33; color:{arch_color}'>{p['archetype']}</span>
                <span class='badge' style='background:{dept_color}33; color:{dept_color}'>{p['dept']}</span>
                <span class='badge' style='background:#1f2330; color:#8892b0'>MBTI: {p['mbti']}</span>
            </div>
            <div style='text-align:right'>
                <span class='badge' style='background:{stress_color}33; color:{stress_color}'>Stress: {p['stress_risk']}</span><br>
                <span class='badge' style='background:{friction_color}33; color:{friction_color}'>Friction: {p['friction_risk']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_radar, col_scores = st.columns([1.2, 1])

    with col_radar:
        fig_r = ocean_radar({p["name"]: p["ocean"]}, title="OCEAN Profile")
        st.plotly_chart(fig_r, use_container_width=True)

    with col_scores:
        st.markdown("#### 📊 Performance Scores")
        for label, val, key in [
            ("🤝 Collaboration",    p["collab_score"],  "collab"),
            ("🎯 Leadership Potential", p["leadership"],   "lead"),
            ("🗣️ Meeting Effectiveness", p["meeting_eff"],  "meet"),
        ]:
            color = score_color(val)
            st.markdown(f"""
            <div style='display:flex; align-items:center; margin:10px 0'>
                <span style='width:190px; font-size:13px'>{label}</span>
                <div style='flex:1; background:#1f2330; border-radius:6px; height:10px; margin:0 12px'>
                    <div style='background:{color}; width:{val*10}%; height:10px; border-radius:6px'></div>
                </div>
                <span style='font-weight:700; color:{color}'>{val}/10</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🎭 Style Summary")
        styles = [
            ("💬 Comm Style",     p["comm_style"]),
            ("⚡ Conflict Style", p["conflict_style"]),
            ("🕐 Work Pace",      p["work_pace"]),
            ("📡 Sync Pref",      p["sync_pref"]),
            ("🧠 Decision Style", p["decision_style"]),
        ]
        for label, val in styles:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #1f2330; font-size:13px'>
                <span style='color:#8892b0'>{label}</span>
                <span style='font-weight:500'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

    # OCEAN detail bars
    st.markdown("#### 🧬 OCEAN Trait Detail")
    trait_icons = {"Openness": "🌱", "Conscientiousness": "📋", "Extraversion": "🗣️", "Agreeableness": "🤝", "Neuroticism": "🌊"}
    for trait, score in p["ocean"].items():
        color = "#7c6ff7" if score >= 60 else "#f59e0b" if score >= 40 else "#ef4444"
        st.markdown(f"""
        <div style='display:flex; align-items:center; margin:6px 0'>
            <span style='width:160px; font-size:13px'>{trait_icons.get(trait,'')} {trait}</span>
            <div style='flex:1; background:#1f2330; border-radius:6px; height:8px; margin:0 12px'>
                <div style='background:{color}; width:{score}%; height:8px; border-radius:6px'></div>
            </div>
            <span style='font-weight:600; color:{color}; width:32px; text-align:right'>{score}</span>
        </div>
        """, unsafe_allow_html=True)

    # Task suitability
    st.markdown("#### 🎯 Task Suitability")
    tasks = [t.strip() for t in p["task_fit"].split(",")]
    tags_html = "".join([f"<span class='tag'>{t}</span>" for t in tasks])
    st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)


# ── Render profile(s) ──────────────────────────────────────────────────────────
if compare_id:
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(f"#### Employee 1")
        render_profile(emp_id, df_all)
    with col_right:
        st.markdown(f"#### Employee 2")
        render_profile(compare_id, df_all)

    # Compatibility note
    st.markdown("---")
    st.markdown("### 🔗 Compatibility Analysis")
    from utils.analysis_engine import predict_collab_success
    compat = predict_collab_success(df_all, emp_id, compare_id)
    color  = score_color(compat["compat_score"])
    st.markdown(f"""
    <div style='background:#1a1d27; border:1px solid #252840; border-radius:12px; padding:20px'>
        <h4 style='margin:0 0 8px'>Compatibility Score: <span style='color:{color}'>{compat['compat_score']}/10</span></h4>
        <p style='color:#8892b0; margin:0 0 12px'>Based on OCEAN profile distance and style alignment</p>
        {''.join(f"<div style='background:#0d0f14; border-radius:6px; padding:8px 12px; margin:4px 0; font-size:13px'>⚠️ {n}</div>" for n in compat.get('notes', [])) or "<p style='color:#10b981'>✅ High compatibility — similar working styles across all dimensions.</p>"}
    </div>
    """, unsafe_allow_html=True)

else:
    render_profile(emp_id, df_all)
