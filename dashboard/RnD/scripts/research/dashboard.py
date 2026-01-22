import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client

# --- 0. PAGE ARCHITECTURE ---
st.set_page_config(
    page_title="SENTINEL | RISK COMMAND",
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

# --- 2. TELEMETRY ENGINE ---
@st.cache_data(ttl=0) 
def fetch_telemetry():
    try:
        response = supabase.table("multi_asset_telemetry")\
            .select("*")\
            .order("timestamp", desc=True)\
            .limit(200).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()

# --- 3. HEARTBEAT DIAGNOSTIC (The Corporate Health Check) ---
def check_system_health(df):
    if df.empty:
        return "OFFLINE", "#C62828"  # Red
    
    # Ensure timestamp is datetime aware
    latest_pulse_time = pd.to_datetime(df['timestamp']).max()
    
    # If the time difference is > 120 seconds, the engine is failing
    if (datetime.now(timezone.utc) - latest_pulse_time) > timedelta(seconds=120):
        return "ENGINE OFFLINE", "#C62828"  # Red
    else:
        return "SYSTEM LIVE", "#2E7D32"  # Green

# --- UI START ---
df_full = fetch_telemetry()

# --- SIDEBAR: COMMAND CONTROLS & MONITOR ---
st.sidebar.header("🛡️ SYSTEM STATUS")

# HEARTBEAT MONITOR PLACEMENT
status_text, status_color = check_system_health(df_full)
st.sidebar.markdown(f"""
    <div style="background-color:{status_color}; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; border: 1px solid rgba(255,255,255,0.2);">
        📡 {status_text}
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
focus_mode = st.sidebar.toggle("🧘 Focus Mode", value=False)
refresh_rate = st.sidebar.select_slider("Refresh (s)", options=[10, 30, 60], value=10)

# Main Title
st.title("🛰️ SENTINEL PRIME : UNIFIED RISK COMMAND")

if not df_full.empty:
    # --- 4. GLOBAL RISK HEATMAP ---
    latest_pulses = df_full.drop_duplicates(subset=['asset'])
    st.subheader("🌍 Global Market Regime Heatmap")
    h_cols = st.columns(len(latest_pulses))
    
    for i, (_, row) in enumerate(latest_pulses.iterrows()):
        with h_cols[i]:
            regime = str(row.get('regime', 'INITIALIZING')).upper()
            bg_color = "#2E7D32" if "STABLE" in regime else \
                       "#F57C00" if "STRESS" in regime else \
                       "#C62828" if "ANOMALY" in regime else "#424242"
            st.markdown(f"""
                <div style="background-color:{bg_color}; padding:15px; border-radius:10px; text-align:center; color:white;">
                    <small>{row['asset']}</small><br><strong>{regime}</strong>
                </div>
            """, unsafe_allow_html=True)

    # --- 5. ASSET FOCUS & CHARTS ---
    asset_focus = st.sidebar.selectbox("Select Asset", latest_pulses['asset'].unique())
    df_asset = df_full[df_full['asset'] == asset_focus]

    if not focus_mode:
        fig_p = px.line(df_asset, x='timestamp', y='price', title=f"{asset_focus} Real-Time Pulse", template="plotly_dark")
        st.plotly_chart(fig_p, use_container_width=True)
    else:
        st.info("🧘 Focus Mode: Charts hidden. Monitoring Regimes.")

else:
    st.warning("🔄 Awaiting Data Signal from ASUS TUF Engine...")

# --- 6. AUTO-RELOAD ---
time.sleep(refresh_rate)
st.rerun()