import ccxt
import pandas as pd
import ta
from datetime import datetime, timezone

exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def fetch_ohlcv(symbol, timeframe='5m', limit=100):
    data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Jakarta')
    return df

def calculate_indicators(df):
    df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['ema200'] = ta.trend.ema_indicator(df['close'], window=200)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    df['volume_avg'] = df['volume'].rolling(window=20).mean()
    return df

def check_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # EMA Crossover
    long_condition = prev['ema20'] < prev['ema50'] and last['ema20'] > last['ema50']
    short_condition = prev['ema20'] > prev['ema50'] and last['ema20'] < last['ema50']

    # Trend Filter
    in_uptrend = last['close'] > last['ema200']
    in_downtrend = last['close'] < last['ema200']

    # Volume spike
    volume_spike = last['volume'] > 1.5 * last['volume_avg']

    # Volatility check
    atr_threshold = last['atr'] > 0.002 * last['close']  # ATR > 0.2% harga

    # Combine conditions
    long_signal = long_condition and in_uptrend and volume_spike and atr_threshold
    short_signal = short_condition and in_downtrend and volume_spike and atr_threshold

    return 'long' if long_signal else 'short' if short_signal else None

def scan_pairs_for_signals(pairs):
    signals = []
    for symbol in pairs:
        try:
            df = fetch_ohlcv(symbol, '5m')
            df = calculate_indicators(df)
            signal = check_signal(df)
            if signal:
                signals.append({'symbol': symbol, 'signal': signal, 'timestamp': datetime.now(timezone.utc)})
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
    return signals
