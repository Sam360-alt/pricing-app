import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")
if st.button("←"):
    st.switch_page("pages/1_Pricer.py")


if "sampled_paths" not in st.session_state:
    st.warning("No path data available. Please run a barrier product first.")
    st.stop()

sampled_paths = st.session_state["sampled_paths"]
barrier = st.session_state.get("barrier")
spot = st.session_state.get("initial_spot")
maturity = st.session_state.get("maturity")
n_scenarios = st.session_state.get("n_scenarios", 10000)

fig = go.Figure()

# nicer multicolor palette
palette = [
    "#00c853", "#ff9100", "#00b8d4", "#d500f9", "#ffd600",
    "#ff1744", "#64dd17", "#2979ff", "#ff6d00", "#aa00ff"
]

path_cols = [col for col in sampled_paths.columns if col != "Barrier"]

for i, col in enumerate(path_cols):
    fig.add_trace(go.Scatter(
        x=sampled_paths.index,
        y=sampled_paths[col],
        mode="lines",
        line=dict(
            width=1.2,
            color=palette[i % len(palette)]
        ),
        opacity=0.35,
        hoverinfo="skip",
        showlegend=False
    ))

# Barrier line
fig.add_trace(go.Scatter(
    x=sampled_paths.index,
    y=sampled_paths["Barrier"],
    mode="lines",
    line=dict(
        color="red",
        width=3,
        dash="dash"
    ),
    name="Barrier",
    showlegend=True
))

# Barrier text annotation on the left
fig.add_annotation(
    x=0.03,
    y=barrier + 8,
    xref="paper",
    yref="y",
    text=f"<b>BARRIER = {barrier:.2f}</b>",
    showarrow=False,
    font=dict(color="red", size=14),
    bgcolor="rgba(0,0,0,0.45)"
)

# Small info box in top-left
fig.add_annotation(
    x=0.01,
    y=0.98,
    xref="paper",
    yref="paper",
    xanchor="left",
    yanchor="top",
    align="left",
    showarrow=False,
    text=(
        f"Spot (S₀): {spot:.2f}<br>"
        f"Barrier: {barrier:.2f}<br>"
        f"Maturity: {maturity:.2f} years<br>"
        f"Paths shown: {len(path_cols)} / {n_scenarios:,}"
    ),
    font=dict(size=12, color="white"),
    bgcolor="rgba(20, 30, 50, 0.75)",
    bordercolor="rgba(255,255,255,0.20)",
    borderwidth=1,
    borderpad=12
)

fig.update_layout(
    template="plotly_dark",
    title=dict(
        text="Monte Carlo Paths with Barrier",
        x=0.02
    ),
    legend=dict(
        x=0.98,
        y=0.98,
        xanchor="right",
        yanchor="top",
        bgcolor="rgba(0,0,0,0.30)",
        bordercolor="rgba(255,255,255,0.20)",
        borderwidth=1,
        font=dict(size=12)
    ),
    xaxis=dict(
        title="Time (years)",
        showgrid=True,
        gridcolor="rgba(255,255,255,0.12)"
    ),
    yaxis=dict(
        title="Price",
        showgrid=True,
        gridcolor="rgba(255,255,255,0.12)"
    ),
    margin=dict(l=40, r=40, t=70, b=40),
    height=700
)

st.plotly_chart(fig, use_container_width=True)