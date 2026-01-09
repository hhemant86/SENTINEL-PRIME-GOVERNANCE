import pandas as pd
import numpy as np
import time
from datetime import datetime
import os
import feedparser
import ssl

# --- 1. INITIALIZATION & SECURITY ---
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Institutional Feed Quorum
FEEDS = {
    'Yahoo Finance': "https://finance.yahoo.com/news/rssindex",
    'Reuters Macro': "https://ir.thomsonreuters.com/rss/news-releases.xml?items=15",
    'Kitco Gold': "https://www.kitco.com/rss/news.xml",
    'ZeroHedge': "http://feeds.feedburner.com/zerohedge/feed"
}
CRITICAL_WORDS = ['war', 'conflict', 'crisis', 'geopolitical', 'sanctions', 'attack']

# --- 2. BEHAVIORAL GUARDRAIL LAYER ---
class HumanGovernance:
    def __init__(self):
        self.anomaly_counter = 0
        self.cooldown_active = False
        self.cooldown_start_time = None
        self.cooldown_duration = 300 # 5 Min for testing

    def evaluate_human_risk(self, market_state, news_risk):
        if self.cooldown_active:
            elapsed = time.time() - self.cooldown_start_time
            if elapsed < self.cooldown_duration:
                return f"⛔ LOCK ACTIVE: Cognitive Reset Required. [{int(self.cooldown_duration-elapsed)}s]"
            self.cooldown_active = False
            self.anomaly_counter = 0

        # Escalate if Market is Anomaly OR News is Critical
        if market_state == "ANOMALY_DETECTION" or news_risk == "CRITICAL":
            self.anomaly_counter += 1
        else:
            self.anomaly_counter = max(0, self.anomaly_counter - 1)

        if self.anomaly_counter >= 5:
            self.cooldown_active = True
            self.cooldown_start_time = time.time()
            return "🚨 ALERT: Behavioral Stress Threshold Breached. SYSTEM LOCKING..."
        
        return "🟢 Human State: Nominal"

# --- 3. NEWS QUORUM LAYER ---
def get_news_risk():
    extreme_sources = set()
    for name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                if any(w in entry.title.lower() for w in CRITICAL_WORDS):
                    extreme_sources.add(name)
        except: continue
    
    quorum = len(extreme_sources)
    return "CRITICAL" if quorum >= 2 else "WARNING" if quorum == 1 else "NORMAL"

# --- 4. THE MASTER ENGINE (FINALIZED) ---
def run_integrated_sentinel():
    gov = HumanGovernance()
    
    # 🏛️ INSTITUTIONAL PATH LOCK (Absolute Path)
    results_dir = r'C:\Users\Asus\OneDrive\Desktop\BILLIONAIRE_ROADMAP\results'
    log_path = os.path.join(results_dir, 'integrated_audit.csv')
    
    # Ensure directory exists before writing
    if not os.path.exists(results_dir): 
        os.makedirs(results_dir)

    print("============================================================")
    print("🛰️  SENTINEL PRIME: QUANT + QUAL + BEHAVIORAL GOVERNANCE")
    print("============================================================")

    while True:
        # A. Market Logic (Simulated Z-Score)
        mock_z = np.random.uniform(0, 4.5)
        market_state = "ANOMALY_DETECTION" if mock_z > 3.0 else "STRESS" if mock_z > 2.0 else "NEUTRAL"
        
        # B. News Logic (Live Quorum)
        news_risk = get_news_risk()

        # C. Human Logic (Behavioral Guardrail)
        behavior_report = gov.evaluate_human_risk(market_state, news_risk)

        # D. Unified Output
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Market: {market_state} ({mock_z:.2f}) | News: {news_risk}")
        print(f"👉 {behavior_report}")
        print("-" * 60)

        # E. Forensic Logging (Using the log_path variable)
        log_data = {
            'timestamp': timestamp,
            'market_z': round(mock_z, 2),
            'market_state': market_state,
            'news_risk': news_risk,
            'behavior_report': behavior_report
        }
        
        # Use log_path here to ensure consistency
        pd.DataFrame([log_data]).to_csv(log_path, mode='a', index=False, header=not os.path.exists(log_path))

        time.sleep(15)

if __name__ == "__main__":
    run_integrated_sentinel()
