"""
utils/chart_helpers.py
======================
Reusable Plotly chart builder functions used across all dashboard pages.
Dark-mode styled, consistent with config.toml theme.
All functions return plotly.graph_objects.Figure objects.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_loader import (
    DEPT_COLORS, ARCHETYPE_COLORS, COMM_COLORS,
    CONFLICT_COLORS, STRESS_COLORS, FRICTION_COLORS,
    OCEAN_COLS,
)

# ── Shared layout defaults ─────────────────────────────────────────────────────
DARK_BG      = "#0d0f14"
CARD_BG      = "#13151c"
BORDER_COLOR = "#1f2330"
TEXT_COLOR   = "#e8eaf0"
MUTED_COLOR  = "#8892b0"
GRID_COLOR   = "#1f2330"
ACCENT       = "#7c6ff7"

BASE_LAYOUT = dict(
    paper_bgcolor=DARK_BG,
    plot_bgcolor=DARK_BG,
    font=dict(family="Space Grotesk, sans-serif", color=TEXT_COLOR, size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(
        bgcolor=CARD_BG,
        bordercolor=BORDER_COLOR,
        borderwidth=1,
        font=dict(size=11),
    ),
    hoverlabel=dict(
        bgcolor=CARD_BG,
        bordercolor=BORDER_COLOR,
        font_color=TEXT_COLOR,
        font_size=12,
    ),
)


def _apply_base(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01, xanchor="left"),
        height=height,
    )
    return fig


# ── 1. OCEAN Radar Chart ───────────────────────────────────────────────────────

def ocean_radar(data: dict, title: str = "OCEAN Profile") -> go.Figure:
    """
    Radar / spider chart for OCEAN scores.
    data: dict of {label: {O, C, E, A, N}} or single {O, C, E, A, N}
    """
    categories = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
    fig = go.Figure()

    if isinstance(list(data.values())[0], dict):
        items = data.items()
    else:
        items = [("Profile", data)]

    colors = list(DEPT_COLORS.values()) + [ACCENT]

    for i, (label, scores) in enumerate(items):
        vals = [scores.get(c, scores.get(c[:1], 50)) for c in categories]
        vals_closed = vals + [vals[0]]
        cats_closed = categories + [categories[0]]
        color = colors[i % len(colors)]

        fig.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=cats_closed,
            fill="toself",
            opacity=0.3,
            line=dict(color=color, width=2),
            name=label,
            hovertemplate="%{theta}: <b>%{r}</b><extra></extra>",
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=9, color=MUTED_COLOR),
                gridcolor=GRID_COLOR,
                linecolor=GRID_COLOR,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=TEXT_COLOR),
                gridcolor=GRID_COLOR,
                linecolor=GRID_COLOR,
            ),
        ),
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=420,
        showlegend=True,
    )
    return fig


# ── 2. Drilldown Donut Chart ───────────────────────────────────────────────────

def donut_chart(
    series: pd.Series,
    color_map: dict,
    title: str = "",
    hole: float = 0.55,
    height: int = 380,
) -> go.Figure:
    """
    Styled donut chart. Clicking a segment triggers Streamlit session state
    updates when combined with plotly_events or use_container_width.
    """
    counts = series.value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    colors = [color_map.get(l, MUTED_COLOR) for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker=dict(colors=colors, line=dict(color=DARK_BG, width=3)),
        textinfo="label+percent",
        textfont=dict(size=11, color=TEXT_COLOR),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
        pull=[0.04 if i == 0 else 0 for i in range(len(labels))],
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=height,
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5, **{
            k: v for k, v in BASE_LAYOUT["legend"].items()
        }),
        annotations=[dict(
            text=f"<b>{len(series)}</b><br><span style='font-size:10px'>total</span>",
            x=0.5, y=0.5, font=dict(size=18, color=TEXT_COLOR),
            showarrow=False,
        )],
    )
    return fig


# ── 3. OCEAN Heatmap by Department ────────────────────────────────────────────

def ocean_heatmap(dept_ocean_df: pd.DataFrame, title: str = "OCEAN Scores by Department") -> go.Figure:
    """Heatmap with departments on Y axis and OCEAN dimensions on X."""
    df = dept_ocean_df.set_index("Department")[OCEAN_COLS]

    fig = go.Figure(go.Heatmap(
        z=df.values,
        x=OCEAN_COLS,
        y=df.index.tolist(),
        colorscale=[
            [0.0, "#1a1d27"],
            [0.3, "#3d3580"],
            [0.6, "#7c6ff7"],
            [1.0, "#c4b5fd"],
        ],
        zmin=30, zmax=85,
        text=df.values.round(1),
        texttemplate="%{text}",
        textfont=dict(size=12, color=TEXT_COLOR),
        hovertemplate="<b>%{y}</b> — %{x}<br>Score: <b>%{z}</b><extra></extra>",
        showscale=True,
        colorbar=dict(
            thickness=12,
            len=0.8,
            tickfont=dict(color=MUTED_COLOR, size=10),
            bgcolor=CARD_BG,
            bordercolor=BORDER_COLOR,
        ),
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=320,
        xaxis=dict(
            tickfont=dict(size=11, color=TEXT_COLOR),
            side="bottom",
            gridcolor=BORDER_COLOR,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color=TEXT_COLOR),
            gridcolor=BORDER_COLOR,
        ),
    )
    return fig


# ── 4. Grouped Bar — OCEAN by Department ──────────────────────────────────────

def ocean_grouped_bar(dept_ocean_df: pd.DataFrame, title: str = "OCEAN Comparison") -> go.Figure:
    """Grouped bar chart comparing OCEAN dimensions across departments."""
    fig = go.Figure()
    trait_colors = ["#7c6ff7", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]

    for i, trait in enumerate(OCEAN_COLS):
        fig.add_trace(go.Bar(
            name=trait,
            x=dept_ocean_df["Department"],
            y=dept_ocean_df[trait],
            marker_color=trait_colors[i],
            hovertemplate=f"<b>{trait}</b><br>%{{x}}: %{{y:.1f}}<extra></extra>",
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        barmode="group",
        height=400,
        xaxis=dict(tickfont=dict(color=TEXT_COLOR), gridcolor=BORDER_COLOR),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR), gridcolor=GRID_COLOR, range=[0, 100]),
        bargap=0.2,
        bargroupgap=0.05,
    )
    return fig


# ── 5. Sunburst — Dept → Archetype → Comm Style ───────────────────────────────

def sunburst_chart(df: pd.DataFrame, title: str = "Dept → Archetype → Comm Style") -> go.Figure:
    """Three-level sunburst: Department → Personality Archetype → Communication Style."""
    fig = px.sunburst(
        df,
        path=["Department", "Personality_Archetype", "Communication_Style"],
        color="Department",
        color_discrete_map=DEPT_COLORS,
        title=title,
    )
    fig.update_traces(
        textfont=dict(size=11, color=TEXT_COLOR),
        insidetextorientation="radial",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percentParent} of parent<extra></extra>",
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=500,
    )
    return fig


# ── 6. Stacked Bar — Style distributions ──────────────────────────────────────

def stacked_bar(
    df: pd.DataFrame,
    group_col: str,
    stack_col: str,
    color_map: dict,
    title: str = "",
    height: int = 380,
    normalise: bool = True,
) -> go.Figure:
    """Stacked (or 100% stacked) bar chart."""
    pivot = df.groupby([group_col, stack_col], observed=True).size().unstack(fill_value=0)
    if normalise:
        pivot = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig = go.Figure()
    for col in pivot.columns:
        fig.add_trace(go.Bar(
            name=col,
            x=pivot.index.tolist(),
            y=pivot[col].round(1),
            marker_color=color_map.get(col, MUTED_COLOR),
            hovertemplate=f"<b>{col}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>" if normalise
                          else f"<b>{col}</b><br>%{{x}}: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        barmode="stack",
        height=height,
        xaxis=dict(tickfont=dict(color=TEXT_COLOR), gridcolor=BORDER_COLOR),
        yaxis=dict(
            tickfont=dict(color=TEXT_COLOR), gridcolor=GRID_COLOR,
            title="%" if normalise else "Count",
            range=[0, 102] if normalise else None,
        ),
    )
    return fig


# ── 7. Scatter — Collaboration vs Leadership ──────────────────────────────────

def scatter_collab_leadership(df: pd.DataFrame, color_by: str = "Department") -> go.Figure:
    """Scatter plot: Collaboration Score vs Leadership Potential, coloured by dept/archetype."""
    color_map = DEPT_COLORS if color_by == "Department" else ARCHETYPE_COLORS

    fig = px.scatter(
        df,
        x="Collaboration_Score",
        y="Leadership_Potential_Score",
        color=color_by,
        color_discrete_map=color_map,
        size="Tenure_Years",
        size_max=18,
        hover_data=["Name", "Department", "Personality_Archetype", "Seniority_Level"],
        title="Collaboration Score vs Leadership Potential",
    )
    fig.update_traces(
        marker=dict(opacity=0.85, line=dict(width=1, color=DARK_BG)),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[1]} · %{customdata[2]}<br>"
            "Seniority: %{customdata[3]}<br>"
            "Collaboration: %{x}<br>"
            "Leadership: %{y}<extra></extra>"
        ),
    )
    fig.update_layout(
        **BASE_LAYOUT,
        height=450,
        xaxis=dict(title="Collaboration Score", range=[0, 11], gridcolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
        yaxis=dict(title="Leadership Potential", range=[0, 11], gridcolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
    )
    return fig


# ── 8. Friction Heatmap ────────────────────────────────────────────────────────

def friction_heatmap(matrix_df: pd.DataFrame, title: str = "Inter-Department Friction Potential") -> go.Figure:
    """Heatmap of friction scores between department pairs."""
    z = matrix_df.values.astype(float)
    depts = matrix_df.index.tolist()

    fig = go.Figure(go.Heatmap(
        z=z,
        x=depts,
        y=depts,
        colorscale=[
            [0.0, CARD_BG],
            [0.4, "#78350f"],
            [0.7, "#dc2626"],
            [1.0, "#fca5a5"],
        ],
        zmin=0, zmax=z.max(),
        text=z.round(1),
        texttemplate="%{text}",
        textfont=dict(size=11),
        hovertemplate="<b>%{y} ↔ %{x}</b><br>Friction Score: <b>%{z:.2f}</b><extra></extra>",
        showscale=True,
        colorbar=dict(
            thickness=12, len=0.8,
            tickfont=dict(color=MUTED_COLOR, size=10),
            bgcolor=CARD_BG, bordercolor=BORDER_COLOR,
            title=dict(text="Friction", font=dict(color=MUTED_COLOR, size=10)),
        ),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=420,
        xaxis=dict(tickfont=dict(color=TEXT_COLOR, size=11)),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR, size=11), autorange="reversed"),
    )
    return fig


# ── 9. Box plot — OCEAN by Dept ───────────────────────────────────────────────

def ocean_boxplot(df: pd.DataFrame, trait: str = "Openness", title: str = "") -> go.Figure:
    """Box plot of a single OCEAN trait across departments."""
    fig = go.Figure()
    for dept in df["Department"].cat.categories if hasattr(df["Department"], "cat") else df["Department"].unique():
        subset = df[df["Department"] == dept][trait]
        fig.add_trace(go.Box(
            y=subset,
            name=dept,
            marker_color=DEPT_COLORS.get(dept, ACCENT),
            line_color=DEPT_COLORS.get(dept, ACCENT),
            opacity=0.4,
            boxmean="sd",
            hovertemplate=f"<b>{dept}</b><br>{trait}: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title or f"{trait} Distribution by Department", font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=400,
        xaxis=dict(tickfont=dict(color=TEXT_COLOR), gridcolor=BORDER_COLOR),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR), gridcolor=GRID_COLOR, range=[0, 105]),
        showlegend=False,
    )
    return fig


# ── 10. KPI gauge ─────────────────────────────────────────────────────────────

def gauge_chart(value: float, title: str, max_val: float = 10) -> go.Figure:
    """Simple gauge chart for a single score."""
    color = "#10b981" if value >= 7 else "#f59e0b" if value >= 4 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title=dict(text=title, font=dict(color=TEXT_COLOR, size=13)),
        number=dict(font=dict(color=color, size=28)),
        gauge=dict(
            axis=dict(range=[0, max_val], tickfont=dict(color=MUTED_COLOR, size=9)),
            bar=dict(color=color, thickness=0.3),
            bgcolor=CARD_BG,
            borderwidth=1,
            bordercolor=BORDER_COLOR,
            steps=[
                dict(range=[0, max_val * 0.4], color="#1a1d27"),
                dict(range=[max_val * 0.4, max_val * 0.7], color="#252840"),
                dict(range=[max_val * 0.7, max_val], color="#2d3050"),
            ],
            threshold=dict(
                line=dict(color=TEXT_COLOR, width=2),
                thickness=0.75,
                value=value,
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=DARK_BG,
        font=dict(family="Space Grotesk, sans-serif", color=TEXT_COLOR),
        height=220,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


# ── 11. Horizontal bar — Top employees by score ───────────────────────────────

def top_employees_bar(
    df: pd.DataFrame,
    score_col: str,
    title: str = "",
    n: int = 10,
    color_by: str = "Department",
) -> go.Figure:
    """Ranked horizontal bar of top N employees by a given score column."""
    top = df.nlargest(n, score_col)[["Name", "Department", "Personality_Archetype", score_col]]

    colors = [DEPT_COLORS.get(d, ACCENT) for d in top["Department"]]

    fig = go.Figure(go.Bar(
        x=top[score_col],
        y=top["Name"],
        orientation="h",
        marker_color=colors,
        text=top[score_col],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            f"{score_col.replace('_', ' ')}: %{{x}}<extra></extra>"
        ),
        customdata=top[["Department", "Personality_Archetype"]].values,
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title or f"Top {n} by {score_col.replace('_', ' ')}", font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=max(300, n * 38),
        xaxis=dict(range=[0, 11], tickfont=dict(color=TEXT_COLOR), gridcolor=GRID_COLOR),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR, size=11), autorange="reversed"),
        showlegend=False,
    )
    return fig


# ── 12. Treemap — Archetype × Dept ────────────────────────────────────────────

def treemap_archetype_dept(df: pd.DataFrame, title: str = "Archetype Distribution by Department") -> go.Figure:
    """Treemap showing archetype breakdown within each department."""
    fig = px.treemap(
        df,
        path=[px.Constant("Organisation"), "Department", "Personality_Archetype"],
        color="Department",
        color_discrete_map=DEPT_COLORS,
        title=title,
    )
    fig.update_traces(
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
        marker=dict(line=dict(width=2, color=DARK_BG)),
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_COLOR), x=0.01),
        height=480,
    )
    return fig
