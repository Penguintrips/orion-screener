import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- PAGE CONFIG ---
st.set_page_config("Orion Screener Dashboard", layout="wide")

# --- AUTO REFRESH EVERY 5 MINUTES ---
st_autorefresh(interval=5 * 60 * 1000, key="auto_refresh")

# --- HEADER ---
st.title("🛰️ Orion Crypto Screener")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- REFRESH BUTTON ---
if st.button("🔁 Refresh Now"):
    st.rerun()

# --- SYMBOLS TO TRACK ---
trading_cryptos = [
    "XRP/USDT", "SOL/USDT", "BNB/USDT", "DOGE/USDT", "CAKE/USDT",
    "ADA/USDT", "AVAX/USDT", "AAVE/USDT", "BONK/USDT", "WIF/USDT"
]
formatted_symbols = [f"{s.lower()}-binanceusdm" for s in trading_cryptos]

# --- Orion Screener API Endpoint ---
url = "https://orionterminal.com/api/screener"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers)
    data = response.json()
except Exception as e:
    st.error(f"Failed to fetch data: {e}")
    st.stop()

# --- FIELD MAPPING ---
key_map = {
    "11": "price",
    "26": "ticks_5m",
    "0":  "change_5m",
    "6":  "volume_5m",
    "42": "volatility_15m",
    "15": "oi_change_1d",
    "8":  "volume_1h",
    "22": "vdelta_1h"
}

# --- PARSE DATA ---
parsed = []
for symbol, stats in data.items():
    if symbol.lower() in formatted_symbols:
        row = {"symbol": symbol.replace("-binanceusdm", "")}
        for k, v in stats.items():
            if k in key_map:
                col = key_map[k]
                if col in ["volume_5m", "volume_1h"] and isinstance(v, list):
                    row[col] = v[0]
                else:
                    row[col] = v
        parsed.append(row)

df = pd.DataFrame(parsed)

# --- DISPLAY ---
if not df.empty:
    ordered_cols = [
        "symbol", "price", "ticks_5m", "change_5m",
        "volume_5m", "volatility_15m", "oi_change_1d",
        "volume_1h", "vdelta_1h"
    ]
    df = df[ordered_cols]
    df["price"] = df["price"].astype(float).round(5)
    df["change_5m"] = (df["change_5m"].astype(float) * 100).round(2)  # to %
    df["volume_5m"] = df["volume_5m"].astype(float).round(2)
    df["volume_1h"] = df["volume_1h"].astype(float).round(2)
    df["volatility_15m"] = df["volatility_15m"].astype(float).round(3)

    st.dataframe(df, use_container_width=True)
else:
    st.warning("No data available for selected symbols.")
