# SENTINEL PRIME v2.0
### Institutional Risk Governance Engine: AI Sentiment + Quantitative Telemetry

**Sentinel Prime** is an institutional-grade risk governance layer designed to operate above active trading strategies. It enforces capital preservation by synchronizing real-time quantitative volatility (Z-Scores) with AI-driven narrative intelligence (FinBERT).

---

## 🏛️ Governance Philosophy
In high-stakes environments, markets fail slowly, but human judgment fails suddenly. Sentinel Prime exists to:
1. **Detect Regime Instability:** Real-time classification of market states.
2. **Validate Narratives:** Cross-referencing price anomalies against global news sentiment.
3. **Enforce Behavioral Circuit Breakers:** Implementing automated "Cognitive Cooldowns" when divergence exceeds safe thresholds.



---

## 🧠 System Architecture

### 1. Market Regime Classification (Quant Layer)
The engine performs rolling statistical analysis of price volatility, classifying market regimes into:
* **STABLE:** Low dispersion, high predictability.
* **STRESS:** Elevated volatility, requiring reduced position sizing.
* **ANOMALY:** Extreme statistical deviation (Z-Score > 3.0).

### 2. AI Sentiment Divergence (R&D Layer)
Using **FinBERT (NLP Transformers)**, the system analyzes live feeds from Yahoo Finance, Reuters, and Kitco.
* **Ghost Move Detection:** If the Quant Layer detects an **ANOMALY** but the AI Layer reports **NEUTRAL** sentiment, the system flags a "Narrative Divergence" and triggers a protective lock.

### 3. Predictive Intelligence (ML Layer)
A Linear Regression module forecasts the next 30 seconds of volatility based on the previous 10 data points, providing the operator with a "Look-Ahead" risk metric.

---

## 📂 Verified Project Structure
```text
SENTINEL_PRIME_GOVERNANCE/
├── ai_research/             # Deep Learning Research
│   └── RnD/scripts/research/ai_sentiment_sentinel.py
├── dashboard/               # Visual Intelligence Layer
│   └── RnD/scripts/research/dashboard.py
├── engine/                  # Core Quantitative Logic
│   ├── live_price_sentinel.py
│   └── kill_switch.py
├── logs/                    # Shared Centralized Data Node
│   └── integrated_audit.csv
├── requirements.txt         # Environment Passport
└── .gitignore               # Institutional Standards
🛠️ Technology Stack
Language: Python 3.12+

AI/NLP: PyTorch, Transformers (FinBERT)

Predictive ML: Scikit-Learn (Linear Regression)

Visualization: Streamlit, Plotly

Data Handling: Pandas, NumPy, Shared-Node Logging

🚀 Deployment & Usage
Install Dependencies:

Bash

pip install -r requirements.txt
Launch the Engine:

Bash

python ai_research/RnD/scripts/research/ai_sentiment_sentinel.py
Launch the Command Center:

Bash

streamlit run dashboard/RnD/scripts/research/dashboard.py
👤 Author
Hemant Verma Quantitative Risk Architect Building governance-first financial systems at the intersection of AI, Market Microstructure, and Human Integrity.

⚠️ Disclaimer: This project is for research and governance design purposes. It does not constitute financial advice.