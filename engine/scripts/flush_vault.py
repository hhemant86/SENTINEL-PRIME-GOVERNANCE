import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def clear_table():
    print("⚠️  INITIATING VAULT PURGE...")
    # This deletes everything where asset is not null (which is every row)
    response = supabase.table("multi_asset_telemetry").delete().neq("asset", "null").execute()
    print("✅ VAULT CLEARED. Sentinel is now a Blank Slate.")

if __name__ == "__main__":
    clear_table()