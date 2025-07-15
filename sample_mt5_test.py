#!/usr/bin/env python
"""
sample_mt5_test.py - Basic MetaTrader 5 connection test based on official sample

This is a minimal test based on the official MetaTrader 5 Python sample.
"""

import time
from datetime import datetime
import MetaTrader5 as mt5

# Display data on MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)
 
# Establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Attempt connection to account 
authorized = mt5.login(1358521, password="Sx!0SpVs", server="STARTRADERFinancial-Live")
if authorized:
    print("Connected to account #{}".format(1358521))
else:
    print("Failed to connect at account #{}, error code: {}".format(1358521, mt5.last_error()))
 
# Display account data
account_info = mt5.account_info()
if account_info!=None:
    print("Account info:")
    print(" Login:", account_info.login)
    print(" Server:", account_info.server) 
    print(" Balance:", account_info.balance)
    print(" Equity:", account_info.equity)
    print(" Margin:", account_info.margin)
    print(" Free margin:", account_info.margin_free)

# Get Gold price
gold_symbols = ["XAUUSD", "XAUUSD.c", "GOLD", "XAUUSDm"]
found_symbol = None

for symbol in gold_symbols:
    info = mt5.symbol_info(symbol)
    if info is not None:
        found_symbol = symbol
        print(f"\nFound working Gold symbol: {symbol}")
        print(f"Bid: ${info.bid}, Ask: ${info.ask}")
        print(f"Spread: {info.spread} points")
        break

if not found_symbol:
    print("No Gold symbol found")

# Shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
