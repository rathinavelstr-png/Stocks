# ==========================================
# Live Revenue Pulse Dashboard (Streamlit)
# ==========================================

import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ================================
# CONFIG
# ================================
st.set_page_config(page_title="Live Revenue Pulse", layout="wide")

API_KEY = st.secrets.get("API_KEY", "YOUR_OPENWEATHER_API_KEY")  # safer
REFRESH_INTERVAL = 30 * 1000  # 30 sec

# ================================
# AUTO REFRESH
# ================================
st_autorefresh(interval=REFRESH_INTERVAL, key="refresh")

st.title("📊 Live Revenue Pulse Dashboard")

# ================================
# SESSION STATE INIT
# ================================
if "sales_data" not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(
        columns=["Time", "Product", "Price", "City"]
    )

# ================================
# FAKE DATA GENERATION
# ================================
products = ["Laptop", "Phone", "Tablet", "Headphones", "Camera"]
cities = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]

def generate_fake_sale():
    return {
        "Time": datetime.now(),
        "Product": random.choice(products),
        "Price": random.randint(5000, 50000),
        "City": random.choice(cities)
    }

# Add new row
new_sale = generate_fake_sale()
st.session_state.sales_data = pd.concat(
    [st.session_state.sales_data, pd.DataFrame([new_sale])],
    ignore_index=True
)

df = st.session_state.sales_data

# ================================
# METRICS
# ================================
total_revenue = int(df["Price"].sum())
total_orders = len(df)

col1, col2 = st.columns(2)

col1.metric("💰 Total Revenue", f"₹{total_revenue:,}")
col2.metric("📦 Total Orders", total_orders)

# ================================
# CHART
# ================================
st.subheader("📈 Sales by City")

city_sales = df.groupby("City", as_index=False)["Price"].sum()

fig = px.bar(city_sales, x="City", y="Price", title="Revenue by City")
st.plotly_chart(fig, use_container_width=True)

# ================================
# WEATHER FUNCTION (CACHED)
# ================================
@st.cache_data(ttl=600)
def get_weather(city):
    if API_KEY == "YOUR_OPENWEATHER_API_KEY":
        return "No API", "No API", "⚠️ Add API key"

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return "Error", "Error", "⚠️ API issue"

        data = response.json()

        weather_main = data["weather"][0]["main"]
        temp = data["main"]["temp"]

        if weather_main.lower() == "rain":
            impact = "🌧️ Rain affecting sales"
        elif temp > 35:
            impact = "🔥 Heat affecting sales"
        else:
            impact = "✅ Normal conditions"

        return weather_main, temp, impact

    except Exception:
        return "N/A", "N/A", "❌ Weather unavailable"

# ================================
# WEATHER DISPLAY
# ================================
st.subheader("🌦️ Weather Impact on Sales")

weather_data = []

for city in cities:
    weather, temp, impact = get_weather(city)
    weather_data.append({
        "City": city,
        "Weather": weather,
        "Temperature (°C)": temp,
        "Impact": impact
    })

weather_df = pd.DataFrame(weather_data)

st.dataframe(weather_df, use_container_width=True)

# ================================
# LIVE TABLE
# ================================
st.subheader("🧾 Live Sales Feed")
st.dataframe(df.tail(10), use_container_width=True)

# ================================
# FOOTER
# ================================
st.caption("Auto-refresh every 30 seconds ⏳")
