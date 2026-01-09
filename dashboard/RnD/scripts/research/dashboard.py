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
# Detects if running locally (.env) or on Streamlit Cloud (st.secrets)
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
        # Pull latest 50 entries from the 'sentinel_logs' table we created
        response = supabase.table("sentinel_logs").select("*").order("id", desc=True).limit(50).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"📡 Cloud Connection Failed: {e}")
        return pd.DataFrame()

# 4. PREDICTIVE ENGINE
def predict_next_move(df):
    if len(df) < 10: return None
    # Sort by ID to ensure chronological order for ML
    df_sorted = df.sort_values('id')
    y = df_sorted['z_score'].tail(10).values
    X = np.arange(len(y)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    prediction = model.predict([[len(y)]])[0]
    return prediction

# 5. UI HEADER & GLOBAL STATUS
st.title("🛰️ SENTINEL PRIME : CLOUD COMMAND")
st.caption(f"Connected to Cloud Node: {URL}")

df = load_data()

if not df.empty:
    # Latest data is the first row because of 'desc=True' in query
    last_row = df.iloc[0] 
    forecast = predict_next_move(df)
    
    # DYNAMIC RISK ALERT SYSTEM
    gov_status = last_row['governance']
    if "LOCK" in gov_status or "ALERT" in gov_status:
        st.error(f"🚨 CRITICAL: {gov_status}")
    elif last_row['state'] == "ANOMALY":
        st.warning("⚠️ WARNING: Market Anomaly Detected - High Divergence Risk")
    else:
        st.success("✅ SYSTEM NOMINAL: AI & Quant signals aligned.")

    # 6. KPI METRICS GRID
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Live Z-Score", f"{last_row['z_score']:.2f}")
    with m2:
        if forecast is not None:
            delta_val = forecast - last_row['z_score']
            st.metric("30s Forecast", f"{forecast:.2f}", delta=f"{delta_val:.2f}")
        else:
            st.metric("30s Forecast", "Learning...")
    with m3:
        st.metric("AI Sentiment", f"{last_row['sentiment']:.4f}")
    with m4:
        st.metric("Market Regime", last_row['state'])

    # 7. VISUAL INTELLIGENCE
    c1, c2 = st.columns(2)
    with c1:
        fig_z = px.line(df, x='timestamp', y='z_score', title="Volatility Pipeline (Cloud)", template="plotly_dark")
        fig_z.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Anomaly")
        st.plotly_chart(fig_z, use_container_width=True)
    with c2:
        fig_s = px.bar(df, x='timestamp', y='sentiment', title="FinBERT Sentiment Signal",
                       color='sentiment', color_continuous_scale='RdYlGn', template="plotly_dark")
        st.plotly_chart(fig_s, use_container_width=True)

    # 8. FORENSIC AUDIT TRAIL
    st.subheader("🏛️ Cloud Forensic Audit Log")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Syncing with Cloud Vault... Ensure your Engine is running on your ASUS TUF.")

# 9. AUTO-REFRESH (15s)
time.sleep(15)
st.rerun()