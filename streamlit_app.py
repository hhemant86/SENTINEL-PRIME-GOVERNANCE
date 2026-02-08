import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime, timezone

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Sentinel Prime | Orion Mesh",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CONNECTION (Hard-coded for Streamlit Cloud Vault)
@st.cache_resource
def init_connection():
    try:
        # These MUST be set in the Streamlit Cloud "Secrets" tab
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Credential Error: Check the Secrets tab in Streamlit Settings.")
        st.stop()

supabase = init_connection()

# 3. DATA FETCHING (Optimized)
@st.cache_data(ttl=600)
def fetch_telemetry():
    res = supabase.table("multi_asset_telemetry").select("*").order("timestamp", desc=True).limit(500).execute()
    return pd.DataFrame(res.data)

@st.cache_data(ttl=600)
def fetch_sentiment():
    res = supabase.table("sentinel_logs").select("*").order("timestamp", desc=True).limit(50).execute()
    return pd.DataFrame(res.data)

# --- LOAD DATA ---
telemetry_df = fetch_telemetry()
sentiment_df = fetch_sentiment()

# --- SIDEBAR: SYSTEM INTEGRITY ---
with st.sidebar:
    st.title("🛡️ Sentinel Node")
    st.divider()
    
    if not telemetry_df.empty:
        last_ts = pd.to_datetime(telemetry_df['timestamp'].iloc[0])
        now = datetime.now(timezone.utc)
        diff = (now - last_ts.replace(tzinfo=timezone.utc)).total_seconds() / 60
        
        if diff < 25:
            st.success("🟢 CLOUD ORACLE: ACTIVE")
            st.caption(f"Pulse: {int(diff)}m ago")
        else:
            st.warning("🟡 ORACLE: STANDBY")
    
    st.divider()
    st.info("**Strategy:** Orion Planetary Mesh\n\n**Calibration:** Institutional (Agra)")

# --- MAIN DASHBOARD ---
st.title("🛡️ Sentinel Prime: Planetary Risk Governance")
st.markdown("---")

# --- 4. THE ORION MESH GRID ---
st.subheader("🌐 Orion Planetary Mesh: Global Telemetry")

groups = {
    "🏆 Bullion (Calibrated)": ["MCX_GOLD", "MCX_SILVER", "GOLD", "SILVER"],
    "🌐 Digital & Macro": ["BTC", "ETH", "DXY", "VIX", "INDIA_VIX"],
    "🛢️ Commodities": ["CRUDE", "NAT_GAS", "COPPER"],
    "📈 Indices": ["NIFTY50", "SENSEX", "SP500", "NASDAQ", "NIKKEI", "DAX", "FTSE", "HANGSENG", "DOW"]
}

if not telemetry_df.empty:
    for group_name, asset_list in groups.items():
        st.write(f"#### {group_name}")
        cols = st.columns(len(asset_list))
        for i, asset_name in enumerate(asset_list):
            asset_data = telemetry_df[telemetry_df['asset'] == asset_name]
            if not asset_data.empty:
                current_price = asset_data['price'].iloc[0]
                delta = current_price - asset_data['price'].iloc[1] if len(asset_data) > 1 else None
                cols[i].metric(label=asset_name, value=f"{current_price:,.1f}", delta=f"{delta:,.2f}" if delta else None, border=True)

st.divider()

# --- 5. ANALYTICS ---
c_left, c_right = st.columns([2, 1])

with c_left:
    st.subheader("📊 Multi-Asset Correlation")
    selected = st.multiselect("Asset Comparison", telemetry_df['asset'].unique(), default=["BTC", "MCX_GOLD", "MCX_SILVER"])
    plot_df = telemetry_df[telemetry_df['asset'].isin(selected)]
    fig = px.line(plot_df, x='timestamp', y='price', color='asset', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with c_right:
    st.subheader("🧠 Narrative Sentiment")
    if not sentiment_df.empty:
        val = sentiment_df['sentiment'].iloc[0]
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=val, domain={'x': [0, 1], 'y': [0, 1]}, gauge={'axis': {'range': [-1, 1]}, 'bar': {'color': "white"}}))
        fig_gauge.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)

# --- 6. AUDIT LOG ---
st.subheader("📜 Risk Governance Audit Log")
if not sentiment_df.empty:
    st.dataframe(sentiment_df[['timestamp', 'state', 'sentiment', 'governance']], use_container_width=True, hide_index=True)