"""
utils/analysis_engine.py
=========================
Descriptive and Diagnostic analysis engine.

Returns structured insight dictionaries that pages can render as
callout boxes, tables, or narrative text — keeping analysis logic
separate from presentation logic.

Analysis types implemented:
  - Descriptive  : distributions, averages, patterns (WHAT)
  - Diagnostic   : root cause exploration, friction drivers (WHY)
  - Predictive   : risk flags, collaboration forecasts (WHAT WILL HAPPEN)  [stubs]
  - Prescriptive : norm recommendations, role fit (WHAT TO DO)             [stubs]
"""

import pandas as pd
import numpy as np
from utils.data_loader import OCEAN_COLS, DEPT_COLORS

# ─────────────────────────────────────────────────────────────────────────────
# DESCRIPTIVE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def describe_org(df: pd.DataFrame) -> dict:
    """
    Top-level descriptive summary of the entire organisation.
    Returns a dict of labelled insights.
    """
    dominant_archetype = df["Personality_Archetype"].value_counts().idxmax()
    dominant_comm      = df["Communication_Style"].value_counts().idxmax()
    dominant_conflict  = df["Conflict_Resolution_Style"].value_counts().idxmax()
    dominant_pace      = df["Work_Pace_Preference"].value_counts().idxmax()
    dominant_sync      = df["Sync_Async_Preference"].value_counts().idxmax()
    dominant_decision  = df["Decision_Making_Style"].value_counts().idxmax()
    high_stress_pct    = (df["Stress_Risk_Level"] == "High").mean() * 100
    high_friction_pct  = (df["Friction_Risk"] == "High").mean() * 100

    avg_collab     = df["Collaboration_Score"].mean()
    avg_leadership = df["Leadership_Potential_Score"].mean()
    avg_meeting    = df["Meeting_Effectiveness_Score"].mean()

    dept_sizes    = df.groupby("Department", observed=True).size()
    largest_dept  = dept_sizes.idxmax()
    smallest_dept = dept_sizes.idxmin()

    ocean_means   = df[OCEAN_COLS].mean().round(1)
    highest_trait = ocean_means.idxmax()
    lowest_trait  = ocean_means.idxmin()

    return {
        "total_employees":     len(df),
        "departments":         df["Department"].nunique(),
        "dominant_archetype":  dominant_archetype,
        "dominant_comm":       dominant_comm,
        "dominant_conflict":   dominant_conflict,
        "dominant_pace":       dominant_pace,
        "dominant_sync":       dominant_sync,
        "dominant_decision":   dominant_decision,
        "high_stress_pct":     round(high_stress_pct, 1),
        "high_friction_pct":   round(high_friction_pct, 1),
        "avg_collab":          round(avg_collab, 1),
        "avg_leadership":      round(avg_leadership, 1),
        "avg_meeting":         round(avg_meeting, 1),
        "largest_dept":        largest_dept,
        "smallest_dept":       smallest_dept,
        "ocean_means":         ocean_means.to_dict(),
        "highest_ocean_trait": highest_trait,
        "lowest_ocean_trait":  lowest_trait,
    }


def describe_department(df: pd.DataFrame, dept: str) -> dict:
    """
    Descriptive summary for a single department.
    """
    d = df[df["Department"] == dept]
    if d.empty:
        return {}

    ocean_means       = d[OCEAN_COLS].mean().round(1)
    archetype_counts  = d["Personality_Archetype"].value_counts()
    dominant_archetype= archetype_counts.idxmax()
    archetype_share   = round(archetype_counts.iloc[0] / len(d) * 100, 1)
    dominant_comm     = d["Communication_Style"].value_counts().idxmax()
    dominant_conflict = d["Conflict_Resolution_Style"].value_counts().idxmax()
    dominant_pace     = d["Work_Pace_Preference"].value_counts().idxmax()
    dominant_sync     = d["Sync_Async_Preference"].value_counts().idxmax()
    dominant_decision = d["Decision_Making_Style"].value_counts().idxmax()

    avg_collab      = d["Collaboration_Score"].mean()
    avg_leadership  = d["Leadership_Potential_Score"].mean()
    avg_meeting_eff = d["Meeting_Effectiveness_Score"].mean()
    high_stress_n   = (d["Stress_Risk_Level"] == "High").sum()
    high_friction_n = (d["Friction_Risk"] == "High").sum()

    seniority_dist  = d["Seniority_Level"].value_counts().to_dict()
    tenure_mean     = d["Tenure_Years"].mean()

    return {
        "dept":               dept,
        "headcount":          len(d),
        "ocean_means":        ocean_means.to_dict(),
        "highest_trait":      ocean_means.idxmax(),
        "lowest_trait":       ocean_means.idxmin(),
        "dominant_archetype": dominant_archetype,
        "archetype_share":    archetype_share,
        "archetype_counts":   archetype_counts.to_dict(),
        "dominant_comm":      dominant_comm,
        "dominant_conflict":  dominant_conflict,
        "dominant_pace":      dominant_pace,
        "dominant_sync":      dominant_sync,
        "dominant_decision":  dominant_decision,
        "avg_collab":         round(avg_collab, 1),
        "avg_leadership":     round(avg_leadership, 1),
        "avg_meeting_eff":    round(avg_meeting_eff, 1),
        "high_stress_n":      int(high_stress_n),
        "high_friction_n":    int(high_friction_n),
        "seniority_dist":     seniority_dist,
        "tenure_mean":        round(tenure_mean, 1),
    }


def describe_employee(row: pd.Series) -> dict:
    """Descriptive profile for a single employee."""
    return {
        "name":          row["Name"],
        "dept":          row["Department"],
        "seniority":     row["Seniority_Level"],
        "tenure":        row["Tenure_Years"],
        "archetype":     row["Personality_Archetype"],
        "mbti":          row["MBTI_Type"],
        "ocean": {
            "Openness":          row["Openness"],
            "Conscientiousness": row["Conscientiousness"],
            "Extraversion":      row["Extraversion"],
            "Agreeableness":     row["Agreeableness"],
            "Neuroticism":       row["Neuroticism"],
        },
        "comm_style":    row["Communication_Style"],
        "conflict_style":row["Conflict_Resolution_Style"],
        "work_pace":     row["Work_Pace_Preference"],
        "sync_pref":     row["Sync_Async_Preference"],
        "decision_style":row["Decision_Making_Style"],
        "collab_score":  row["Collaboration_Score"],
        "leadership":    row["Leadership_Potential_Score"],
        "meeting_eff":   row["Meeting_Effectiveness_Score"],
        "stress_risk":   row["Stress_Risk_Level"],
        "friction_risk": row["Friction_Risk"],
        "task_fit":      row["Task_Suitability"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def diagnose_department(df: pd.DataFrame, dept: str) -> list[dict]:
    """
    Returns a list of diagnostic insight dicts for a department.
    Each dict has: {type, title, body, severity}
    severity: 'info' | 'warning' | 'critical'
    """
    d = df[df["Department"] == dept]
    insights = []

    ocean_means = d[OCEAN_COLS].mean()

    # ── Conscientiousness ──────────────────────────────────────────────────
    if ocean_means["Conscientiousness"] >= 72:
        insights.append({
            "type": "diagnostic",
            "title": "High Conscientiousness → Speed Risk",
            "body": (
                f"{dept} scores {ocean_means['Conscientiousness']:.0f}/100 on Conscientiousness — "
                "above the 70 threshold that predicts strong quality focus but potential slowness. "
                "Teams this structured may over-invest in process at the expense of decision speed. "
                "Watch for analysis paralysis in cross-functional projects with fast-moving peers like Sales or Marketing."
            ),
            "severity": "warning",
        })

    # ── Low Conscientiousness ──────────────────────────────────────────────
    if ocean_means["Conscientiousness"] < 55:
        insights.append({
            "type": "diagnostic",
            "title": "Low Conscientiousness → Execution Risk",
            "body": (
                f"{dept} scores {ocean_means['Conscientiousness']:.0f}/100 on Conscientiousness. "
                "Teams below 55 tend to generate ideas and energy but underinvest in follow-through. "
                "Expect missed deadlines or incomplete handoffs when paired with detail-focused teams like Finance or Operations."
            ),
            "severity": "warning",
        })

    # ── High Agreeableness ────────────────────────────────────────────────
    if ocean_means["Agreeableness"] >= 70:
        insights.append({
            "type": "diagnostic",
            "title": "High Agreeableness → Conflict Avoidance Risk",
            "body": (
                f"{dept} scores {ocean_means['Agreeableness']:.0f}/100 on Agreeableness. "
                "While this drives strong relationships and harmony, it can suppress critical feedback. "
                "High-agreeableness teams often let problems fester rather than surface them directly — "
                "particularly risky in performance conversations, project retrospectives, and vendor negotiations."
            ),
            "severity": "warning",
        })

    # ── Low Extraversion ─────────────────────────────────────────────────
    if ocean_means["Extraversion"] < 45:
        insights.append({
            "type": "diagnostic",
            "title": "Low Extraversion → Meeting Friction Risk",
            "body": (
                f"{dept} has a mean Extraversion of {ocean_means['Extraversion']:.0f}/100. "
                "This team is likely to under-contribute in verbal, meeting-heavy formats — "
                "particularly when paired with high-E teams like Sales or HR who dominate conversations. "
                "Diagnostic: ideas and concerns may go unvoiced in unstructured settings."
            ),
            "severity": "info",
        })

    # ── High Neuroticism ─────────────────────────────────────────────────
    if ocean_means["Neuroticism"] >= 55:
        insights.append({
            "type": "diagnostic",
            "title": "Elevated Neuroticism → Stress Sensitivity",
            "body": (
                f"{dept} averages {ocean_means['Neuroticism']:.0f}/100 on Neuroticism (emotional reactivity). "
                "This predicts higher sensitivity to pressure, change, and ambiguity. "
                "Under workload spikes or organisational change, this team may show higher burnout signals. "
                "Check Stress Risk distribution — elevated Neuroticism + Avoidant conflict style is the highest-risk combination."
            ),
            "severity": "warning",
        })

    # ── Avoidant conflict style ───────────────────────────────────────────
    avoidant_pct = (d["Conflict_Resolution_Style"] == "Avoidant").mean() * 100
    if avoidant_pct >= 35:
        insights.append({
            "type": "diagnostic",
            "title": f"High Conflict Avoidance ({avoidant_pct:.0f}% of team)",
            "body": (
                f"{avoidant_pct:.0f}% of {dept} defaults to Avoidant conflict resolution. "
                "This is the style most associated with stress accumulation, passive disagreement, and "
                "unresolved tension. In cross-functional settings, avoidant team members often appear to agree "
                "in meetings but disengage or escalate quietly afterward. "
                "Prescriptive: introduce structured retrospectives and anonymous feedback mechanisms."
            ),
            "severity": "critical" if avoidant_pct >= 45 else "warning",
        })

    # ── Competitive conflict style ────────────────────────────────────────
    competitive_pct = (d["Conflict_Resolution_Style"] == "Competitive").mean() * 100
    if competitive_pct >= 30:
        insights.append({
            "type": "diagnostic",
            "title": f"High Competitive Conflict Style ({competitive_pct:.0f}%)",
            "body": (
                f"{competitive_pct:.0f}% of {dept} uses a Competitive conflict resolution style. "
                "This drives urgency and results but creates friction with Diplomatic or Avoidant teams. "
                "Pairing this department with HR or Finance on collaborative projects may surface "
                "power dynamics that need explicit facilitation."
            ),
            "severity": "warning",
        })

    # ── Pace vs Decision mismatch ─────────────────────────────────────────
    structured_pct   = (d["Work_Pace_Preference"] == "Structured").mean() * 100
    intuitive_pct    = (d["Decision_Making_Style"] == "Intuitive").mean() * 100
    if structured_pct >= 60 and intuitive_pct >= 50:
        insights.append({
            "type": "diagnostic",
            "title": "Internal Pace–Decision Mismatch",
            "body": (
                f"{dept} has {structured_pct:.0f}% preferring Structured pace AND {intuitive_pct:.0f}% "
                "making Intuitive decisions. This internal tension — wanting structured processes but deciding "
                "by gut — can create inconsistency. Some members will feel decisions are made too fast; "
                "others will find process requirements burdensome. Clarity on decision rights and protocols is key."
            ),
            "severity": "info",
        })

    # ── Async heavy ──────────────────────────────────────────────────────
    async_pct = (d["Sync_Async_Preference"] == "Async (Written)").mean() * 100
    if async_pct >= 65:
        insights.append({
            "type": "diagnostic",
            "title": f"Strong Async Preference ({async_pct:.0f}%)",
            "body": (
                f"{dept} is predominantly async-preferring ({async_pct:.0f}%). "
                "This is efficient within the team but will create channel friction when collaborating with "
                "sync-heavy teams like Sales or HR. Meetings called without written pre-reads will consistently "
                "under-engage this team. Diagnostic: meeting fatigue complaints often trace back to this mismatch."
            ),
            "severity": "info",
        })

    # ── High friction risk employees ─────────────────────────────────────
    high_friction_n = (d["Friction_Risk"] == "High").sum()
    if high_friction_n >= 3:
        insights.append({
            "type": "diagnostic",
            "title": f"{high_friction_n} Employees Flagged as High Friction Risk",
            "body": (
                f"{high_friction_n} employees in {dept} carry a High Friction Risk profile — "
                "typically a combination of Competitive conflict style, Intuitive decision-making, "
                "and Structured pace preference. These individuals are valuable drivers in the right context "
                "but may create interpersonal friction in collaborative settings without clear role boundaries."
            ),
            "severity": "warning",
        })

    if not insights:
        insights.append({
            "type": "diagnostic",
            "title": "No Major Risk Patterns Detected",
            "body": f"{dept} shows a balanced personality profile with no acute friction or stress signals.",
            "severity": "info",
        })

    return insights


def diagnose_cross_functional_pair(df: pd.DataFrame, dept1: str, dept2: str) -> list[dict]:
    """
    Diagnose friction between two specific departments.
    """
    d1 = df[df["Department"] == dept1]
    d2 = df[df["Department"] == dept2]
    insights = []

    # OCEAN gap analysis
    o1 = d1[OCEAN_COLS].mean()
    o2 = d2[OCEAN_COLS].mean()
    gaps = (o1 - o2).abs().sort_values(ascending=False)
    biggest_gap_trait = gaps.idxmax()
    biggest_gap_val   = gaps.iloc[0]

    if biggest_gap_val >= 20:
        insights.append({
            "type": "diagnostic",
            "title": f"Large {biggest_gap_trait} Gap ({biggest_gap_val:.0f} pts)",
            "body": (
                f"{dept1} and {dept2} differ by {biggest_gap_val:.0f} points on {biggest_gap_trait}. "
                f"{dept1} scores {o1[biggest_gap_trait]:.0f} vs {dept2} at {o2[biggest_gap_trait]:.0f}. "
                "This is the primary personality driver of friction between these teams."
            ),
            "severity": "warning",
        })

    # Pace mismatch
    p1_structured = (d1["Work_Pace_Preference"] == "Structured").mean()
    p2_structured = (d2["Work_Pace_Preference"] == "Structured").mean()
    if abs(p1_structured - p2_structured) >= 0.35:
        fast = dept1 if p1_structured < p2_structured else dept2
        slow = dept2 if fast == dept1 else dept1
        insights.append({
            "type": "diagnostic",
            "title": "Pace Mismatch — Speed vs Process",
            "body": (
                f"{fast} is predominantly Flexible/fast-moving while {slow} is predominantly Structured. "
                "This is one of the most common sources of inter-team frustration. "
                f"{fast} will feel blocked by {slow}'s approval/review cycles; "
                f"{slow} will feel {fast} bypasses necessary quality gates."
            ),
            "severity": "warning",
        })

    # Sync preference mismatch
    s1_sync = (d1["Sync_Async_Preference"] == "Sync (Meetings)").mean()
    s2_sync = (d2["Sync_Async_Preference"] == "Sync (Meetings)").mean()
    if abs(s1_sync - s2_sync) >= 0.35:
        sync_team  = dept1 if s1_sync > s2_sync else dept2
        async_team = dept2 if sync_team == dept1 else dept1
        insights.append({
            "type": "diagnostic",
            "title": "Channel Preference Mismatch",
            "body": (
                f"{sync_team} prefers synchronous meetings while {async_team} prefers written async. "
                "Meetings called by {sync_team} will frustrate {async_team} members who prefer written briefs first. "
                "Recommended norm: 24-hour pre-read requirement before any cross-team meeting."
            ),
            "severity": "info",
        })

    return insights if insights else [{
        "type": "diagnostic",
        "title": "Low Friction Pair",
        "body": f"{dept1} and {dept2} show relatively compatible working styles.",
        "severity": "info",
    }]


# ─────────────────────────────────────────────────────────────────────────────
# PREDICTIVE ANALYSIS (stubs — expandable)
# ─────────────────────────────────────────────────────────────────────────────

def predict_burnout_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag employees at elevated burnout risk based on profile combination.
    Returns DataFrame with risk flags.
    """
    risk_df = df.copy()
    risk_df["Burnout_Risk_Score"] = (
        risk_df["Neuroticism"] * 0.4
        + (risk_df["Conflict_Resolution_Style"] == "Avoidant").astype(int) * 15
        - risk_df["Emotional_Stability"] * 0.2
        - risk_df["Extraversion"] * 0.1
    ).round(1)
    risk_df["Burnout_Risk_Flag"] = risk_df["Burnout_Risk_Score"].apply(
        lambda x: "High" if x > 30 else "Medium" if x > 15 else "Low"
    )
    return risk_df[["Employee_ID", "Name", "Department", "Burnout_Risk_Score", "Burnout_Risk_Flag"]]


def predict_collab_success(df: pd.DataFrame, emp_id1: str, emp_id2: str) -> dict:
    """
    Predict collaboration compatibility between two employees.
    """
    e1 = df[df["Employee_ID"] == emp_id1]
    e2 = df[df["Employee_ID"] == emp_id2]
    if e1.empty or e2.empty:
        return {"score": None, "notes": "Employee not found"}

    e1, e2 = e1.iloc[0], e2.iloc[0]
    ocean_distance = np.sqrt(sum((e1[c] - e2[c]) ** 2 for c in OCEAN_COLS))
    compat_score   = max(1, round(10 - ocean_distance / 20, 1))

    notes = []
    if e1["Sync_Async_Preference"] != e2["Sync_Async_Preference"]:
        notes.append("Channel preference mismatch — agree on communication format upfront.")
    if e1["Decision_Making_Style"] != e2["Decision_Making_Style"]:
        notes.append("Different decision styles — one data-driven, one intuitive. Define decision criteria early.")
    if e1["Work_Pace_Preference"] != e2["Work_Pace_Preference"]:
        notes.append("Pace mismatch — set explicit deadlines and milestone agreements.")

    return {
        "employee_1":   e1["Name"],
        "employee_2":   e2["Name"],
        "compat_score": compat_score,
        "notes":        notes,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PRESCRIPTIVE ANALYSIS (stubs — expandable)
# ─────────────────────────────────────────────────────────────────────────────

def prescribe_team_norms(dept_insights: list[dict]) -> list[str]:
    """
    Given diagnostic insights, return a list of norm recommendations.
    """
    norms = []
    severities = [i["severity"] for i in dept_insights]
    titles     = [i["title"] for i in dept_insights]

    if any("Avoidant" in t for t in titles):
        norms.append("🔄 Introduce structured retrospectives with anonymous input channels (e.g., Retrium, EasyRetro).")
        norms.append("📋 Add a standing agenda item: 'What are we not saying?' in team meetings.")

    if any("Async" in t for t in titles):
        norms.append("📝 Mandate 24-hour written pre-reads before all cross-functional meetings.")
        norms.append("✅ Establish async-first default: use written Slack/Teams threads before scheduling calls.")

    if any("Pace" in t for t in titles):
        norms.append("⏱️ Agree on a Decision Turnaround SLA: e.g., decisions required within 48 hours unless flagged.")
        norms.append("🚦 Use a traffic-light system for urgency classification on all requests (Green / Amber / Red).")

    if any("Friction Risk" in t for t in titles):
        norms.append("🤝 Assign a rotating 'friction monitor' role in cross-functional projects.")
        norms.append("📊 Use pre-mortem exercises before major projects to surface conflict proactively.")

    if any("Conscientiousness" in t and "Speed" in t for t in titles):
        norms.append("⚡ Set explicit 'good enough' quality thresholds for each deliverable type to prevent over-engineering.")

    if not norms:
        norms.append("✅ Profile appears balanced. Focus on maintaining current communication and decision protocols.")

    return norms


def recommend_task_assignments(df: pd.DataFrame, task_type: str) -> pd.DataFrame:
    """
    Return best-fit employees for a given task type keyword.
    """
    matches = df[df["Task_Suitability"].str.contains(task_type, case=False, na=False)].copy()
    matches = matches.sort_values(
        ["Collaboration_Score", "Leadership_Potential_Score"], ascending=False
    )
    return matches[["Employee_ID", "Name", "Department", "Personality_Archetype",
                     "Seniority_Level", "Collaboration_Score",
                     "Leadership_Potential_Score", "Task_Suitability"]]
