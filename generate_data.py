"""
generate_data.py
================
Synthetic Employee Personality Dataset Generator.

Generates 65 realistic employee records across 6 departments with
statistically-biased personality profiles reflecting real occupational patterns.

Run once before launching the dashboard:
    python generate_data.py

Output: data/employees.csv
"""

import pandas as pd
import numpy as np
import random
import os

np.random.seed(42)
random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# DEPARTMENT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

DEPARTMENTS = {
    "Finance": {
        "size": 10,
        "ocean_bias": {
            "O": (40, 12),
            "C": (78, 10),
            "E": (42, 12),
            "A": (58, 10),
            "N": (48, 12),
        },
        "comm_weights":     [0.10, 0.50, 0.30, 0.10],
        "conflict_weights": [0.20, 0.45, 0.15, 0.20],
        "work_pace_weights":[0.70, 0.30],
        "sync_weights":     [0.30, 0.70],
        "decision_weights": [0.75, 0.25],
        "seniority_dist":   [0.20, 0.40, 0.30, 0.10],
    },
    "HR": {
        "size": 7,
        "ocean_bias": {
            "O": (60, 12),
            "C": (65, 10),
            "E": (68, 12),
            "A": (78, 10),
            "N": (50, 12),
        },
        "comm_weights":     [0.10, 0.15, 0.55, 0.20],
        "conflict_weights": [0.40, 0.35, 0.05, 0.20],
        "work_pace_weights":[0.45, 0.55],
        "sync_weights":     [0.65, 0.35],
        "decision_weights": [0.35, 0.65],
        "seniority_dist":   [0.15, 0.35, 0.35, 0.15],
    },
    "Operations": {
        "size": 15,
        "ocean_bias": {
            "O": (38, 10),
            "C": (80, 8),
            "E": (45, 12),
            "A": (60, 10),
            "N": (42, 12),
        },
        "comm_weights":     [0.35, 0.35, 0.20, 0.10],
        "conflict_weights": [0.30, 0.25, 0.25, 0.20],
        "work_pace_weights":[0.80, 0.20],
        "sync_weights":     [0.50, 0.50],
        "decision_weights": [0.70, 0.30],
        "seniority_dist":   [0.25, 0.40, 0.25, 0.10],
    },
    "Marketing": {
        "size": 9,
        "ocean_bias": {
            "O": (80, 10),
            "C": (50, 12),
            "E": (72, 10),
            "A": (62, 10),
            "N": (52, 14),
        },
        "comm_weights":     [0.20, 0.10, 0.25, 0.45],
        "conflict_weights": [0.35, 0.30, 0.15, 0.20],
        "work_pace_weights":[0.25, 0.75],
        "sync_weights":     [0.60, 0.40],
        "decision_weights": [0.25, 0.75],
        "seniority_dist":   [0.20, 0.45, 0.25, 0.10],
    },
    "Sales": {
        "size": 13,
        "ocean_bias": {
            "O": (62, 12),
            "C": (55, 12),
            "E": (80, 8),
            "A": (65, 10),
            "N": (55, 14),
        },
        "comm_weights":     [0.45, 0.10, 0.20, 0.25],
        "conflict_weights": [0.25, 0.20, 0.35, 0.20],
        "work_pace_weights":[0.35, 0.65],
        "sync_weights":     [0.70, 0.30],
        "decision_weights": [0.30, 0.70],
        "seniority_dist":   [0.30, 0.40, 0.20, 0.10],
    },
    "IT": {
        "size": 11,
        "ocean_bias": {
            "O": (65, 12),
            "C": (75, 10),
            "E": (38, 12),
            "A": (52, 10),
            "N": (50, 12),
        },
        "comm_weights":     [0.25, 0.50, 0.15, 0.10],
        "conflict_weights": [0.35, 0.30, 0.20, 0.15],
        "work_pace_weights":[0.65, 0.35],
        "sync_weights":     [0.30, 0.70],
        "decision_weights": [0.80, 0.20],
        "seniority_dist":   [0.20, 0.35, 0.30, 0.15],
    },
}

COMM_STYLES     = ["Direct", "Analytical", "Diplomatic", "Expressive"]
CONFLICT_STYLES = ["Collaborative", "Avoidant", "Competitive", "Compromising"]
WORK_PACE       = ["Structured", "Flexible"]
SYNC_PREF       = ["Sync (Meetings)", "Async (Written)"]
DECISION_STYLE  = ["Data-driven", "Intuitive"]
SENIORITY       = ["Junior", "Mid-level", "Senior", "Lead/Manager"]

# ─────────────────────────────────────────────────────────────────────────────
# DERIVATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def ocean_to_mbti(O, C, E, A, N):
    ei = "E" if E >= 50 else "I"
    sn = "N" if O >= 55 else "S"
    tf = "F" if A >= 55 else "T"
    jp = "J" if C >= 55 else "P"
    return f"{ei}{sn}{tf}{jp}"


def personality_archetype(O, C, E, A, N):
    if C >= 70 and O < 55 and E < 55:
        return "Detail-focused Executor"
    elif E >= 65 and A >= 65:
        return "People-oriented Connector"
    elif O >= 72 and E >= 60:
        return "Idea-driven Innovator"
    elif C >= 68 and E < 50 and O >= 55:
        return "Analytical Specialist"
    elif E >= 68 and C < 58:
        return "Action-oriented Driver"
    elif A >= 70 and E < 60:
        return "Empathetic Supporter"
    else:
        return "Balanced Generalist"


def collaboration_score(archetype, dept):
    base = {
        "Detail-focused Executor":   6,
        "People-oriented Connector": 9,
        "Idea-driven Innovator":     7,
        "Analytical Specialist":     6,
        "Action-oriented Driver":    7,
        "Empathetic Supporter":      8,
        "Balanced Generalist":       7,
    }.get(archetype, 6)
    if dept in ["Sales", "HR"] and archetype in ["People-oriented Connector", "Action-oriented Driver"]:
        base = min(10, base + 1)
    if dept == "IT" and archetype == "Analytical Specialist":
        base = min(10, base + 1)
    if dept == "Operations" and archetype == "Detail-focused Executor":
        base = min(10, base + 1)
    return min(10, max(1, base + np.random.randint(-1, 2)))


def task_suitability(archetype):
    return {
        "Detail-focused Executor":   "Quality Assurance, Compliance, Reporting, Process Documentation",
        "People-oriented Connector": "Stakeholder Management, Client Relations, Mediation, Onboarding",
        "Idea-driven Innovator":     "Ideation, Strategy, Product Development, Campaign Concepting",
        "Analytical Specialist":     "Data Analysis, Risk Assessment, Process Design, Technical Review",
        "Action-oriented Driver":    "Sales, Project Delivery, Crisis Response, Negotiation",
        "Empathetic Supporter":      "Coaching, Conflict Resolution, Culture Building, Wellbeing Programs",
        "Balanced Generalist":       "Cross-functional Projects, Coordination, Facilitation, Change Management",
    }.get(archetype, "General Coordination")


def stress_risk(N, E, conflict_style):
    score = N - (E * 0.25)
    if conflict_style == "Avoidant":
        score += 12
    elif conflict_style == "Competitive":
        score += 5
    if score > 58:
        return "High"
    elif score > 38:
        return "Medium"
    else:
        return "Low"


def meeting_effectiveness(E, comm_style, sync_pref):
    base = 5
    if E >= 65:
        base += 2
    elif E < 40:
        base -= 1
    if comm_style in ["Direct", "Expressive"]:
        base += 1
    if sync_pref == "Sync (Meetings)":
        base += 1
    return min(10, max(1, base + np.random.randint(-1, 2)))


def leadership_potential(E, C, O, seniority):
    raw = (E * 0.35 + C * 0.30 + O * 0.20) / 10
    bonus = {"Junior": 0.0, "Mid-level": 0.8, "Senior": 2.0, "Lead/Manager": 3.2}[seniority]
    return min(10, max(1, round(raw + bonus + np.random.uniform(-0.4, 0.4), 1)))


def friction_risk(comm_style, conflict_style, work_pace, decision_style):
    score = 0
    if decision_style == "Intuitive" and work_pace == "Structured":
        score += 2
    if conflict_style == "Competitive":
        score += 2
    if comm_style == "Direct" and conflict_style == "Avoidant":
        score += 1
    if score >= 4:
        return "High"
    elif score >= 2:
        return "Medium"
    else:
        return "Low"


# ─────────────────────────────────────────────────────────────────────────────
# NAME POOLS
# ─────────────────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery",
    "Quinn", "Drew", "Blake", "Reese", "Cameron", "Skyler", "Peyton", "Hayden",
    "Charlie", "Rowan", "Sage", "River", "Nour", "Priya", "Lena", "Marco",
    "Omar", "Sofia", "Kenji", "Aisha", "Ivan", "Mei", "Raj", "Sara", "Luis",
    "Nina", "Tariq", "Zoe", "Felix", "Nia", "Arjun", "Elif", "Yuki", "Hana",
    "Dmitri", "Amara", "Soren", "Linh", "Tobias", "Chiara", "Emre", "Yara",
    "Finn", "Leila", "Mateo", "Ingrid", "Kofi", "Mila", "Dani", "Sasha", "Cleo",
    "Remy", "Ines", "Thabo", "Vera", "Cyrus", "Naomi", "Leon", "Fatima", "Bram"
]

LAST_NAMES = [
    "Smith", "Patel", "Chen", "Johnson", "Williams", "Brown", "Davis", "Garcia",
    "Martinez", "Lee", "Kim", "Singh", "Kumar", "Ali", "Muller", "Kowalski",
    "Santos", "Nguyen", "Osei", "Tanaka", "Costa", "Benali", "Johansson", "Reyes",
    "Fischer", "Andersen", "Nkosi", "Yamamoto", "Ferreira", "Bakker", "Petrov",
    "Hernandez", "Chowdhury", "Lindqvist", "Diallo", "Rossi", "Vance", "Park",
]

used_names = set()

def gen_name():
    attempts = 0
    while attempts < 1000:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in used_names:
            used_names.add(name)
            return name
        attempts += 1
    return f"Employee {len(used_names) + 1}"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GENERATION LOOP
# ─────────────────────────────────────────────────────────────────────────────

def generate_dataset():
    rows = []
    emp_id = 1001

    for dept, cfg in DEPARTMENTS.items():
        for _ in range(cfg["size"]):
            O = int(np.clip(np.random.normal(*cfg["ocean_bias"]["O"]), 10, 100))
            C = int(np.clip(np.random.normal(*cfg["ocean_bias"]["C"]), 10, 100))
            E = int(np.clip(np.random.normal(*cfg["ocean_bias"]["E"]), 10, 100))
            A = int(np.clip(np.random.normal(*cfg["ocean_bias"]["A"]), 10, 100))
            N = int(np.clip(np.random.normal(*cfg["ocean_bias"]["N"]), 10, 100))

            comm     = np.random.choice(COMM_STYLES,     p=cfg["comm_weights"])
            conflict = np.random.choice(CONFLICT_STYLES, p=cfg["conflict_weights"])
            pace     = np.random.choice(WORK_PACE,       p=cfg["work_pace_weights"])
            sync     = np.random.choice(SYNC_PREF,       p=cfg["sync_weights"])
            decision = np.random.choice(DECISION_STYLE,  p=cfg["decision_weights"])
            seniority= np.random.choice(SENIORITY,       p=cfg["seniority_dist"])

            tenure_ranges = {
                "Junior": (0, 2), "Mid-level": (2, 6),
                "Senior": (5, 12), "Lead/Manager": (7, 18),
            }
            lo, hi = tenure_ranges[seniority]
            tenure = np.random.randint(lo, hi + 1)

            mbti       = ocean_to_mbti(O, C, E, A, N)
            archetype  = personality_archetype(O, C, E, A, N)
            collab     = collaboration_score(archetype, dept)
            task_fit   = task_suitability(archetype)
            stress     = stress_risk(N, E, conflict)
            meet_eff   = meeting_effectiveness(E, comm, sync)
            lead_pot   = leadership_potential(E, C, O, seniority)
            friction   = friction_risk(comm, conflict, pace, decision)
            es         = 100 - N

            rows.append({
                "Employee_ID":                f"EMP{emp_id:04d}",
                "Name":                       gen_name(),
                "Department":                 dept,
                "Seniority_Level":            seniority,
                "Tenure_Years":               tenure,
                "Openness":                   O,
                "Conscientiousness":          C,
                "Extraversion":               E,
                "Agreeableness":              A,
                "Neuroticism":                N,
                "Emotional_Stability":        es,
                "MBTI_Type":                  mbti,
                "Personality_Archetype":      archetype,
                "Communication_Style":        comm,
                "Conflict_Resolution_Style":  conflict,
                "Work_Pace_Preference":       pace,
                "Sync_Async_Preference":      sync,
                "Decision_Making_Style":      decision,
                "Collaboration_Score":        collab,
                "Task_Suitability":           task_fit,
                "Stress_Risk_Level":          stress,
                "Meeting_Effectiveness_Score":meet_eff,
                "Leadership_Potential_Score": lead_pot,
                "Friction_Risk":              friction,
            })
            emp_id += 1

    return pd.DataFrame(rows)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("🔄 Generating synthetic employee personality dataset...")
    df = generate_dataset()
    output_path = "data/employees.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✅ Dataset saved to: {output_path}")
    print(f"   Total employees : {len(df)}")
    print(f"   Departments     : {df['Department'].nunique()}")
    print(f"   Columns         : {len(df.columns)}")
    print("\n📊 Department breakdown:")
    print(df.groupby("Department").size().rename("Count").to_string())
    print("\n🧬 Archetype distribution:")
    print(df["Personality_Archetype"].value_counts().to_string())
    print("\n⚠️  Stress risk distribution:")
    print(df["Stress_Risk_Level"].value_counts().to_string())
    print("\n✅ Done. Run: streamlit run app.py")
