import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime, timezone

# 1. PAGE CONFIG
st.set_page_config(page_title="Sentinel Prime | Orion Mesh", page_icon="🛡️", layout="wide")

# 2. BULLETPROOF CONNECTION
@st.cache_resource
def init_connection():
    # Diagnostic: Check if keys exist in the vault
    if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
        st.error("❌ CRITICAL: Secrets missing in Streamlit Cloud Dashboard.")
        st.stop()
    
    # Use st.secrets instead of os.environ for cloud reliability
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"❌ Connection Handshake Failed: {e}")
    st.stop()

# 3. DATA FETCHING (With Error Handling)
@st.cache_data(ttl=300)
def fetch_telemetry():
    try:
        res = supabase.table("multi_asset_telemetry").select("*").order("timestamp", desc=True).limit(500).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.warning(f"📡 Telemetry Standby: {e}")
        return pd.DataFrame()

# --- APP LOGIC ---
st.title("🛡️ Sentinel Prime: Orion Mesh")
st.markdown("---")

telemetry_df = fetch_telemetry()

# 4. DASHBOARD GRID
if not telemetry_df.empty:
    st.subheader("🌐 Global Telemetry")
    top_assets = ["BTC", "MCX_GOLD", "MCX_SILVER", "DXY"]
    cols = st.columns(len(top_assets))
    
    for i, asset in enumerate(top_assets):
        data = telemetry_df[telemetry_df['asset'] == asset]
        if not data.empty:
            val = data['price'].iloc[0]
            cols[i].metric(asset, f"{val:,.1f}", border=True)
            
    st.divider()
    st.subheader("📊 Price Correlation")
    selected = st.multiselect("Select Comparison", telemetry_df['asset'].unique(), default=["BTC", "MCX_GOLD"])
    plot_df = telemetry_df[telemetry_df['asset'].isin(selected)]
    fig = px.line(plot_df, x='timestamp', y='price', color='asset', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("🔄 System Initializing... Refreshing data from Orion Mesh.")