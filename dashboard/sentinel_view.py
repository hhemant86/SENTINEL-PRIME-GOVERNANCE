import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Sentinel Prime | Orion Mesh",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# 2. CONNECTION (Cached for speed)
@st.cache_resource
def init_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_connection()

# 3. DATA FETCHING (Cached for 10 minutes)
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

# --- SIDEBAR & SYSTEM HEALTH ---
with st.sidebar:
    st.title("🛡️ Sentinel Node")
    st.divider()
    
    if not telemetry_df.empty:
        last_ts = pd.to_datetime(telemetry_df['timestamp'].iloc[0])
        now = datetime.now(timezone.utc)
        diff = (now - last_ts.replace(tzinfo=timezone.utc)).total_seconds() / 60
        
        if diff < 25:
            st.success(f"🟢 CLOUD ORACLE: ACTIVE")
            st.caption(f"Last Pulse: {int(diff)}m ago")
        else:
            st.warning("🟡 ORACLE: STANDBY")
            st.caption("Waiting for Cloud Heartbeat...")
    
    st.divider()
    st.markdown("### 🛰️ Infrastructure")
    st.info("**Strategy:** Orion Planetary Mesh\n\n**Calibration:** Institutional (Agra)\n\n**Compute:** GitHub Cloud Node")

# --- HEADER ---
st.title("🛡️ Sentinel Prime: Planetary Risk Governance")
st.markdown("---")

# --- 4. THE ORION MESH GRID (21 ASSETS) ---
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
                # Calculate simple delta if data exists
                delta = None
                if len(asset_data) > 1:
                    delta = current_price - asset_data['price'].iloc[1]
                
                cols[i].metric(
                    label=asset_name, 
                    value=f"{current_price:,.1f}", 
                    delta=f"{delta:,.2f}" if delta else None,
                    border=True
                )
        st.write("")

st.divider()

# --- 5. ANALYTICS SECTION ---
c_left, c_right = st.columns([2, 1])

with c_left:
    st.subheader("📊 Multi-Asset Correlation")
    # Filter for top 5 assets to keep chart clean
    selected_assets = st.multiselect("Select Assets to Compare", telemetry_df['asset'].unique(), default=["BTC", "MCX_GOLD", "MCX_SILVER"])
    plot_df = telemetry_df[telemetry_df['asset'].isin(selected_assets)]
    
    fig = px.line(plot_df, x='timestamp', y='price', color='asset', 
                 template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Prism)
    fig.update_layout(height=450, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

with c_right:
    st.subheader("🧠 Narrative Sentiment")
    if not sentiment_df.empty:
        latest_sent = sentiment_df['sentiment'].iloc[0]
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = latest_sent,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [-1, 1], 'tickwidth': 1},
                'bar': {'color': "white"},
                'steps' : [
                    {'range': [-1, -0.4], 'color': "#FF4B4B"},
                    {'range': [-0.4, 0.4], 'color': "#31333F"},
                    {'range': [0.4, 1], 'color': "#00D46A"}],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': latest_sent}
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)

# --- 6. AUDIT LOG ---
st.subheader("📜 Risk Governance Audit Log")
if not sentiment_df.empty:
    # Stylized dataframe
    st.dataframe(
        sentiment_df[['timestamp', 'state', 'sentiment', 'governance']],
        use_container_width=True,
        hide_index=True
    )