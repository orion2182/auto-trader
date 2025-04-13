import ccxt
import pandas as pd
import os
import time
from datetime import datetime

exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def fetch_ohlcv_to_csv(symbol='BTC/USDT', timeframe='5m', since_days=90, save_path='data/ohlcv'):
    print(f"📥 Mengunduh data {symbol} ({timeframe}) selama {since_days} hari...")
    ms_per_candle = exchange.parse_timeframe(timeframe) * 1000
    limit = 1500  # batas maksimal per fetch
    now = exchange.milliseconds()
    since = now - since_days * 24 * 60 * 60 * 1000

    all_data = []

    while since < now:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
            if not ohlcv:
                break
            all_data.extend(ohlcv)
            since = ohlcv[-1][0] + ms_per_candle
            time.sleep(exchange.rateLimit / 1000)
        except Exception as e:
            print(f"⚠️ Error fetch: {e}")
            time.sleep(5)

    df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    os.makedirs(save_path, exist_ok=True)

    symbol_str = symbol.replace("/", "_")
    filename = f"{symbol_str}_{timeframe}.csv"
    filepath = os.path.join(save_path, filename)
    df.to_csv(filepath, index=False)
    print(f"✅ Data disimpan ke {filepath} — Total candle: {len(df)}")

# Contoh pemakaian langsung
if __name__ == "__main__":
    fetch_ohlcv_to_csv(symbol='BTC/USDT', timeframe='5m', since_days=90)
