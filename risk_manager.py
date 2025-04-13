import json
import os
from datetime import datetime, timedelta

RISK_FILE = "data/risk_state.json"

DEFAULT_STATE = {
    "wins": 0,
    "losses": 0,
    "consecutive_losses": 0,
    "cooldown_until": None,
    "daily_loss": 0.0,
    "last_trade_date": None
}

MAX_CONSECUTIVE_LOSSES = 3
DAILY_LOSS_LIMIT = 0.03  # 3% dari modal

def load_risk_state():
    if not os.path.exists(RISK_FILE):
        return DEFAULT_STATE.copy()
    with open(RISK_FILE, "r") as f:
        return json.load(f)

def save_risk_state(state):
    with open(RISK_FILE, "w") as f:
        json.dump(state, f, indent=2)

def update_after_trade(profit_percent):
    state = load_risk_state()
    today = datetime.utcnow().date()

    if state["last_trade_date"] != str(today):
        state["daily_loss"] = 0.0
        state["consecutive_losses"] = 0
        state["last_trade_date"] = str(today)

    if profit_percent > 0:
        state["wins"] += 1
        state["consecutive_losses"] = 0
    else:
        state["losses"] += 1
        state["consecutive_losses"] += 1
        state["daily_loss"] += abs(profit_percent)

    # Cek apakah perlu cooldown
    if state["consecutive_losses"] >= MAX_CONSECUTIVE_LOSSES or state["daily_loss"] >= DAILY_LOSS_LIMIT:
        cooldown_hours = 12
        state["cooldown_until"] = (datetime.utcnow() + timedelta(hours=cooldown_hours)).isoformat()
        print(f"⚠️ Cooldown diaktifkan sampai {state['cooldown_until']}")

    save_risk_state(state)

def is_in_cooldown():
    state = load_risk_state()
    if state["cooldown_until"]:
        until = datetime.fromisoformat(state["cooldown_until"])
        if datetime.utcnow() < until:
            return True
        else:
            state["cooldown_until"] = None
            save_risk_state(state)
    return False

def get_risk_status():
    state = load_risk_state()
    return {
        "wins": state["wins"],
        "losses": state["losses"],
        "consecutive_losses": state["consecutive_losses"],
        "cooldown": state["cooldown_until"],
        "daily_loss": state["daily_loss"]
    }
