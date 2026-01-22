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
        z_score = (price - mean) / std if std > 0.0001 else 0.0
        buffer.append(price)
        regime = "ANOMALY" if abs(z_score) >= 3.0 else "STRESS" if abs(z_score) >= 1.5 else "STABLE"
        return regime, round(float(z_score), 2)

class MultiAssetPulse:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.brain = RegimeClassifier()
        # Hardened for DNS Stability
        self.binance = ccxt.binance({
            'timeout': 30000, 
            'connector_kwargs': {'resolver': aiohttp.DefaultResolver()}
        })

    @classmethod
    async def create(cls):
        return cls(await acreate_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")))

    async def fetch_all(self):
        """Unified parallel fetch for Phase 0 assets."""
        # Crypto, Global Metals, MCX Proxies
        symbols = {"BTC": "BTC/USDT", "XAU": "GC=F", "XAG": "SI=F", 
                   "MCX_GOLD": "GOLDBEES.NS", "MCX_SILVER": "SILVERBEES.NS"}
        
        results = []
        # BTC Pulse
        try:
            tick = await self.binance.fetch_ticker(symbols["BTC"])
            results.append({"asset": "BTC", "price": tick['last'], "source": "Binance"})
        except: pass

        # Yahoo Pulse (Metals & MCX)
        for asset in ["XAU", "XAG", "MCX_GOLD", "MCX_SILVER"]:
            try:
                ticker = symbols[asset]
                price = await asyncio.to_thread(lambda: yf.Ticker(ticker).fast_info['last_price'])
                mult = 1200 if asset == "MCX_GOLD" else 1100 if asset == "MCX_SILVER" else 1.0
                results.append({"asset": asset, "price": price * mult, "source": "yfinance"})
            except: pass
        return results

    async def run(self):
        print("\n🚀 SENTINEL ENGINE: FRESH START (PHASE 0)\n" + "═"*50)
        while True:
            payload = await self.fetch_all()
            for data in payload:
                regime, z_score = self.brain.classify(data['asset'], data['price'])
                data.update({'regime': regime, 'z_score': z_score, 'timestamp': datetime.now(timezone.utc).isoformat()})
                try:
                    await self.supabase.table("multi_asset_telemetry").insert(data).execute()
                    print(f"📡 SYNC | {data['asset']:<10} | Price: {data['price']:,.2f} | [{regime}]")
                except Exception as e:
                    print(f"❌ Cloud Error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    async def main():
        engine = await MultiAssetPulse.create()
        try: await engine.run()
        finally: await engine.binance.close()
    asyncio.run(main())