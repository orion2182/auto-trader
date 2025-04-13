import ccxt
import math
import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi API
exchange = ccxt.binance({
    'apiKey': os.getenv("BINANCE_API_KEY"),
    'secret': os.getenv("BINANCE_API_SECRET"),
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# Config
RISK_PER_TRADE = 0.01  # 1%
TRAILING_STOP_PCT = 0.005  # 0.5%
TAKE_PROFIT_RR = 2  # Risk:Reward 1:2

def get_balance():
    balance = exchange.fetch_balance({'type': 'future'})
    usdt_balance = balance['total']['USDT']
    return usdt_balance

def calculate_position_size(symbol, entry_price, stop_loss_price):
    balance = get_balance()
    risk_amount = RISK_PER_TRADE * balance
    sl_distance = abs(entry_price - stop_loss_price)
    qty = risk_amount / sl_distance
    market = exchange.market(symbol)
    precision = market['precision']['amount']
    return round(qty, precision)

def place_order(symbol, signal, current_price):
    side = 'buy' if signal == 'long' else 'sell'
    opposite = 'sell' if signal == 'long' else 'buy'

    # SL & TP logic
    sl_pct = 0.005  # 0.5% dari harga masuk
    sl_price = current_price * (1 - sl_pct) if signal == 'long' else current_price * (1 + sl_pct)
    tp_price = current_price + TAKE_PROFIT_RR * (current_price - sl_price) if signal == 'long' else current_price - TAKE_PROFIT_RR * (sl_price - current_price)

    # Size berdasarkan risk
    qty = calculate_position_size(symbol, current_price, sl_price)

    print(f"🔫 Executing {signal.upper()} {qty} {symbol} at {current_price}")

    # Order market entry
    exchange.create_order(
        symbol=symbol,
        type='market',
        side=side,
        amount=qty
    )

    # Pasang SL/TP
    exchange.create_order(
        symbol=symbol,
        type='take_profit_market',
        side=opposite,
        amount=qty,
        params={
            'stopPrice': round(tp_price, 2),
            'closePosition': True
        }
    )

    exchange.create_order(
        symbol=symbol,
        type='stop_market',
        side=opposite,
        amount=qty,
        params={
            'stopPrice': round(sl_price, 2),
            'closePosition': True
        }
    )

    # Trailing Stop
    trailing_trigger = current_price * (1 + TRAILING_STOP_PCT) if signal == 'long' else current_price * (1 - TRAILING_STOP_PCT)

    exchange.create_order(
        symbol=symbol,
        type='trailing_stop_market',
        side=opposite,
        amount=qty,
        params={
            'activationPrice': round(trailing_trigger, 2),
            'callbackRate': TRAILING_STOP_PCT * 100,
            'closePosition': True
        }
    )

    return {
        'symbol': symbol,
        'side': signal,
        'qty': qty,
        'entry': current_price,
        'sl': round(sl_price, 2),
        'tp': round(tp_price, 2)
    }
