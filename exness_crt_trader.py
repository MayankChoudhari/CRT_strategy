import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta, timezone
import pandas as pd
import os
import openpyxl

# --- CONFIG ---
SYMBOL = 'XAUUSDm'
RISK_PER_TRADE = 0.01
LOT_SIZE = 0.01
# Set session hours to match Exness Market Watch time (UTC+0)
SESSION_HOURS = [1, 5, 9, 13, 15, 18, 21]  # These are in Exness Market Watch time (UTC+0)
USE_ORDER_BLOCK = True
USE_POWER_OF_THREE = True
ENTRY_TIMEFRAME = mt5.TIMEFRAME_M5
RANGE_TIMEFRAME = mt5.TIMEFRAME_H1
TP_MODE = 'both'  # 'mid', 'full', or 'both'
SL_BUFFER = 1.0  # Buffer in price units (e.g. $1 for gold)

# --- EXNESS TERMINAL PATH (set this to your Exness terminal64.exe) ---
EXNESS_MT5_PATH = r"C:\\Program Files\\MetaTrader 5 EXNESS\\terminal64.exe"  # Update if needed

# --- MT5 Attach Only to Exness ---
print(f"Connecting to Exness MT5 terminal at {EXNESS_MT5_PATH} (attach only)...")
if not mt5.initialize(EXNESS_MT5_PATH, portable=True):
    print(f"MT5 initialize() failed: {mt5.last_error()}")
    quit()
account = mt5.account_info()
if account is None:
    print("Failed to get account info. Please ensure you are logged in manually.")
    mt5.shutdown()
    quit()
print(f"Connected: {account.name} | Balance: {account.balance}")

# --- Helper: Get last N candles as DataFrame ---
def get_rates(symbol, timeframe, count, shift=0):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, shift, count)
    if rates is None or len(rates) < count:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

# --- Helper: Find order block (last opposite candle before move) ---
def find_order_block(df, direction):
    # For BUY: last bearish candle before up move; for SELL: last bullish before down move
    if direction == 'BUY':
        obs = df[(df['close'] < df['open'])]
    else:
        obs = df[(df['close'] > df['open'])]
    if obs.empty:
        return None
    return obs.iloc[-1]

# --- Helper: Get Market Watch (broker) time ---
def get_broker_time():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(tick.time, timezone.utc)

# --- Trade Limiting and R:R Filter ---
trades_today = 0
last_trade_day = None

# --- Excel Journal Setup ---
JOURNAL_FILE = "trade_journal.xlsx"
JOURNAL_HEADERS = [
    "Ticket", "DateTime", "Symbol", "Direction", "EntryPrice", "SL", "TP", "LotSize", "RR1", "RR2", "Status", "ExitPrice", "Profit", "Comment"
]
if not os.path.exists(JOURNAL_FILE):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(JOURNAL_HEADERS)
    wb.save(JOURNAL_FILE)

# --- Helper: Log trade to Excel journal ---
def log_trade(ticket, dt, symbol, direction, entry, sl, tp, lot, rr1, rr2, status, exit_price, profit, comment):
    wb = openpyxl.load_workbook(JOURNAL_FILE)
    ws = wb.active
    ws.append([
        ticket, dt, symbol, direction, entry, sl, tp, lot, rr1, rr2, status, exit_price, profit, comment
    ])
    wb.save(JOURNAL_FILE)

# --- Main CRT Strategy Loop ---
print("Starting advanced CRT strategy on live Exness demo...")
last_trade_time = None

while True:
    broker_now = get_broker_time()
    broker_day = broker_now.date()
    if last_trade_day != broker_day:
        trades_today = 0
        last_trade_day = broker_day
    if trades_today >= 3:
        print(f"{broker_now} Max 3 trades reached for {broker_day}. Waiting for next day...")
        time.sleep(60)
        continue
    if broker_now.hour not in SESSION_HOURS:
        print(f"{broker_now} Not in CRT session hours (Market Watch time). Waiting...")
        time.sleep(60)
        continue
    # Get last 3 H1 candles for power of three
    h1_df = get_rates(SYMBOL, RANGE_TIMEFRAME, 3, 1)
    if h1_df is None:
        print("No H1 data. Waiting...")
        time.sleep(10)
        continue
    # Power of three: require 3-candle sequence
    if USE_POWER_OF_THREE:
        range_candle = h1_df.iloc[0]
        sweep_candle = h1_df.iloc[1]
        confirm_candle = h1_df.iloc[2]
        crt_high = range_candle['high']
        crt_low = range_candle['low']
        # Sweep must wick through range, confirm must close back inside
        sweeped_high = sweep_candle['high'] > crt_high
        sweeped_low = sweep_candle['low'] < crt_low
        confirm_in_range = (crt_low < confirm_candle['close'] < crt_high)
        if not ((sweeped_high or sweeped_low) and confirm_in_range):
            print(f"{broker_now} No CRT power-of-three pattern.")
            time.sleep(60)
            continue
        direction = 'SELL' if sweeped_high else 'BUY'
    else:
        # Simple: use last closed H1 for range
        range_candle = h1_df.iloc[-1]
        crt_high = range_candle['high']
        crt_low = range_candle['low']
        direction = None
    # Get last 10 M5 candles for entry
    m5_df = get_rates(SYMBOL, ENTRY_TIMEFRAME, 10, 1)
    if m5_df is None:
        print("No M5 data. Waiting...")
        time.sleep(10)
        continue
    # Find entry: after confirm, wait for price to return to order block
    entry_candle = None
    if USE_ORDER_BLOCK:
        ob = find_order_block(m5_df, direction)
        if ob is not None:
            # Wait for price to return to OB
            if direction == 'BUY' and m5_df.iloc[-1]['low'] <= ob['low']:
                entry_candle = m5_df.iloc[-1]
            elif direction == 'SELL' and m5_df.iloc[-1]['high'] >= ob['high']:
                entry_candle = m5_df.iloc[-1]
    else:
        # Enter on first M5 close back inside range after sweep
        for i in range(1, len(m5_df)):
            c = m5_df.iloc[i]
            if direction == 'SELL' and c['high'] > crt_high and c['close'] < crt_high:
                entry_candle = c
                break
            elif direction == 'BUY' and c['low'] < crt_low and c['close'] > crt_low:
                entry_candle = c
                break
    if entry_candle is None:
        print(f"{broker_now} No CRT entry signal.")
        time.sleep(60)
        continue
    # Prevent duplicate trades in same hour
    if last_trade_time and entry_candle.name <= last_trade_time:
        time.sleep(60)
        continue
    last_trade_time = entry_candle.name
    # Calculate SL/TP and R:R
    if direction == 'SELL':
        sl = entry_candle['high'] + (entry_candle['high'] - entry_candle['close']) * 0.1  # Just above the wick
        tp1 = (crt_high + crt_low) / 2
        tp2 = crt_low
        price = mt5.symbol_info_tick(SYMBOL).bid
        risk = abs(price - sl)
        rr1 = abs(price - tp1) / risk if risk > 0 else 0
        rr2 = abs(price - tp2) / risk if risk > 0 else 0
    else:
        sl = entry_candle['low'] - (entry_candle['close'] - entry_candle['low']) * 0.1  # Just below the wick
        tp1 = (crt_high + crt_low) / 2
        tp2 = crt_high
        price = mt5.symbol_info_tick(SYMBOL).ask
        risk = abs(price - sl)
        rr1 = abs(price - tp1) / risk if risk > 0 else 0
        rr2 = abs(price - tp2) / risk if risk > 0 else 0
    # Only trade if R:R to at least one TP is 2.0+
    if max(rr1, rr2) < 2.0:
        print(f"{broker_now} R:R too low (TP1: {rr1:.2f}, TP2: {rr2:.2f}). Skipping trade.")
        time.sleep(60)
        continue
    # Place order
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_SELL if direction == 'SELL' else mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp2 if TP_MODE == 'full' else tp1,
        "deviation": 20,
        "magic": 123456,
        "comment": "CRT advanced",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"{entry_candle.name} {direction} order placed at {price} | SL: {sl} | TP: {request['tp']} | RR1: {rr1:.2f} | RR2: {rr2:.2f}")
        trades_today += 1
        # Log entry to Excel
        log_trade(
            result.order, str(broker_now), SYMBOL, direction, price, sl, request['tp'], LOT_SIZE, rr1, rr2, "OPEN", "", "", request['comment']
        )
    else:
        print(f"Order failed: {result.retcode} {result.comment}")
    time.sleep(60)

mt5.shutdown()
