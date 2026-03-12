import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from irt_algorithm import ability_to_score


def learning_curve_chart(sessions: list) -> go.Figure:
    """30-day learning curve line chart"""
    if not sessions:
        fig = go.Figure()
        fig.add_annotation(
            text="No sessions yet — start quizzing!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#64748B", size=14)
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#1E293B",
            height=300
        )
        return fig

    timestamps = [s[3] for s in sessions][::-1]
    scores = [s[1] for s in sessions][::-1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(scores)+1)),
        y=scores,
        mode="lines+markers",
        line=dict(color="#60A5FA", width=3),
        marker=dict(color="#60A5FA", size=8, line=dict(color='white', width=2)),
        fill="tozeroy",
        fillcolor="rgba(96, 165, 250, 0.1)",
        name="Score"
    ))

    fig.update_layout(
        title=dict(text="📈 Learning Curve", font=dict(color="#1E293B")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#1E293B",
        xaxis=dict(
            title="Session",
            gridcolor="#E2E8F0",
            color="#64748B"
        ),
        yaxis=dict(
            title="Score %",
            range=[0, 100],
            gridcolor="#E2E8F0",
            color="#64748B"
        ),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def weak_topics_chart(weak_topics: list) -> go.Figure:
    """Radar chart showing topic strengths"""
    if not weak_topics:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300
        )
        return fig

    topics = [t[0] for t in weak_topics]
    scores = [t[1] for t in weak_topics]

    fig = go.Figure(go.Scatterpolar(
        r=scores,
        theta=topics,
        fill="toself",
        fillcolor="rgba(96, 165, 250, 0.1)",
        line=dict(color="#60A5FA", width=2)
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color="#64748B",
                gridcolor="#E2E8F0"
            ),
            angularaxis=dict(color="#64748B", gridcolor="#E2E8F0")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#1E293B",
        title=dict(text="🎯 Topic Strength Radar", font=dict(color="#1E293B")),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def score_gauge(score: float) -> go.Figure:
    """Gauge chart for current score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Current Score", "font": {"color": "#1E293B", "size": 18}},
        number={"suffix": "%", "font": {"color": "#3B82F6", "size": 32, "family": "DM Mono"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#64748B"},
            "bar":  {"color": "#60A5FA"},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#E2E8F0",
            "steps": [
                {"range": [0, 40],   "color": "#FEE2E2"},
                {"range": [40, 70],  "color": "#FEF3C7"},
                {"range": [70, 100], "color": "#DCFCE7"},
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#1E293B",
        height=250,
        margin=dict(l=25, r=25, t=50, b=25)
    )
    return fig
