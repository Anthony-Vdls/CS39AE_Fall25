import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
import json

# 1) Read API once
st.set_page_config(page_title="Weather Updates in the Bermuda Triangle", page_icon="⛈️", layout="wide")
# Disable fade/transition so charts don't blink between reruns
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("Live weather updates in the worlds biggest plane graveyard✈️ ")
st.caption("Wondering if its safe to traverse the Bermuda Triangle? You just found a resource to check before you brave the worlds biggest graveyard to air planes that diassapered👻")

# 2) Config
COINS = ["bitcoin", "ethereum"]
VS = "usd"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

def build_url(ids):
    return f"https://api.open-meteo.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies={VS}"

API_URL = build_url(COINS)

# Tiny sample to keep the demo working even if the API is rate-limiting
SAMPLE_DF = pd.DataFrame(
    [{"coin": "bitcoin", VS: 68000}, {"coin": "ethereum", VS: 3500}]
)
############################################################################
# Bermuda Triangle
lat, lon = 25.853311586063516, -70.60603721520464 
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
@st.cache_data(ttl=600)
def get_weather():
    r = requests.get(wurl, timeout=10); r.raise_for_status()
    j = r.json()["current"]
    return pd.DataFrame([{"time": pd.to_datetime(j["time"]),
                          "temperature": j["temperature_2m"],
                          "wind": j["wind_speed_10m"]}])
# bern triangle geojson 
triangle_geojson = {
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "id": "bermuda_triangle",
    "properties": {"name": "Bermuda Triangle"},
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-80.1918, 25.7617],  # Miami
        [-64.7505, 32.3078],  # Bermuda
        [-66.1057, 18.4655],  # San Juan
        [-80.1918, 25.7617]   # back to Miami to close
      ]]
    }
  }]
}

metric = st.radio("Color by", ["temperature", "wind"], horizontal=True)

data = pd.DataFrame({
    "id": ["bermuda_triangle"],
    "value": [df.iloc[0][metric]],
    "label": [f"{metric}: {df.iloc[0][metric]}"]
})



############################################################################
# 3) FETCH (CACHED)
@st.cache_data(ttl=300, show_spinner=False)   # Cache for 5 minutes

def fetch_weather(url: str):
    """Return (df, error_message). Never raise. Safe for beginners."""
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        # Handle 429 and other non-200s
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "a bit")
            return None, f"429 Too Many Requests — try again after {retry_after}s"
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data).T.reset_index().rename(columns={"index": "coin"})
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"
# 4) Refresh Button
# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")

# Let user choose how often to refresh (in seconds)
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)

# Toggle to turn automatic refreshing on/off
auto_refresh = st.toggle("Enable auto-refresh", value=False)

# Show current refresh time
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# 5) MAIN VIEW --------------------------------------

st.subheader("Prices")
df, err = fetch_weather(wurl)

if err:
    st.warning(f"{err}\nShowing sample data so the demo continues.")
    df = SAMPLE_DF.copy()

st.dataframe(df, use_container_width=True)

# fig = px.bar(df, x="coin", y='temperature_2m', title=f"Current price ({VS.upper()})")

fig = px.choropleth(
    data_frame=data,
    geojson=triangle_geojson,
    locations="id",
    color="value",
    featureidkey="id",
    projection="natural earth",
    hover_name="label",
    color_continuous_scale="Viridis",
)
fig.update_geos(
    showocean=True, oceancolor="#aadaff",
    showland=False, showcountries=False,
    fitbounds="locations"
)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                  coloraxis_colorbar=dict(title=metric))

st.plotly_chart(fig, use_container_width=True)


# If auto-refresh is ON, wait and rerun the app
if auto_refresh:
    time.sleep(refresh_sec)
    fetch_weather.clear()
    st.rerun()

