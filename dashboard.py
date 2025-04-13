from risk_manager import get_risk_status
from datetime import datetime
import os
import json

TRADE_LOG = "data/trade_log.json"

def load_trade_log():
    if not os.path.exists(TRADE_LOG):
        return []
    with open(TRADE_LOG, "r") as f:
        return json.load(f)

def save_trade_log(log):
    with open(TRADE_LOG, "w") as f:
        json.dump(log, f, indent=2)

def log_trade(symbol, side, entry, sl, tp, result=None, pnl_pct=None):
    log = load_trade_log()
    log.append({
        "time": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "side": side,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "result": result,
        "pnl_pct": pnl_pct
    })
    save_trade_log(log)

def get_last_trade():
    log = load_trade_log()
    return log[-1] if log else None

def generate_dashboard_text():
    risk = get_risk_status()
    last = get_last_trade()
    text = "📈 **Auto Trading Dashboard**\n\n"

    if risk["cooldown"]:
        text += f"🚫 **Bot Status:** COOLDOWN aktif sampai `{risk['cooldown']}`\n"
    else:
        text += "✅ **Bot Status:** AKTIF & Siap Trading\n"

    text += f"🎯 **Win:** `{risk['wins']}` | ❌ **Loss:** `{risk['losses']}` | 🔄 **Drawdown:** `{risk['consecutive_losses']}x`\n"
    text += f"📉 **Daily Loss So Far:** `{round(risk['daily_loss'] * 100, 2)}%`\n\n"

    if last:
        text += f"🕒 **Last Trade**: `{last['symbol']} - {last['side'].upper()}`\n"
        text += f"💵 Entry: `{last['entry']}` | SL: `{last['sl']}` | TP: `{last['tp']}`\n"
        if last['result']:
            text += f"🏁 Result: `{last['result'].upper()}` | PnL: `{round(last['pnl_pct']*100, 2)}%`\n"

    text += f"\n📅 Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}` (WIB)"
    return text
