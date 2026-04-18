import streamlit as st
st.set_page_config(layout="wide")

col1,_,col2 = st.columns([6,1,1])
with col1:

    if st.button("←"):
        st.switch_page("pages/1_Pricer.py")


with col2:

    @st.dialog("Greeks")
    def show_quick_info():
        st.markdown("""
    **Greeks are computed using a bump-and-reprice approach**, which consists in slightly perturbing one parameter and observing the impact on the price.

    The idea is to approximate sensitivities using finite differences:

    - **Delta** measures sensitivity to the spot:
                    
    `Δ ≈ (V(S + dS) - V(S - dS)) / (2 dS)`

    - **Gamma** measures the curvature with respect to the spot:
                    
    `Γ ≈ (V(S + dS) - 2V(S) + V(S - dS)) / (dS²)`

    - **Vega** measures sensitivity to volatility:
                    
    `Vega ≈ (V(σ + dσ) - V(σ - dσ)) / (2 dσ)`

    Where v is the price of the product.                    

    For each Greek, the product is repriced under slightly different parameters using the same pricing function.

    This approach is particularly useful for complex or path-dependent products, where analytical formulas are not available and sensitivities must be estimated numerically.
    """)

    if st.button("ℹ️ Info"):
            show_quick_info()




st.title("Greeks Dashboard")

# Safety check
if "greeks" not in st.session_state:
    st.warning("No data available. Please run the pricer first.")
    st.stop()

# Display price
st.success(f"Price: {st.session_state['price']:.4f}")

# Display Greeks
st.subheader("Greeks at current spot")

greeks = st.session_state["greeks"]

for k, v in greeks.items():
    st.write(f"{k}: {v:.6f}")

# Display curves
st.subheader("Greek curves")

curve_df = st.session_state["curve_df"]

for greek in ["Delta", "Gamma", "Vega"]:
    st.write(f"### {greek}")
    st.line_chart(curve_df.set_index("Spot")[[greek]])


