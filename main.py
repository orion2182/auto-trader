import time
from scanner import scan_pairs_for_signals
from order_executor import execute_trade, place_order
from risk_manager import check_cooldown, update_drawdown_status
from dashboard import update_dashboard
from config import TRADE_PAIRS, SCAN_INTERVAL
import ccxt  # Ensure you have ccxt imported if you're using it

def main():
    print("🚀 Auto Trading Bot Started...")
    
    while True:
        scan_result = []  # Initialize scan_result to store signals

        for pair in TRADE_PAIRS:
            if check_cooldown(pair):
                print(f"⚠️ Cooldown active for {pair}, skipping.")
                continue

            signals = scan_pairs_for_signals([pair])  # Pass a list of pairs
            if signals:
                scan_result.extend(signals)  # Collect all signals

                for signal in signals:
                    symbol = signal['symbol']
                    action = signal['signal']
                    price = exchange.fetch_ticker(symbol)['last']
                    result = place_order(symbol, action, price)
                    print(f"✅ Order Executed: {result}")

                    # Update drawdown status and dashboard for each signal
                    update_drawdown_status(result)
                    update_dashboard(symbol, action, result)

        time.sleep(SCAN_INTERVAL)  # Sleep after processing all pairs

if __name__ == "__main__":
    main()
