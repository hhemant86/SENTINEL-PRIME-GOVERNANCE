"""
SENTINEL PRIME | Executive Policy Governor v3.0
Deterministic Adjudication for XAU/USD Treasury Operations.
"""
import os
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class SentinelGovernor:
    def __init__(self):
        # 📜 Institutional SOP Clause 4.3 Thresholds
        self.RED_ZONE = 0.70    # Force FREEZE
        self.YELLOW_ZONE = 0.30 # Force REDUCE
        
        # Paths & Connections
        self.audit_path = os.path.join("trust_layer", "forensic_vault.csv")
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_KEY")
        )

    def adjudicate(self, advisory_vector):
        """
        The Deterministic Verdict Engine.
        Processes SRI (Systemic Risk Index) into a Global Lawful Command.
        """
        # Ensure input is safe
        sri = float(advisory_vector.get('sri_index', 0))
        timestamp = advisory_vector.get('timestamp', datetime.now(timezone.utc).isoformat())

        # --- THE LAW OF CAPITAL PRESERVATION ---
        if sri >= self.RED_ZONE:
            verdict = "🔴 FREEZE"
            rationale = f"SOP BREACH: Systemic Risk ({sri*100}%) exceeds 70% threshold."
        elif sri >= self.YELLOW_ZONE:
            verdict = "🟡 REDUCE"
            rationale = "VOLATILITY ALERT: Yellow Zone - Manual de-leveraging required."
        else:
            verdict = "🟢 ALLOW"
            rationale = "NOMINAL: Market conditions within institutional bounds."

        # --- DUAL PERSISTENCE STRATEGY ---
        # 1. Local Forensic Log (For physical audit)
        self._log_local_forensic(verdict, rationale, sri)
        
        # 2. Cloud Governance Push (For 'Always-On' Dashboard)
        self._push_to_cloud(verdict, rationale, sri)

        return verdict, rationale

    def _log_local_forensic(self, verdict, rationale, sri):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": verdict,
            "sri_index": sri,
            "rationale": rationale
        }
        df = pd.DataFrame([entry])
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.audit_path), exist_ok=True)
        df.to_csv(self.audit_path, mode='a', index=False, header=not os.path.exists(self.audit_path))

    def _push_to_cloud(self, verdict, rationale, sri):
        """Updates the 'governance_commands' table for the Streamlit dashboard."""
        try:
            payload = {
                "command": verdict,
                "rationale": rationale,
                "sri_at_execution": sri
            }
            self.supabase.table("governance_commands").insert(payload).execute()
        except Exception as e:
            print(f"⚠️ Cloud Sync Failure: {e}")

if __name__ == "__main__":
    # Test Mock: Simulating an ORION Advisory Vector
    gov = SentinelGovernor()
    mock_vector = {"sri_index": 0.85} 
    verdict, why = gov.adjudicate(mock_vector)
    print(f"VERDICT: {verdict} | REASON: {why}")