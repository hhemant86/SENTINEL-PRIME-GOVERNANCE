import asyncio
import os
import collections
import numpy as np
import yfinance as yf
import ccxt.async_support as ccxt
import aiohttp
from dotenv import load_dotenv
from supabase import acreate_client, AsyncClient
from datetime import datetime, timezone

load_dotenv()

class RegimeClassifier:
    def __init__(self, window_size=50):
        self.buffers = collections.defaultdict(lambda: collections.deque(maxlen=window_size))

    def classify(self, asset, price):
        buffer = self.buffers[asset]
        if len(buffer) < 20: 
            buffer.append(price)
            return "INITIALIZING", 0.0
        mean, std = np.mean(buffer), np.std(buffer)
        # Added safety for zero-standard deviation (flat markets)
        z_score = (price - mean) / std if std > 0.000001 else 0.0
        buffer.append(price)
        regime = "ANOMALY" if abs(z_score) >= 3.0 else "STRESS" if abs(z_score) >= 1.5 else "STABLE"
        return regime, round(float(z_score), 2)

class MultiAssetPulse:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.brain = RegimeClassifier()
        self.binance = ccxt.binance({
            'timeout': 30000, 
            'connector_kwargs': {'resolver': aiohttp.DefaultResolver()}
        })

    @classmethod
    async def create(cls):
        return cls(await acreate_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")))

    async def fetch_yahoo_price(self, ticker_symbol):
        """Thread-safe async fetch with triple-fallback (FastInfo -> 1m History -> 5d History)."""
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Attempt 1: Fast Info
            price = await asyncio.to_thread(lambda: ticker.fast_info.get('last_price'))
            
            # Attempt 2: 1-minute interval History
            if price is None or price == 0:
                data = await asyncio.to_thread(lambda: ticker.history(period="1d", interval="1m"))
                if not data.empty:
                    price = data['Close'].iloc[-1]
            
            # Attempt 3: 5-day broad History
            if price is None or price == 0:
                data = await asyncio.to_thread(lambda: ticker.history(period="5d"))
                if not data.empty:
                    price = data['Close'].iloc[-1]
                
            return float(price) if price else None
        except Exception:
            return None

    async def fetch_all(self):
        """Unified parallel fetch with Live Brokerage Alignment Calibration."""
        symbols = {
            "BTC": "BTC/USDT", 
            "XAU": "GC=F", 
            "XAG": "SI=F", 
            "MCX_GOLD": "GOLDBEES.NS",    
            "MCX_SILVER": "SILVERBEES.NS" 
        }
        
        results = []
        
        # 1. BTC Pulse (Binance)
        try:
            tick = await self.binance.fetch_ticker(symbols["BTC"])
            results.append({"asset": "BTC", "price": float(tick['last']), "source": "Binance"})
        except Exception:
            pass

        # 2. Parallel Fetch for Metals & MCX Proxies
        assets_to_fetch = ["XAU", "XAG", "MCX_GOLD", "MCX_SILVER"]
        tasks = [self.fetch_yahoo_price(symbols[a]) for a in assets_to_fetch]
        fetched_prices = await asyncio.gather(*tasks)
        
        for asset, price in zip(assets_to_fetch, fetched_prices):
            if price:
                calibrated_price = price
                
                # --- LIVE CALIBRATION (Aligned with Brokerage Data) ---
                if asset == "MCX_GOLD":
                    # Calibrating GOLDBEES to 154k range
                    calibrated_price = price * 1240  
                
                elif asset == "MCX_SILVER":
                    # Calibrating SILVERBEES to 324k range
                    calibrated_price = price * 1175  
                
                results.append({
                    "asset": asset, 
                    "price": float(calibrated_price), 
                    "source": "yfinance"
                })
                
        return results

    async def run(self):
        print("\n🚀 SENTINEL ENGINE: MULTI-ASSET CORE LIVE (BROKERAGE ALIGNED)\n" + "═"*60)
        while True:
            payload = await self.fetch_all()
            for data in payload:
                regime, z_score = self.brain.classify(data['asset'], data['price'])
                data.update({
                    'regime': regime, 
                    'z_score': z_score, 
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                try:
                    await self.supabase.table("multi_asset_telemetry").insert(data).execute()
                    print(f"📡 SYNC | {data['asset']:<10} | Price: {data['price']:,.2f} | [{regime}]")
                except Exception as e:
                    print(f"❌ Cloud Sync Error: {e}")
            
            # 30s Governance Heartbeat
            await asyncio.sleep(30)

if __name__ == "__main__":
    async def main():
        engine = await MultiAssetPulse.create()
        try: 
            await engine.run()
        finally: 
            await engine.binance.close()

    async def safe_run():
        """Resilient entry point to handle network drops."""
        while True:
            try:
                await main()
            except Exception as e:
                print(f"🔄 Restarting Engine in 10s due to connection drop: {e}")
                await asyncio.sleep(10)

    asyncio.run(safe_run())