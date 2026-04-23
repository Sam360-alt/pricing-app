import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from app_project import GBM

st.set_page_config(page_title="Pricer", layout="wide")

colu1,_,colu2 = st.columns([6,1,1])
with colu1:
    st.title("Options and Structured Products Pricer")
with colu2:
    if st.button("👤 About me"):
        st.session_state["previous_page"] = "pages/1_Pricer.py"
        st.switch_page("pages/2_About.py")
    @st.dialog("Explanation on the pricing method")
    def show_quick_info():
        st.write("""**Geometric Brownian Motion (GBM)** models the evolution of an asset price using a combination of trend and randomness.

Under the risk-neutral measure:
`dS = rS dt + σS dW`

In discrete time:
`S(t+1) = S(t) · exp((r - 0.5σ²)Δt + σ√Δt Z)`

By simulating many paths, we obtain different possible trajectories for the asset price.

This is essential for **path-dependent products**, where the payoff depends on the full path:
- Barrier options → depend on level crossings  
- Range accruals → depend on time spent in a range  

The price is computed as the discounted average payoff across all scenarios.
                    """)

    if st.button("ℹ️ Info"):
        show_quick_info()

col1, col2 = st.columns([1, 2])
# 1) Market data
with col1:
    st.subheader("Market data")
    ticker_list = ["AAPL", "MSFT", "TSLA", "NVDA", "SPY", "^GSPC", "^STOXX50E"]
    selected_ticker = st.selectbox("Choose a ticker", ticker_list)
    start_date = st.date_input("Import data from", value=datetime(2015, 1, 1))





if st.button("Load market data"):
    data = yf.download(selected_ticker,start=start_date,end=datetime.today(), interval='1d', auto_adjust=True)

    if data.empty:
        st.error("No data found for this ticker.")
    else:
        close = data["Close"].dropna()

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        log_returns = np.log(close / close.shift(1)).dropna()

        spot_est = float(close.iloc[-1])
        vol_est = float(log_returns.std() * np.sqrt(252))
        riskfree_est = yf.download('^IRX',interval='1d',period='1y')['Close'].squeeze().iloc[-1]/100

        st.session_state["market_data"] = data
        st.session_state["spot_est"] = spot_est
        st.session_state["vol_est"] = vol_est
        st.session_state["riskfree_est"] = float(riskfree_est)


        st.success(f"Loaded market data for {selected_ticker}")
       
# Show chart if data exists

with col2:
    if "market_data" in st.session_state:
        st.line_chart(st.session_state["market_data"]["Close"])
        st.write(f"Spot: {st.session_state['spot_est']:.2f}")
        st.write(f"Historic annual volatility: {st.session_state['vol_est']:.2%}")


cl1,cl2 = st.columns([1,2])
with cl1:
# 2) Model parameters

    st.subheader("Model parameters")

    default_spot = st.session_state.get("spot_est", 100.0)
    default_vol = st.session_state.get("vol_est", 0.20)
    default_riskfree = st.session_state.get('riskfree_est',0.02)

    spot = st.number_input("Spot", min_value=0.01, value=float(default_spot), step=1.0)
    risk_free = st.number_input("Risk-free rate", value=float(default_riskfree), step=0.005, format="%.4f")


    sigma = st.number_input("Volatility (annual)", min_value=0.0001, value=float(default_vol), step=0.01, format="%.4f")
    maturity = st.number_input("Maturity (years)", min_value=0.01, value=1.0, step=0.25)
    st.session_state["maturity"] = maturity
    n_scenarios = 10000
    steps_per_year = 252

with cl2:
# 3) Product selection
    st.subheader("Product selection")

    product = st.selectbox(
        "Choose product",
        ["Vanilla Option", "Knock-In Option", "Knock-Out Option", "Bonus Steps Certificate",'Range Accrual']
    )

    price = None

    # -----------------------------
    # 4) Product-specific inputs
    # -----------------------------
    if product == "Vanilla Option":
        strike = st.number_input("Strike", min_value=0.01, value=float(spot), step=1.0)
        option_type = st.selectbox("Option type", ["call", "put"])

    elif product == "Knock-In Option":
        strike = st.number_input("Strike", min_value=0.01, value=float(spot), step=1.0)
        barrier = st.number_input("Barrier", min_value=0.01, value=float(spot * 1.10), step=1.0)
        option_type = st.selectbox("Option type", ["PDI", "PUI", "CUI", "CDI"])

    elif product == "Knock-Out Option":
        strike = st.number_input("Strike", min_value=0.01, value=float(spot), step=1.0)
        barrier = st.number_input("Barrier", min_value=0.01, value=float(spot * 1.10), step=1.0)
        option_type = st.selectbox("Option type", ["PDO", "PUO", "CUO", "CDO"])

    elif product == "Bonus Steps Certificate":
        barrier1 = st.number_input("Barrier 1", min_value=0.01, value=float(spot * 0.90), step=1.0)
        barrier2 = st.number_input("Barrier 2", min_value=0.01, value=float(spot * 1.10), step=1.0)
        coupon = st.number_input("Coupon rate", min_value=0.0, value=0.05, step=0.01, format="%.4f")
        notional = st.number_input("Notional", min_value=0.01, value=1000.0, step=100.0)
        product_type = st.selectbox("Observation type", ["American", "European"])

    elif product == "Range Accrual":
        range_down = st.number_input("Range Down", min_value=0.01, value=float(spot * 0.90), step=1.0)
        range_up = st.number_input("Range Up", min_value=0.01, value=float(spot * 1.10), step=1.0)
        coupon = st.number_input("Coupon rate", min_value=0.0, value=0.05, step=0.01, format="%.4f")
        notional = st.number_input("Notional", min_value=0.01, value=1000.0, step=100.0)

    product_kwargs = {}

    if product == "Vanilla Option":
        product_kwargs = {
            "strike": strike,
            "option_type": option_type
        }

    elif product == "Knock-In Option":
        product_kwargs = {
            "strike": strike,
            "barrier": barrier,
            "option_type": option_type
        }

    elif product == "Knock-Out Option":
        product_kwargs = {
            "strike": strike,
            "barrier": barrier,
            "option_type": option_type
        }

    elif product == "Bonus Steps Certificate":
        product_kwargs = {
            "barrier1": barrier1,
            "barrier2": barrier2,
            "coupon": coupon,
            "product_type": product_type,
            "notional": notional
        }
    elif product == "Range Accrual":
        product_kwargs = {
            "range_down": range_down,
            "range_up": range_up,
            "coupon": coupon,
            "notional": notional
        }
# -----------------------------
# 5) Price button
# -----------------------------
    c1,c2 = st.columns([1,6])
    with c1:
        if st.button("Price product"):
            try:
                if product in ["Knock-In Option", "Knock-Out Option"]:
                    path_model = GBM(
                        maturity=maturity,
                        n_scenarios=int(n_scenarios),
                        risk_free=risk_free,
                        sigma=sigma,
                        steps_per_year=int(steps_per_year),
                        s_0=spot
                    )

                    all_paths = path_model.monte_carlo()
                    sample_cols = np.random.choice(all_paths.columns, size=min(75, all_paths.shape[1]), replace=False)
                    sampled_paths = all_paths.loc[:, sample_cols].copy()
                    sampled_paths.index = np.linspace(0, maturity, len(sampled_paths))
                    sampled_paths["Barrier"] = barrier

                    st.session_state["sampled_paths"] = sampled_paths
                    st.session_state["barrier"] = barrier

                    
                model = GBM(
                    maturity=maturity,
                    n_scenarios=int(n_scenarios),
                    risk_free=risk_free,
                    sigma=sigma,
                    steps_per_year=int(steps_per_year),
                    s_0=spot
                )

                price = model.price_product(product, **product_kwargs)
                st.session_state["selected_product"] = product
                st.session_state["product_kwargs"] = product_kwargs
                st.session_state["maturity"] = maturity
                st.session_state["risk_free"] = risk_free
                st.session_state["initial_price"] = price
                st.session_state["initial_spot"] = spot
                st.session_state["initial_sigma"] = sigma
                st.success(f"Price: {price:.4f}")
                
                
                
                delta_val = -model.delta(product=product, **product_kwargs)
                gamma_val = -model.gamma(product=product, **product_kwargs)
                vega_val = -model.vega(product=product, **product_kwargs)/100

                st.session_state["price"] = price
                st.session_state["greeks"] = {
                        "Delta": delta_val,
                        "Gamma": gamma_val,
                        "Vega": vega_val,
                    }

                

                spot_grid = np.linspace(0.5 * spot, 1.5 * spot, 25)

                delta_curve = []
                gamma_curve = []
                vega_curve = []

                progress_bar = st.progress(0)
                status_text = st.empty()
                n_points = len(spot_grid)
                for i,s in enumerate(spot_grid):
                    scenario_model = GBM(
                        maturity=maturity,
                        n_scenarios=int(n_scenarios),
                        risk_free=risk_free,
                        sigma=sigma,
                        steps_per_year=int(steps_per_year),
                        s_0=float(s)
                    )

                    delta_curve.append(-scenario_model.delta(product=product, **product_kwargs))
                    gamma_curve.append(-scenario_model.gamma(product=product, **product_kwargs))
                    vega_curve.append(-scenario_model.vega(product=product, **product_kwargs)/100)
            
                    progress = (i + 1) / n_points
                    progress_bar.progress(progress)

                    status_text.text(f"Computing Greeks... {int(progress*100)}%")
                

                curve_df = pd.DataFrame({
                    "Spot": spot_grid,
                    "Delta": delta_curve,
                    "Gamma": gamma_curve,
                    "Vega": vega_curve,
                })


                st.session_state["curve_df"] = curve_df

            
            except Exception as e:
                st.error(f"Error: {e}")


        if st.button("View Greeks"):
            st.switch_page("pages/3_Greeks.py")
    with c2:
        if st.button("P&L"):
            st.switch_page("pages/4_PnL.py")

        if st.button("Paths Sample"):
            st.switch_page("pages/5_Paths.py")

