# SENTINEL PRIME v2.0
![Supabase Custom Badge](https://img.shields.io/badge/Cloud_Node-Active-green?style=for-the-badge&logo=supabase)
![Streamlit Badge](https://img.shields.io/badge/Dashboard-Live-FF4B4B?style=for-the-badge&logo=streamlit)

### Institutional Risk Governance: Cloud-Native AI Sentiment & Quantitative Telemetry

**Live Dashboard:** [Access Sentinel Command](https://sentinel-prime-governance.streamlit.app/)

**Sentinel Prime** is a distributed risk governance layer designed to operate above active trading strategies. It synchronizes local GPU-accelerated AI processing (Edge Computing) with a Global Cloud Vault (Supabase) to enforce capital preservation through real-time volatility analysis and narrative intelligence.

---

## 🏛️ Governance Philosophy
In high-stakes environments, human judgment often fails at the exact moment of market instability. Sentinel Prime enforces a "Triple-Lock" security protocol:
1. **Edge Intelligence:** Local FinBERT analysis for zero-latency sentiment extraction.
2. **Cloud Persistence:** Secure, centralized SQL node ensuring a unified "Source of Truth" for global monitoring.
3. **Predictive Enforcement:** ML-driven look-ahead metrics to anticipate regime shifts before they occur.

[Image of a cloud computing architecture for an AI application]

---

## 🧠 System Architecture

### 1. Edge Engine (Quant & NLP)
The core engine runs on local hardware to leverage GPU acceleration for:
* **Market Regime Classification:** Statistical Z-Score modeling to classify states as STABLE, STRESS, or ANOMALY.
* **Narrative Validation:** Real-time sentiment extraction from institutional news feeds via **FinBERT Transformers**.

### 2. Cloud Vault (Supabase Integration)
The system utilizes a **Relational Cloud Infrastructure** for data integrity:
* **Live Sync:** Telemetry is pushed to a remote SQL node every 30 seconds.
* **Persistence:** Historical audit logs are stored securely, independent of the local machine's state.

### 3. Predictive Command Center (ML Layer)
The dashboard implements a **Linear Regression** engine for real-time trend forecasting:
* **30s Forecast:** Analyzes a rolling window of the last 10 cloud entries to predict immediate volatility.
* **Visual Intelligence:** Dynamic Plotly streams cross-referencing price dispersion against AI sentiment.

[Image of a software architecture diagram showing core engines connecting to advanced AI and Cloud layers]

---

## 📂 Project Structure
```text
SENTINEL_PRIME_GOVERNANCE/
├── ai_research/             # Deep Learning & Edge Engine
│   └── RnD/scripts/research/ai_sentiment_sentinel.py
├── dashboard/               # Cloud Command Center (Streamlit)
│   └── RnD/scripts/research/dashboard.py
├── engine/                  # Core Quantitative Logic
│   ├── live_price_sentinel.py
│   └── kill_switch.py
├── .streamlit/              # Cloud Configuration
│   └── secrets.toml         # Secure API Credentials
├── requirements.txt         # Environment Passport (Cloud Standard)
└── .gitignore               # Security & Hygiene
🛠️ Technology Stack
AI/NLP: PyTorch, Transformers (FinBERT)

Database: Supabase (PostgreSQL)

Predictive ML: Scikit-Learn (Linear Regression)

Visualization: Streamlit, Plotly

Infrastructure: GitHub Actions, Streamlit Cloud

🚀 Deployment & Usage
1. Launch the Edge Engine (ASUS TUF)
PowerShell

python ai_research/RnD/scripts/research/ai_sentiment_sentinel.py
2. Access Global Dashboard
Access the Command Center via the live Streamlit URL to view real-time risk telemetry from any device.
## 🛰️ Future Roadmap: Sentinel Prime v3.0
The next phase of Sentinel Prime focuses on moving from **Governance-as-Monitoring** to **Governance-as-Execution**:

* **Adaptive Circuit Breakers:** Implementing a "Dynamic Slippage" engine that adjusts order execution speed based on the Live Z-Score.
* **Narrative Clustering:** Upgrading the AI Layer to cluster global news into "Market Themes" using Unsupervised Learning (K-Means) to detect structural regime shifts.
* **Distributed Governance Nodes:** Enabling multiple "Observer Engines" to push to the same Cloud Vault, allowing for cross-asset correlation analysis (e.g., Gold vs. USD divergence).
* **Institutional Alerting:** Integrating **Twilio/SendGrid** via Supabase Edge Functions to send SMS/Email alerts the millisecond an ANOMALY state is triggered.

👤 Author
Hemant Verma Quantitative Risk Architect Building governance-first financial systems at the intersection of AI, Market Microstructure, and Cloud Infrastructure.