import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import time
from dotenv import load_dotenv
from supabase import create_client

# 1. INSTITUTIONAL PAGE CONFIG
st.set_page_config(
    page_title="SENTINEL PRIME | CLOUD COMMAND",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. SECURE HYBRID AUTHENTICATION
if os.path.exists(".env"):
    load_dotenv()
    URL = os.getenv("SUPABASE_URL")
    KEY = os.getenv("SUPABASE_KEY")
else:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]

# 3. CLOUD DATA FETCHING (Supabase)
@st.cache_data(ttl=15)
def load_data():
    try:
        supabase = create_client(URL, KEY)
        # Fetching latest 50 entries to provide context for the audit trail
        response = supabase.table("sentinel_logs").select("*").order("id", desc=True).limit(50).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"📡 Cloud Connection Failed: {e}")
        return pd.DataFrame()

# 4. PREDICTIVE COMMAND ENGINE (ML Integration)
def predict_next_move(df):
    """Calculates a short-term forecast based on the last 10 cloud entries."""
    if len(df) < 10:
        return None  # Ensure enough history exists for a valid trend analysis
        
    # 1. PREP: Sort by ID to follow the true time-series sequence
    df_sorted = df.sort_values('id')
    
    # 2. FEATURE ENGINEERING: Focus on the last 10 Z-Scores for rolling prediction
    y = df_sorted['z_score'].tail(10).values
    X = np.arange(len(y)).reshape(-1, 1)  # Time steps as independent variable (0-9)
    
    # 3. ML FIT: Linear Regression for immediate trend detection
    model = LinearRegression()
    model.fit(X, y)
    
    # 4. FORECAST: Predict the next 30s step (index 10)
    prediction = model.predict([[len(y)]])[0]
    return prediction

# 5. UI HEADER & GLOBAL STATUS
st.title("🛰️ SENTINEL PRIME : CLOUD COMMAND")
st.caption(f"Linked to Global Data Node: {URL}")

df = load_data()

if not df.empty:
    # Access the most recent telemetry (ID is descending)
    last_row = df.iloc[0] 
    forecast = predict_next_move(df)
    
    # DYNAMIC RISK ALERT SYSTEM
    gov_status = str(last_row['governance'])
    if "LOCK" in gov_status or "ALERT" in gov_status:
        st.error(f"🚨 SYSTEM GOVERNANCE: {gov_status}")
    elif last_row['state'] == "ANOMALY":
        st.warning("⚠️ RISK WARNING: Market Anomaly Detected - High Divergence")
    else:
        st.success("✅ SYSTEM NOMINAL: AI & Quant signals aligned across nodes.")

    # 6. KPI METRICS GRID
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Live Z-Score", f"{last_row['z_score']:.2f}")
    with m2:
        if forecast is not None:
            # Calculate delta for the 30s forecast display
            delta_val = forecast - last_row['z_score']
            st.metric("30s Forecast", f"{forecast:.2f}", delta=f"{delta_val:.2f}")
        else:
            st.metric("30s Forecast", "Learning...")
    with m3:
        st.metric("AI Sentiment", f"{last_row['sentiment']:.4f}")
    with m4:
        st.metric("Market Regime", last_row['state'])

    # 7. VISUAL INTELLIGENCE (Cloud Telemetry)
    c1, c2 = st.columns(2)
    with c1:
        # Plotting the Z-score pipeline
        fig_z = px.line(df, x='timestamp', y='z_score', title="Volatility Pipeline (Cloud Vault)", template="plotly_dark")
        fig_z.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Anomaly Threshold")
        st.plotly_chart(fig_z, use_container_width=True)
    with c2:
        # Visualizing sentiment distribution
        fig_s = px.bar(df, x='timestamp', y='sentiment', title="FinBERT Sentiment Stream",
                       color='sentiment', color_continuous_scale='RdYlGn', template="plotly_dark")
        st.plotly_chart(fig_s, use_container_width=True)

    # 8. INSTITUTIONAL AUDIT TRAIL
    st.subheader("🏛️ Cloud Forensic Audit Log")
    st.dataframe(df, use_container_width=True)

else:
    st.info("🔄 Syncing with Cloud Vault... Ensure your ASUS TUF engine is active.")

# 9. AUTO-REFRESH (Set to 15s to match database cache TTL)
time.sleep(15)
st.rerun()