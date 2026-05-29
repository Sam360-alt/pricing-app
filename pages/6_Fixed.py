import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import requests

st.set_page_config(page_title="Fixed Income", layout="wide")

api_key = st.secrets["MY_API_KEY"]

def get_fred_series(series_id, api_key):
    url = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()["observations"]

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()

    return df[["date", "value"]]

bond_series = {
    "United States 10Y": "DGS10",
    "Germany 10Y": "IRLTLT01DEM156N",
    "France 10Y": "IRLTLT01FRM156N",
    "Italy 10Y": "IRLTLT01ITM156N",
    "Spain 10Y": "IRLTLT01ESM156N",
    "United Kingdom 10Y": "IRLTLT01GBM156N",
    "Japan 10Y": "IRLTLT01JPM156N",
    "Canada 10Y": "IRLTLT01CAM156N",
    "Australia 10Y": "IRLTLT01AUM156N",
}

st.subheader("Government Bond Yields")

country = st.selectbox("Choose country", list(bond_series.keys()))

df = get_fred_series(
    bond_series[country],
    api_key
)

st.line_chart(df.set_index("date")["value"])
latest_rate = df["value"].iloc[-1] / 100

st.write(f"Latest {country} yield: {latest_rate:.2%}")

def duration(notional, y = latest_rate):
    time = np.array([1,2,3,4,5,6,7,8,9,10])
    discount_factor = []
    for i in range(0,10):
        discount_factor.append(1/((1+y)**i))

    discount_factor = np.array(discount_factor)
    coupons = []
    for i in range(0,10):
        coupons.append(notional*y)

    coupons = np.array(coupons)
    coupons[-1] = coupons[-1]+notional
    coupons = coupons*discount_factor
    
    macaulay = np.sum(coupons*time)/np.sum(coupons)
    modified = macaulay/(1+y)
    return modified

if st.button('Duration'):
    st.write(duration(1000))



