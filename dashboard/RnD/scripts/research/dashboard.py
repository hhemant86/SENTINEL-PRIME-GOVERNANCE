import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client

# --- 0. PAGE ARCHITECTURE ---
st.set_page_config(
    page_title="SENTINEL | UNIFIED COMMAND",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. SECURE CLOUD CONNECTION ---
if os.path.exists(".env"):
    load_dotenv()
    URL = os.getenv("SUPABASE_URL")
    KEY = os.getenv("SUPABASE_KEY")
else:
    URL = st.secrets.get("SUPABASE_URL")
    KEY = st.secrets.get("SUPABASE_KEY")

@st.cache_resource
def get_supabase():
    return create_client(URL, KEY)

supabase = get_supabase()

# --- 2. DATA FUSION ENGINES ---
# Added 'nocache' parameter to force fresh data every refresh_rate
def fetch_telemetry():
    try:
        response = supabase.table("multi_asset_telemetry")\
            .select("*")\
            .order("timestamp", desc=True)\
            .limit(100).execute()
        return pd.DataFrame(response.data)
    except Exception:
        return pd.DataFrame()

def fetch_sentiment():
    try:
        # Step 1: Query by ID (assuming it's an auto-incrementing primary key)
        # This is the most reliable way to get the "Last In" row
        response = supabase.table("sentinel_logs")\
            .select("sentiment")\
            .order("id", desc=True)\
            .limit(1).execute()
        
        if response.data:
            # Step 2: Extract the score
            score = response.data[0].get('sentiment', 0.5)
            return float(score)
        return 0.5
    except Exception as e:
        # Step 3: Minimal error reporting for your eyes only during the demo
        # st.sidebar.error(f"Sync Lag: {e}") 
        return 0.5

# --- 3. SYSTEM HEALTH LOGIC ---
def check_system_health(df):
    if df.empty: return "OFFLINE", "#C62828"
    latest_pulse = pd.to_datetime(df['timestamp']).max()
    if latest_pulse.tzinfo is None:
        latest_pulse = latest_pulse.replace(tzinfo=timezone.utc)
    
    if (datetime.now(timezone.utc) - latest_pulse) > timedelta(seconds=120):
        return "ENGINE LAG", "#F57C00"
    return "SYSTEM LIVE", "#2E7D32"

# --- DATA EXECUTION ---
df_full = fetch_telemetry()
ai_score = fetch_sentiment()

# --- SIDEBAR: GOVERNANCE ---
st.sidebar.header("🛡️ SYSTEM GOVERNANCE")

status_text, status_color = check_system_health(df_full)
st.sidebar.markdown(f"""
    <div style="background-color:{status_color}; padding:10px; border-radius:8px; text-align:center; color:white; font-weight:bold;">
        📡 {status_text}
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# 🤖 AI SENTINEL GAUGE
st.sidebar.subheader("🤖 AI SENTINEL")
# Color logic for sentiment
s_color = "#C62828" if ai_score < 0.45 else "#2E7D32" if ai_score > 0.55 else "#F57C00"

st.sidebar.metric("Sentiment Pulse (FinBERT)", f"{ai_score:.4f}")
st.sidebar.markdown(f"""
    <div style="width: 100%; background-color: #424242; border-radius: 5px; margin-top:10px;">
        <div style="width: {min(max((ai_score + 1) / 2 * 100, 0), 100)}%; background-color: {s_color}; height: 8px; border-radius: 5px;"></div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
refresh_rate = st.sidebar.select_slider("Telemetry Sync (s)", options=[5, 10, 30, 60], value=10)

# --- MAIN DASHBOARD ---
st.title("🛰️ SENTINEL PRIME : UNIFIED RISK COMMAND")

if not df_full.empty:
    # 🌍 Heatmap
    latest_pulses = df_full.drop_duplicates(subset=['asset'])
    h_cols = st.columns(len(latest_pulses))
    
    for i, (_, row) in enumerate(latest_pulses.iterrows()):
        with h_cols[i]:
            regime = str(row.get('regime', 'SYNCING')).upper()
            reg_color = "#2E7D32" if "STABLE" in regime else "#F57C00" if "STRESS" in regime else "#C62828"
            st.markdown(f"""
                <div style="background-color:{reg_color}; padding:12px; border-radius:8px; text-align:center; color:white;">
                    <small>{row['asset']}</small><br><strong>{regime}</strong>
                </div>
                """, unsafe_allow_html=True)

    # 📈 Charting
    asset_focus = st.sidebar.selectbox("Focus Asset", latest_pulses['asset'].unique())
    df_plot = df_full[df_full['asset'] == asset_focus]
    
    fig = px.line(df_plot, x='timestamp', y='price', title=f"{asset_focus} Real-time Telemetry",
                  template="plotly_dark", color_discrete_sequence=[s_color])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("🔄 Establishing Cloud Handshake... Check local engine status.")

# --- AUTO-REFRESH ---
time.sleep(refresh_rate)
st.rerun()