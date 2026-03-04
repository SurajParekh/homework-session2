# 🧠 Personality Intelligence Dashboard
> Understand how your teams are structured, how people communicate, and who is best suited to what — across every department.

---

## 📌 Overview

This dashboard transforms employee personality assessment data into **actionable team intelligence**. Built for SME organisations, it helps HR leaders, team managers, and operations leads answer:

- What personality archetypes dominate each department?
- Where are the friction points between teams?
- Which employees are best suited to cross-functional collaboration?
- How should we structure meetings, decisions, and conflict protocols?

The analysis is grounded in the **Big Five (OCEAN)** personality model, enriched with:
- Communication style preferences (Direct, Analytical, Diplomatic, Expressive)
- Conflict resolution styles (Collaborative, Avoidant, Competitive, Compromising)
- Work style preferences (Structured vs Flexible, Sync vs Async, Data-driven vs Intuitive)

---

## 🗂️ Project Structure

```
personality_dashboard/
│
├── app.py                          # Main Streamlit entry point
├── generate_data.py                # Synthetic data generator (run once)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git exclusions
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
│
├── data/
│   └── employees.csv               # Generated dataset (65 records)
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── chart_helpers.py
│   └── analysis_engine.py
│
└── pages/
    ├── 01_org_overview.py
    ├── 02_department_deep_dive.py
    ├── 03_employee_profiles.py
    ├── 04_cross_functional.py
    └── 05_task_alignment.py
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/personality_dashboard.git
cd personality_dashboard
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate the Synthetic Dataset
```bash
python generate_data.py
```
> ⚠️ Run this before launching. Creates `data/employees.csv`.

### 5. Launch the Dashboard
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Set repo, branch (`main`), main file = `app.py`
5. Click **Deploy**

> Commit `data/employees.csv` to the repo — auto-generation is handled in `app.py` if the file is missing.

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| **Org Overview** | OCEAN heatmap, archetype distribution, org-wide patterns |
| **Department Deep Dive** | Per-dept radar, drilldown donuts, diagnostic callouts |
| **Employee Profiles** | Individual radar charts, personality cards, task fit |
| **Cross-Functional Map** | Inter-team friction matrix, collaboration heatmap |
| **Task Alignment** | Best-fit employees per task; archetype × seniority grid |

---

## 🔬 Analysis Framework

| Type | Focus |
|------|-------|
| **Descriptive** | What does the data show? |
| **Diagnostic** | Why does this pattern exist? |
| **Predictive** | What is likely to happen? |
| **Prescriptive** | What should we do? |

> Current emphasis: **Descriptive + Diagnostic**

---

## 🧬 Dataset Columns

| Column | Type | Description |
|--------|------|-------------|
| Employee_ID | ID | Unique identifier |
| Name | String | Synthetic name |
| Department | Categorical | Finance, HR, Operations, Marketing, Sales, IT |
| Seniority_Level | Ordinal | Junior → Lead/Manager |
| Tenure_Years | Integer | Years at company |
| Openness | Score 0–100 | Curiosity, creativity |
| Conscientiousness | Score 0–100 | Organisation, discipline |
| Extraversion | Score 0–100 | Social energy, assertiveness |
| Agreeableness | Score 0–100 | Cooperativeness, empathy |
| Neuroticism | Score 0–100 | Emotional reactivity |
| Emotional_Stability | Score 0–100 | 100 − Neuroticism |
| MBTI_Type | Categorical | Derived 4-letter approximation |
| Personality_Archetype | Categorical | 7 team archetypes |
| Communication_Style | Categorical | Direct / Analytical / Diplomatic / Expressive |
| Conflict_Resolution_Style | Categorical | Collaborative / Avoidant / Competitive / Compromising |
| Work_Pace_Preference | Categorical | Structured / Flexible |
| Sync_Async_Preference | Categorical | Sync / Async |
| Decision_Making_Style | Categorical | Data-driven / Intuitive |
| Collaboration_Score | Score 1–10 | Cross-functional effectiveness |
| Task_Suitability | String | Best-fit task categories |
| Stress_Risk_Level | Categorical | Low / Medium / High |
| Meeting_Effectiveness_Score | Score 1–10 | Sync meeting effectiveness |
| Leadership_Potential_Score | Score 1–10 | Leadership readiness |
| Friction_Risk | Categorical | Low / Medium / High inter-team friction potential |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Dashboard framework |
| Plotly | Interactive charts with drilldown |
| Pandas | Data manipulation |
| NumPy | Numerical generation |

---

## 📝 Notes

- All data is **synthetic** — for demonstration only
- MBTI types are approximated from OCEAN and not validated assessments
- Not intended for hiring or HR decisions — supports team conversations only

---

## 📄 License
MIT — free to use and adapt with attribution.
