import pandas as pd
import numpy as np
import time
from datetime import datetime
import os
import feedparser
import ssl
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# --- 1. CENTRALIZED PATH MANAGEMENT ---
# --- 1. FIXED PATH MANAGEMENT ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Correct move to root: research -> scripts -> RnD -> ai_research (4 levels)
LOGS_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../../../logs"))
LOG_PATH = os.path.join(LOGS_DIR, "integrated_audit.csv")

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

# Auto-create the centralized logs directory if it doesn't exist
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

# --- AI SETUP ---
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

FEEDS = {
    'Yahoo Finance': "https://finance.yahoo.com/news/rssindex",
    'Reuters Macro': "https://ir.thomsonreuters.com/rss/news-releases.xml?items=15",
    'Kitco Gold': "https://www.kitco.com/rss/news.xml"
}

class HumanGovernance:
    def __init__(self):
        self.anomaly_counter = 0
        self.cooldown_active = False
        self.cooldown_start_time = None
        self.cooldown_duration = 300 

    def evaluate_risk(self, market_state, sentiment_score):
        if self.cooldown_active:
            elapsed = time.time() - self.cooldown_start_time
            if elapsed < self.cooldown_duration:
                return f"⛔ LOCK ACTIVE. [{int(self.cooldown_duration-elapsed)}s]"
            self.cooldown_active = False
            self.anomaly_counter = 0

        # Divergence Logic: Price moves without News support
        if market_state == "ANOMALY" and abs(sentiment_score) < 0.2:
            self.anomaly_counter += 2 
        elif market_state == "ANOMALY":
            self.anomaly_counter += 1
        else:
            self.anomaly_counter = max(0, self.anomaly_counter - 1)

        if self.anomaly_counter >= 5:
            self.cooldown_active = True
            self.cooldown_start_time = time.time()
            return "🚨 ALERT: SYSTEM LOCKING - High Divergence Detected."
        
        return "🟢 State: Nominal"

def get_live_sentiment():
    headlines = []
    for url in FEEDS.values():
        try:
            feed = feedparser.parse(url)
            headlines.extend([entry.title for entry in feed.entries[:3]])
        except: continue
    
    if not headlines: return 0.0
    
    inputs = tokenizer(headlines, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # FinBERT Classes: 0:Pos, 1:Neg, 2:Neut
    avg_pos = probs[:, 0].mean().item()
    avg_neg = probs[:, 1].mean().item()
    return round(avg_pos - avg_neg, 4)

def run_sentinel_prime():
    gov = HumanGovernance()
    print(f"\n{'='*60}\n{'SENTINEL PRIME v2.0 | AI + QUANT + GOVERNANCE':^60}\n{'='*60}")
    print(f"📡 Shared Data Node: {LOG_PATH}")

    while True:
        # A. Quant Math (Z-Score Simulation)
        mock_z = np.random.uniform(0, 4.0) 
        market_state = "ANOMALY" if mock_z > 3.0 else "STRESS" if mock_z > 2.0 else "STABLE"
        
        # B. AI Qualitative Logic
        sentiment_score = get_live_sentiment()
        
        # C. Governance Verification
        report = gov.evaluate_risk(market_state, sentiment_score)

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] Market: {market_state} ({mock_z:.2f}) | Sentiment: {sentiment_score}")
        print(f"👉 {report}\n" + "-"*60)

        # D. Forensic Data Persistence
        log_entry = pd.DataFrame([{
            'Timestamp': ts, 'Z-Score': mock_z, 'Sentiment': sentiment_score, 
            'State': market_state, 'Governance': report
        }])
        
        # Write to the central root log file
        log_entry.to_csv(LOG_PATH, mode='a', index=False, header=not os.path.exists(LOG_PATH))
        time.sleep(30)

if __name__ == "__main__":
    run_sentinel_prime()