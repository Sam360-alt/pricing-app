import streamlit as st
import numpy as np
from app_project import GBM
st.set_page_config(page_title="P&L", layout="wide")
col1,_,col2 = st.columns([6,1,1])
with col1:

    st.subheader("Choose a Spot and Volatility to compute the PnL")
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

spot = st.number_input("Spot", min_value=0.01, value=0.01, step=1.0)
sigma = st.number_input("Volatility (annual)", min_value=0.0001, value=0.01, step=0.01, format="%.4f")
product = st.session_state.get("selected_product")
product_kwargs = st.session_state.get("product_kwargs")
initial_price = st.session_state.get("initial_price")
initial_spot = st.session_state.get("initial_spot")
greeks = st.session_state.get('greeks')
st.write(f"Selected product: {product}")

if st.button('PnL'):
    try:
        model = GBM(
            maturity=st.session_state.get('maturity'),
            n_scenarios=10000,
            risk_free=st.session_state.get('riskfree_est'),
            sigma=sigma,
            steps_per_year=252,
            s_0=spot
        )

        new_price = model.price_product(product, **product_kwargs)
        pnl = initial_price - new_price
        
        delta = greeks['Delta']
        dhedge = initial_price - new_price - delta*(spot - initial_spot)
        
        if pnl < 0:

            st.error(f"P&L: {pnl:.4f}")
        elif pnl > 0:
            st.success(f"P&L: {pnl:.4f}")
        else:
            pass

        if dhedge<0:
            st.error(f"Delta Hedged P&L: {dhedge:.4f}")
        elif dhedge>0:
            st.success(f"Delta Hedged P&L: {dhedge:.4f}")
        else:
            pass

    except Exception as e:
        st.error(f"Error: {e}")