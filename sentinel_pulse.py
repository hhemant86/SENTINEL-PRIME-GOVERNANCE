import os
import time
import asyncio
import yfinance as yf
import requests
import feedparser
from supabase import create_client
from datetime import datetime, timezone
from dotenv import load_dotenv

# 1. SETUP CONNECTIONS
load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not URL or not KEY:
    print("❌ ERROR: Credentials missing. Check .env or GitHub Secrets.")
    exit(1)

supabase = create_client(URL, KEY)

# 2. THE ORION MESH (21 Global Assets)
def fetch_market_data():
    assets = {
        # Bullion (Institutional Calibration)
        "GOLD": "GC=F", "SILVER": "SI=F", 
        "MCX_GOLD": "GOLDBEES.NS", "MCX_SILVER": "SILVERBEES.NS",
        # Digital Assets
        "BTC": "BTC-USD", "ETH": "ETH-USD",
        # Macro & Fear Indices
        "DXY": "DX-Y.NYB", "VIX": "^VIX", "INDIA_VIX": "^INDIAVIX",
        # Commodities
        "CRUDE": "CL=F", "NAT_GAS": "NG=F", "COPPER": "HG=F",
        # Global Equity Indices
        "SP500": "^GSPC", "NASDAQ": "^IXIC", "NIKKEI": "^N225", 
        "DAX": "^GDAXI", "FTSE": "^FTSE", "HANGSENG": "^HSI",
        "NIFTY50": "^NSEI", "SENSEX": "^BSESN", "DOW": "^DJI"
    }
    payload = []
    for name, ticker in assets.items():
        try:
            # Using fast_info for high-speed cloud execution
            price = yf.Ticker(ticker).fast_info['last_price']
            
            # --- INSTITUTIONAL CALIBRATION LOGIC ---
            if name == "MCX_GOLD": price *= 1240 
            if name == "MCX_SILVER": price *= 1175
            
            payload.append({
                "asset": name, 
                "price": float(price), 
                "source": "Cloud-Oracle"
            })
        except: continue
    return payload

# 3. AI NARRATIVE ENGINE (FinBERT)
def get_ai_sentiment():
    API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    feeds = ["https://finance.yahoo.com/news/rssindex", "https://www.kitco.com/rss/news.xml"]
    headlines = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            headlines.extend([entry.title for entry in feed.entries[:3]])
        except: continue

    if not headlines: return 0.0, "STABLE"

    try:
        for attempt in range(3):
            response = requests.post(API_URL, headers=headers, json={"inputs": headlines}, timeout=15)
            result = response.json()
            
            if isinstance(result, dict) and "error" in result:
                time.sleep(result.get("estimated_time", 20))
                continue

            if isinstance(result, list):
                # Calculate Prob(Pos) - Prob(Neg) for institutional net sentiment
                scores = []
                for entry in result:
                    pos = next(item['score'] for item in entry if item['label'] == 'positive')
                    neg = next(item['score'] for item in entry if item['label'] == 'negative')
                    scores.append(pos - neg)
                
                net_sentiment = round(sum(scores) / len(scores), 4)
                
                # Dynamic State Mapping based on your Audit Log
                state = "STABLE"
                if abs(net_sentiment) > 0.45: state = "STRESS"
                if abs(net_sentiment) > 0.75: state = "ANOMALY"
                
                return net_sentiment, state
    except: pass
    return 0.0, "STABLE"

# 4. EXECUTION PULSE
def run_pulse():
    ts = datetime.now(timezone.utc)
    print(f"🛰️ ORION MESH PULSE | {ts.strftime('%H:%M:%S')} UTC")
    
    prices = fetch_market_data()
    sentiment, state = get_ai_sentiment()
    timestamp_str = ts.isoformat()

    # Log All 21 Assets
    for item in prices:
        item['timestamp'] = timestamp_str
        supabase.table("multi_asset_telemetry").insert(item).execute()

    # Log Governance State
    gov_msg = f"Orion Mesh Nominal | Sentiment: {sentiment}"
    if state != "STABLE":
        gov_msg = f"🚨 {state} DETECTED | Narrative Divergence: {sentiment}"

    supabase.table("sentinel_logs").insert({
        "sentiment": float(sentiment),
        "state": state,
        "timestamp": timestamp_str,
        "governance": gov_msg
    }).execute()
    
    print(f"✅ SYNC COMPLETE | Assets: {len(prices)} | Sentiment: {sentiment}")

if __name__ == "__main__":
    run_pulse()