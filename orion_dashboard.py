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
url = "https://orionterminal.com/api/screener"  # Replace with actual endpoint
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
    "1":  "change_1d",  # Change 1d (%)
    "7":  "oi_change_1d",
    "9":  "oi_change_8h",
    "8":  "oi_change_1h",
    "19": "vdelta_1d",
    "20": "vdelta_1h"
}

# --- PARSE DATA (Extract 3rd Element When List) ---
parsed = []
for symbol, stats in data.items():
    if symbol.lower() in formatted_symbols:
        row = {"symbol": symbol.replace("-binanceusdm", "")}
        for k, v in stats.items():
            if k in key_map:
                if isinstance(v, list) and len(v) >= 3:
                    row[key_map[k]] = v[2]  # ✅ Use 3rd element (index 2)
                else:
                    row[key_map[k]] = v
        parsed.append(row)

df = pd.DataFrame(parsed)

# --- DISPLAY ---
if not df.empty:
    ordered_cols = [
        "symbol", "price", "change_1d",
        "oi_change_1d", "oi_change_8h", "oi_change_1h",
        "vdelta_1d", "vdelta_1h"
    ]
    df = df[ordered_cols]

    # ✅ Formatting + Fixed Decimal Places:
    df["price"] = df["price"].astype(float).round(4)
    df["change_1d"] = df["change_1d"].astype(float).round(1)
    for col in ["oi_change_1d", "oi_change_8h", "oi_change_1h", "vdelta_1d", "vdelta_1h"]:
        df[col] = df[col].astype(float).round(1)

    # ✅ Convert to Strings to Force Exact Decimal Display
    df["price"] = df["price"].map("{:.4f}".format)
    df["change_1d"] = df["change_1d"].map("{:.1f}".format)
    for col in ["oi_change_1d", "oi_change_8h", "oi_change_1h", "vdelta_1d", "vdelta_1h"]:
        df[col] = df[col].map("{:.1f}".format)

    # ✅ Column Renaming for UI
    df.columns = [
        "Symbol", "Price", "Change 1d (%)",
        "OI Change 1d (%)", "OI Change 8h (%)", "OI Change 1h (%)",
        "Vdelta 1d", "Vdelta 1h"
    ]

    # ✅ Color highlighting function
    def highlight_positive_red_negative_green(val):
        try:
            val = float(val)
            if val > 0:
                return 'color: green'
            elif val < 0:
                return 'color: red'
            else:
                return 'color: black'
        except:
            return ''

    # ✅ Apply coloring to % fields
    styled_df = df.style.applymap(
        highlight_positive_red_negative_green,
        subset=[
            "Change 1d (%)",
            "OI Change 1d (%)", "OI Change 8h (%)", "OI Change 1h (%)",
            "Vdelta 1d", "Vdelta 1h"
        ]
    )

    st.dataframe(styled_df, use_container_width=True)
else:
    st.warning("No data available for selected symbols.")
