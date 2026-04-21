import streamlit as st
import numpy as np
from app_project import GBM
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="P&L", layout="wide")
if st.button("←"):
    st.switch_page("pages/1_Pricer.py")

col1,_,col2 = st.columns([6,1,1])
with col1:

    st.subheader("Spot and Volatility Overview")
with col2:
    @st.dialog("Quick Info")
    def show_quick_info():
        st.markdown("""
    **The P&L measures how the value of the position changes under a new market scenario.**

    For a trader **short the product**, the P&L is computed as:
    `P&L = Initial Price - New Price`


    ---

    **Delta-hedged P&L**

    To isolate the effect of non-directional risks, a Delta hedge can be applied.

    Delta measures the sensitivity of the product price to the underlying. By taking an opposite position in the underlying, the trader neutralizes the first-order impact of spot movements.

    The Delta-hedged P&L is approximated by:
    `P&L_hedged = (Initial Price - New Price) - Delta × (New Spot - Initial Spot)`

    This removes the main directional exposure and highlights the impact of other risk factors such as volatility (Vega) and curvature (Gamma).

    ---

    Even after hedging, the P&L is not zero because:
    - the hedge is only first-order (Gamma effects remain)  
    - volatility changes affect the price (Vega)  
    - the model is non-linear, especially for path-dependent products  

    This explains why the Delta-hedged P&L can still be positive or negative.
    """)
    
    if st.button("ℹ️ Info"):
        show_quick_info()


default_spot = st.session_state.get("spot_est", 100.0)
default_vol = st.session_state.get("vol_est", 0.20)
st.write(f'{default_spot:.4f}')
st.write(f'{default_vol:.4f}')

product = st.session_state.get("selected_product")
product_kwargs = st.session_state.get("product_kwargs")
initial_price = st.session_state.get("initial_price")
initial_spot = st.session_state.get("initial_spot")
greeks = st.session_state.get('greeks')
st.write(f"Selected product: {product}")


if st.button("Compute PnL Matrix"):

    spot_shocks = np.array([-0.15, -0.10, -0.05, 0.00, 0.05, 0.10, 0.15])
    vol_shocks  = np.array([-0.10, -0.05,  0.00, 0.05, 0.10])

    base_spot = initial_spot
    base_vol = st.session_state.get("vol_est", default_vol)

    pnl_matrix = np.zeros((len(vol_shocks), len(spot_shocks)))

    n_steps = int(st.session_state.get("maturity") * 252)
    z = np.random.normal(size=(n_steps, 10000))

    for i, vol_shift in enumerate(vol_shocks):
        for j, spot_shift in enumerate(spot_shocks):

            shocked_spot = base_spot * (1 + spot_shift)
            shocked_vol = max(1e-6, base_vol * (1 + vol_shift))

            model = GBM(
                maturity=st.session_state.get("maturity"),
                n_scenarios=10000,
                risk_free=st.session_state.get("riskfree_est"),
                sigma=shocked_vol,
                steps_per_year=252,
                s_0=shocked_spot
            )

            new_price = model.price_product(product, z=z, **product_kwargs)
            pnl_matrix[i, j] = initial_price - new_price

    # Labels
    x_labels = [f"{s:+.0%}\nS={base_spot*(1+s):.2f}" for s in spot_shocks]
    y_labels = [f"{v:+.0%}\nσ={base_vol*(1+v):.2%}" for v in vol_shocks]

    st.session_state["pnl_matrix"] = pnl_matrix
    st.session_state["pnl_x_labels"] = x_labels
    st.session_state["pnl_y_labels"] = y_labels

    

    spot_shocks = np.array([-0.15, -0.10, -0.05, 0.00, 0.05, 0.10, 0.15])
    vol_shocks  = np.array([-0.10, -0.05,  0.00, 0.05, 0.10])


    base_spot = st.session_state["initial_spot"]
    base_vol = st.session_state["initial_sigma"]
    base_risk_free = st.session_state["risk_free"]
    delta = greeks["Delta"]

    dhedge_matrix = np.zeros((len(vol_shocks), len(spot_shocks)))

    n_steps = int(st.session_state.get("maturity") * 252)
    z = np.random.normal(size=(n_steps, 10000))

    for i, vol_shift in enumerate(vol_shocks):
        for j, spot_shift in enumerate(spot_shocks):

            shocked_spot = base_spot * (1 + spot_shift)
            shocked_vol = max(1e-6, base_vol * (1 + vol_shift))

            model = GBM(
                maturity=st.session_state.get("maturity"),
                n_scenarios=10000,
                risk_free=base_risk_free,
                sigma=shocked_vol,
                steps_per_year=252,
                s_0=shocked_spot
            )

            new_price = model.price_product(product, z=z, **product_kwargs)

            dhedge_pnl = (
                initial_price
                - new_price
                - delta * (shocked_spot - base_spot)
            )

            dhedge_matrix[i, j] = dhedge_pnl

    x_labels = [f"{s:+.0%} S={base_spot*(1+s):.2f}" for s in spot_shocks]
    y_labels = [f"{v:+.0%} σ={base_vol*(1+v):.2%}" for v in vol_shocks]

    st.session_state["dhedge_matrix"] = dhedge_matrix
    st.session_state["dhedge_x_labels"] = x_labels
    st.session_state["dhedge_y_labels"] = y_labels
    









if "pnl_matrix" in st.session_state:
    pnl_matrix = st.session_state["pnl_matrix"]
    x_labels = st.session_state["pnl_x_labels"]
    y_labels = st.session_state["pnl_y_labels"]

    text_values = [[f"{val:.2f}" for val in row] for row in pnl_matrix]

    fig = go.Figure(
        data=go.Heatmap(
            z=pnl_matrix,
            x=x_labels,
            y=y_labels,
            text=text_values,
            texttemplate="%{text}",
            colorscale=[
                [0.0, "#ff4d4d"],
                [0.5, "#fff176"],
                [1.0, "#2e8b57"]
            ],
            zmid=0,
            colorbar=dict(title="PnL"),
            hovertemplate=(
                "Spot shock: %{x}<br>"
                "Vol shock: %{y}<br>"
                "PnL: %{z:.2f}<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=dict(
            text="PnL Matrix<br>",
            x=0.02
        ),
        xaxis=dict(title="Spot Shocks", side="top"),
        yaxis=dict(title="Volatility Shocks", autorange="reversed"),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)


if "dhedge_matrix" in st.session_state:
    dhedge_matrix = st.session_state["dhedge_matrix"]
    x_labels = st.session_state["dhedge_x_labels"]
    y_labels = st.session_state["dhedge_y_labels"]

    text_values = [[f"{val:.2f}" for val in row] for row in dhedge_matrix]

    fighedge = go.Figure(
        data=go.Heatmap(
            z=dhedge_matrix,
            x=x_labels,
            y=y_labels,
            text=text_values,
            texttemplate="%{text}",
            colorscale=[
                [0.0, "#ff4d4d"],
                [0.5, "#fff176"],
                [1.0, "#2e8b57"]
            ],
            zmid=0,
            colorbar=dict(title="PnL"),
            hovertemplate=(
                "Spot shock: %{x}<br>"
                "Vol shock: %{y}<br>"
                "Delta-Hedged PnL: %{z:.2f}<extra></extra>"
            )
        )
    )

    fighedge.update_layout(
        title=dict(
            text="Delta-hedged PnL Matrix<br>",
            x=0.02
        ),
        xaxis=dict(title="Spot Shocks", side="top"),
        yaxis=dict(title="Volatility Shocks", autorange="reversed"),
        height=700
    )

    st.plotly_chart(fighedge, use_container_width=True)
