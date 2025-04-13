import pandas as pd
import os
from strategy import calculate_indicators, check_signal
from dashboard import log_trade

DATA_PATH = "data/ohlcv/"
RESULTS_PATH = "data/backtest_results/"

SL_PCT = 0.005  # 0.5%
RR = 2  # TP jarak = 2x SL
TRAILING_STOP = False  # Bisa diaktifkan nanti

def load_data(symbol):
    path = os.path.join(DATA_PATH, f"{symbol}_5m.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data tidak ditemukan: {path}")
    df = pd.read_csv(path, parse_dates=['timestamp'])
    return df

def simulate_trade(df, i, signal):
    entry = df.loc[i + 1, 'close']
    sl = entry * (1 - SL_PCT) if signal == 'long' else entry * (1 + SL_PCT)
    tp = entry + (entry - sl) * RR if signal == 'long' else entry - (sl - entry) * RR
    qty = 1  # asumsi 1 unit untuk simulasi

    for j in range(i + 2, len(df)):
        high = df.loc[j, 'high']
        low = df.loc[j, 'low']

        if signal == 'long':
            if low <= sl:
                return -SL_PCT
            if high >= tp:
                return SL_PCT * RR
        else:
            if high >= sl:
                return -SL_PCT
            if low <= tp:
                return SL_PCT * RR
    return 0  # trade masih berjalan atau tidak tersentuh

def backtest(symbol):
    df = load_data(symbol)
    df = calculate_indicators(df)
    results = []

    for i in range(50, len(df) - 30):  # skip awal dan akhir
        sliced = df.iloc[:i + 1]
        signal = check_signal(sliced)
        if not signal:
            continue

        pnl_pct = simulate_trade(df, i, signal)
        results.append({
            "timestamp": df.loc[i, 'timestamp'],
            "symbol": symbol,
            "signal": signal,
            "entry_price": df.loc[i + 1, 'close'],
            "result": "TP" if pnl_pct > 0 else "SL" if pnl_pct < 0 else "NONE",
            "pnl_pct": round(pnl_pct * 100, 2)
        })

    results_df = pd.DataFrame(results)
    out_file = os.path.join(RESULTS_PATH, f"{symbol}_backtest.csv")
    results_df.to_csv(out_file, index=False)

    win = results_df[results_df['result'] == "TP"]
    loss = results_df[results_df['result'] == "SL"]
    print(f"📊 Backtest {symbol}:")
    print(f"- Total Trade: {len(results_df)}")
    print(f"- Win: {len(win)} ({round(len(win)/len(results_df)*100, 2)}%)")
    print(f"- Loss: {len(loss)}")
    print(f"- Net PnL: {round(results_df['pnl_pct'].sum(), 2)}%")
