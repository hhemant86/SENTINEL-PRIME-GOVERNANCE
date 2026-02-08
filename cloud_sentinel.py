import time
import os
from SENTINEL_PRIME.core_logic.governor import SentinelGovernor
from supabase import create_client

# Initialize Cloud Connection
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)
gov = SentinelGovernor()

def run_cloud_governance():
    print("🛰️ SENTINEL PRIME CLOUD ENGINE: ACTIVE")
    while True:
        try:
            # 1. Pull the latest Advisory from ORION (stored in Supabase)
            response = supabase.table("orion_advisory").select("*").order("timestamp", desc=True).limit(1).execute()
            
            if response.data:
                advisory = response.data[0]
                # 2. Adjudicate
                command, rationale = gov.adjudicate(advisory)
                
                # 3. Push Law back to Cloud for the Dashboard to see
                supabase.table("governance_commands").insert({
                    "command": command,
                    "rationale": rationale,
                    "timestamp": "now()"
                }).execute()
                
            time.sleep(30) # Governance Heartbeat
        except Exception as e:
            print(f"Cloud Sync Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_cloud_governance()