import time
from scanner import scan_pairs_for_signals
from order_executor import execute_trade
from risk_manager import check_cooldown, update_drawdown_status
from dashboard import update_dashboard
from config import TRADE_PAIRS, SCAN_INTERVAL


def main():
    print("🚀 Auto Trading Bot Started...")
    
    while True:
        for pair in TRADE_PAIRS:
            if check_cooldown(pair):
                print(f"⚠️ Cooldown active for {pair}, skipping.")
                continue

            signal = scan_pairs_for_signals(pair)
            if signal:
                result = execute_trade(pair, signal)
                update_drawdown_status(result)
                update_dashboard(pair, signal, result)

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
