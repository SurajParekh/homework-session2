"""
utils/data_loader.py
====================
Cached data loading, preprocessing, and helper accessors.
All functions are decorated with @st.cache_data so the CSV is
read only once per session regardless of how many pages call them.
"""

import streamlit as st
import pandas as pd
import numpy as np

DATA_PATH = "data/employees.csv"

# ── Ordered categories for consistent sorting ──────────────────────────────────
SENIORITY_ORDER  = ["Junior", "Mid-level", "Senior", "Lead/Manager"]
STRESS_ORDER     = ["Low", "Medium", "High"]
FRICTION_ORDER   = ["Low", "Medium", "High"]
DEPT_ORDER       = ["Finance", "HR", "Operations", "Marketing", "Sales", "IT"]

OCEAN_COLS       = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
SCORE_COLS       = ["Collaboration_Score", "Meeting_Effectiveness_Score", "Leadership_Potential_Score", "Emotional_Stability"]
CATEGORICAL_COLS = [
    "Department", "Seniority_Level", "MBTI_Type", "Personality_Archetype",
    "Communication_Style", "Conflict_Resolution_Style",
    "Work_Pace_Preference", "Sync_Async_Preference",
    "Decision_Making_Style", "Stress_Risk_Level", "Friction_Risk",
]

# ── Department colour palette ──────────────────────────────────────────────────
DEPT_COLORS = {
    "Finance":    "#7c6ff7",
    "HR":         "#06b6d4",
    "Operations": "#10b981",
    "Marketing":  "#f59e0b",
    "Sales":      "#ef4444",
    "IT":         "#8b5cf6",
}

ARCHETYPE_COLORS = {
    "Detail-focused Executor":   "#7c6ff7",
    "People-oriented Connector": "#06b6d4",
    "Idea-driven Innovator":     "#f59e0b",
    "Analytical Specialist":     "#10b981",
    "Action-oriented Driver":    "#ef4444",
    "Empathetic Supporter":      "#ec4899",
    "Balanced Generalist":       "#94a3b8",
}

COMM_COLORS = {
    "Direct":     "#ef4444",
    "Analytical": "#7c6ff7",
    "Diplomatic": "#06b6d4",
    "Expressive": "#f59e0b",
}

CONFLICT_COLORS = {
    "Collaborative": "#10b981",
    "Avoidant":      "#94a3b8",
    "Competitive":   "#ef4444",
    "Compromising":  "#f59e0b",
}

STRESS_COLORS = {
    "Low":    "#10b981",
    "Medium": "#f59e0b",
    "High":   "#ef4444",
}

FRICTION_COLORS = {
    "Low":    "#10b981",
    "Medium": "#f59e0b",
    "High":   "#ef4444",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and preprocess the employee dataset. Cached per session."""
    df = pd.read_csv(DATA_PATH)

    # Enforce ordered categoricals
    df["Seniority_Level"] = pd.Categorical(df["Seniority_Level"], categories=SENIORITY_ORDER, ordered=True)
    df["Stress_Risk_Level"] = pd.Categorical(df["Stress_Risk_Level"], categories=STRESS_ORDER, ordered=True)
    df["Friction_Risk"] = pd.Categorical(df["Friction_Risk"], categories=FRICTION_ORDER, ordered=True)
    df["Department"] = pd.Categorical(df["Department"], categories=DEPT_ORDER, ordered=False)

    return df


@st.cache_data
def dept_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-department aggregated stats."""
    agg = df.groupby("Department", observed=True).agg(
        Headcount=("Employee_ID", "count"),
        Avg_Openness=("Openness", "mean"),
        Avg_Conscientiousness=("Conscientiousness", "mean"),
        Avg_Extraversion=("Extraversion", "mean"),
        Avg_Agreeableness=("Agreeableness", "mean"),
        Avg_Neuroticism=("Neuroticism", "mean"),
        Avg_Emotional_Stability=("Emotional_Stability", "mean"),
        Avg_Collaboration=("Collaboration_Score", "mean"),
        Avg_Leadership=("Leadership_Potential_Score", "mean"),
        Avg_Meeting_Effectiveness=("Meeting_Effectiveness_Score", "mean"),
        High_Stress_Pct=("Stress_Risk_Level", lambda x: (x == "High").mean() * 100),
        High_Friction_Pct=("Friction_Risk", lambda x: (x == "High").mean() * 100),
    ).reset_index()

    for col in agg.select_dtypes(include="float").columns:
        agg[col] = agg[col].round(1)

    return agg


@st.cache_data
def ocean_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return OCEAN means per department, shaped for heatmap."""
    return df.groupby("Department", observed=True)[OCEAN_COLS].mean().round(1).reset_index()


@st.cache_data
def archetype_counts(df: pd.DataFrame, dept: str = None) -> pd.DataFrame:
    """Return archetype value counts, optionally filtered by department."""
    subset = df if dept is None else df[df["Department"] == dept]
    return subset["Personality_Archetype"].value_counts().reset_index().rename(
        columns={"index": "Personality_Archetype", "count": "Count",
                 "Personality_Archetype": "Personality_Archetype"}
    )


@st.cache_data
def friction_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a department × department friction potential matrix.
    Score = average absolute difference in OCEAN means between dept pairs,
    normalised 0–10. Higher = more potential for communication friction.
    """
    dept_means = df.groupby("Department", observed=True)[OCEAN_COLS].mean()
    depts = dept_means.index.tolist()
    matrix = pd.DataFrame(index=depts, columns=depts, dtype=float)

    for d1 in depts:
        for d2 in depts:
            if d1 == d2:
                matrix.loc[d1, d2] = 0.0
            else:
                diff = np.abs(dept_means.loc[d1] - dept_means.loc[d2]).mean()
                matrix.loc[d1, d2] = round(diff / 10, 2)  # normalise

    return matrix


def filter_df(df: pd.DataFrame, dept: str = "All Departments") -> pd.DataFrame:
    """Return filtered dataframe. Passthrough if 'All Departments'."""
    if dept == "All Departments" or dept is None:
        return df
    return df[df["Department"] == dept].copy()


def get_employee(df: pd.DataFrame, emp_id: str) -> pd.Series:
    """Return single employee row as a Series."""
    rows = df[df["Employee_ID"] == emp_id]
    if rows.empty:
        return None
    return rows.iloc[0]


def score_color(score: float, low: float = 4, high: float = 7) -> str:
    """Return a hex color for a 1–10 score (red → amber → green)."""
    if score >= high:
        return "#10b981"
    elif score >= low:
        return "#f59e0b"
    else:
        return "#ef4444"
