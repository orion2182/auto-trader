import time
import os
import ccxt  # Ensure you have ccxt imported if you're using it
from scanner import scan_pairs_for_signals
from order_executor import execute_trade, place_order
from risk_manager import check_cooldown, update_drawdown_status, is_in_cooldown, update_after_trade
from dashboard import update_dashboard, generate_dashboard_text, get_last_trade
from config import TRADE_PAIRS, SCAN_INTERVAL
from backtest_engine import backtest
import discord
from discord.ext import commands
import asyncio
from ohlcv_downloader import fetch_ohlcv_to_csv

# Initialize the exchange
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def main():
    print("🚀 Auto Trading Bot Started...")
    
    while True:
        if is_in_cooldown():
            print("⛔ Bot sedang cooldown, skip trade.")
            time.sleep(SCAN_INTERVAL)  # Sleep before checking again
            continue

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

                    # Example: TP +2%, SL -1%
                    update_after_trade(profit_percent=0.02)  # after TP
                    update_after_trade(profit_percent=-0.01)  # after SL

        time.sleep(SCAN_INTERVAL)  # Sleep after processing all pairs

if __name__ == "__main__":
    main()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Whitelist user (replace with your user ID)
AUTHORIZED_USERS = [int(os.getenv("DISCORD_ALLOWED_USER_ID"))]

def is_authorized(ctx):
    return ctx.author.id in AUTHORIZED_USERS

@bot.event
async def on_ready():
    print(f"✅ Bot Discord aktif sebagai {bot.user}")

@bot.command()
async def status(ctx):
    if not is_authorized(ctx): return
    msg = generate_dashboard_text()
    await ctx.send(msg)

@bot.command()
async def lasttrade(ctx):
    if not is_authorized(ctx): return
    last = get_last_trade()
    if last:
        await ctx.send(f"🕒 Trade Terakhir:\n{last}")
    else:
        await ctx.send("Belum ada histori trade.")

@bot.command()
async def download(ctx, symbol: str, tf: str, days: int):
    if not is_authorized(ctx): return
    await ctx.send(f"📥 Mulai download OHLCV {symbol} ({tf}, {days} hari)...")
    try:
        fetch_ohlcv_to_csv(symbol.replace("_", "/"), tf, days)
        await ctx.send(f"✅ Data {symbol}_{tf} berhasil disimpan!")
    except Exception as e:
        await ctx.send(f"❌ Gagal download: {e}")

@bot.command()
async def backtestcmd(ctx, symbol: str):
    if not is_authorized(ctx): return
    await ctx.send(f"⚙️ Mulai backtest {symbol}...")
    try:
        backtest(symbol.replace("_", "/"))
        await ctx.send(f"✅ Backtest selesai. Cek hasil CSV di `/data/backtest_results/{symbol}_backtest.csv`.")
    except Exception as e:
        await ctx.send(f"❌ Gagal backtest: {
