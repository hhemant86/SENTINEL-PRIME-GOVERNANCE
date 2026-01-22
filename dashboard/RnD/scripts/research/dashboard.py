import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
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
@st.cache_data(ttl=0) 
def fetch_telemetry():
    try:
        response = supabase.table("multi_asset_telemetry")\
            .select("*")\
            .order("timestamp", desc=True)\
            .limit(200).execute()
        return pd.DataFrame(response.data)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=0)
def fetch_sentiment():
    try:
        # DIRECT LINK TO THE AI SENTINEL TABLE
        response = supabase.table("sentinel_intelligence")\
            .select("*")\
            .order("timestamp", desc=True)\
            .limit(1).execute()
        if response.data:
            return response.data[0]['sentiment_score']
        return 0.5  # Neutral fallback
    except Exception:
        return 0.5

# --- 3. DIAGNOSTICS ---
def check_system_health(df):
    if df.empty: return "OFFLINE", "#C62828"
    latest_pulse_time = pd.to_datetime(df['timestamp']).max()
    if (datetime.now(timezone.utc) - latest_pulse_time) > timedelta(seconds=120):
        return "ENGINE OFFLINE", "#C62828"
    return "SYSTEM LIVE", "#2E7D32"

# --- DATA RECOVERY ---
df_full = fetch_telemetry()
ai_score = fetch_sentiment()

# --- SIDEBAR: GOVERNANCE & AI ---
st.sidebar.header("🛡️ SYSTEM GOVERNANCE")

# Heartbeat
status_text, status_color = check_system_health(df_full)
st.sidebar.markdown(f"""
    <div style="background-color:{status_color}; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold;">
        📡 {status_text}
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# 🤖 FINBERT SENTIMENT DISPLAY
st.sidebar.subheader("🤖 AI SENTINEL")
sentiment_color = "#C62828" if ai_score < 0.4 else "#2E7D32" if ai_score > 0.6 else "#F57C00"
st.sidebar.metric("Geopolitical Stress Score", f"{ai_score:.2f}", delta=None)
st.sidebar.markdown(f"""
    <div style="width: 100%; background-color: #424242; border-radius: 5px;">
        <div style="width: {ai_score*100}%; background-color: {sentiment_color}; height: 10px; border-radius: 5px;"></div>
    </div>
    <small> Institutional News Sentiment (FinBERT)</small>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
focus_mode = st.sidebar.toggle("🧘 Focus Mode", value=False)
refresh_rate = st.sidebar.select_slider("Refresh (s)", options=[10, 30, 60], value=10)

# --- MAIN DASHBOARD ---
st.title("🛰️ SENTINEL PRIME : UNIFIED RISK COMMAND")

if not df_full.empty:
    # --- 4. GLOBAL RISK HEATMAP ---
    latest_pulses = df_full.drop_duplicates(subset=['asset'])
    st.subheader("🌍 Multi-Asset Regime Heatmap")
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

    # --- 5. ASSET FOCUS ---
    asset_focus = st.sidebar.selectbox("Select Asset", latest_pulses['asset'].unique())
    df_asset = df_full[df_full['asset'] == asset_focus]

    if not focus_mode:
        fig_p = px.line(df_asset, x='timestamp', y='price', 
                        title=f"{asset_focus} Live Price Action", 
                        template="plotly_dark", color_discrete_sequence=[sentiment_color])
        st.plotly_chart(fig_p, use_container_width=True)
    else:
        st.info("🧘 Focus Mode: Charts hidden. Monitoring Regimes and AI Sentiment.")

else:
    st.warning("🔄 Awaiting Hybrid Data Signal (Multi-Asset + FinBERT)...")

# --- 6. AUTO-RELOAD ---
time.sleep(refresh_rate)
st.rerun()