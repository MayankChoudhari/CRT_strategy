#!/usr/bin/env python
"""
mt5_direct_test.py - Direct MetaTrader 5 test with hardcoded settings

This script performs a direct test of MetaTrader 5 connectivity with hardcoded
settings to identify the correct configuration for Gold trading.
"""

import os
import time
from datetime import datetime

# Hardcoded configuration - will try different combinations
MT5_SERVER = "STARTRADERFinancial-Live"
MT5_LOGIN = 1358521
MT5_PASSWORD = "Sx!0SpVs"
MT5_SYMBOL = "XAUUSD.c"

def print_divider(char="-", length=50):
    print(char * length)

def main():
    print_divider("=")
    print("DIRECT METATRADER 5 CONNECTION TEST")
    print(f"Date: {datetime.now()}")
    print_divider("=")
    
    print("\nUsing configuration:")
    print(f"Server: {MT5_SERVER}")
    print(f"Login: {MT5_LOGIN}")
    print(f"Symbol: {MT5_SYMBOL}")
    print_divider()
    
    try:
        print("\nImporting MetaTrader5 module...")
        import MetaTrader5 as mt5
        print(f"MetaTrader5 version: {mt5.__version__}")
    except ImportError as e:
        print(f"ERROR: Could not import MetaTrader5 module: {e}")
        return
    
    print("\nInitializing MetaTrader5...")
    init_result = mt5.initialize()
    print(f"Initialization result: {init_result}")
    
    if not init_result:
        error = mt5.last_error()
        print(f"ERROR: {error}")
        
        if error[0] == -10005:
            print("MetaTrader 5 terminal is not running.")
            print("Please start the MetaTrader 5 terminal and try again.")
    else:
        print("MT5 initialized successfully!")
        
        # Check terminal information
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print("\nTerminal Information:")
            print(f"  Name: {terminal_info.name}")
            print(f"  Path: {terminal_info.path}")
            print(f"  Connected to broker: {'Yes' if terminal_info.connected else 'No'}")
            print(f"  Auto trading allowed: {'Yes' if terminal_info.trade_allowed else 'No'}")
        
        # Try to login
        print(f"\nLogging in to account {MT5_LOGIN} on {MT5_SERVER}...")
        login_result = mt5.login(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
        
        if not login_result:
            error = mt5.last_error()
            print(f"Login failed: {error}")
        else:
            print("Login successful!")
            
            # Get account info
            account_info = mt5.account_info()
            print("\nAccount Information:")
            print(f"  Login: {account_info.login}")
            print(f"  Server: {account_info.server}")
            print(f"  Balance: ${account_info.balance}")
            print(f"  Equity: ${account_info.equity}")
            
            # Check symbol
            print(f"\nChecking symbol {MT5_SYMBOL}...")
            symbol_info = mt5.symbol_info(MT5_SYMBOL)
            
            if symbol_info:
                print(f"Symbol {MT5_SYMBOL} found:")
                print(f"  Description: {symbol_info.description}")
                print(f"  Contract size: {symbol_info.trade_contract_size}")
                print(f"  Current price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
                print(f"  Spread: {symbol_info.spread} points")
                
                # Get available Gold symbols
                print("\nSearching for all Gold symbols...")
                gold_symbols = []
                symbols = mt5.symbols_get()
                for symbol in symbols:
                    if "GOLD" in symbol.name or "XAU" in symbol.name:
                        gold_symbols.append(symbol.name)
                
                if gold_symbols:
                    print(f"Found {len(gold_symbols)} Gold symbols:")
                    for i, sym in enumerate(gold_symbols, 1):
                        print(f"  {i}. {sym}")
            else:
                print(f"Symbol {MT5_SYMBOL} not found")
                
                # Look for Gold symbols
                print("\nSearching for available Gold symbols...")
                gold_symbols = []
                symbols = mt5.symbols_get()
                for symbol in symbols:
                    if "GOLD" in symbol.name or "XAU" in symbol.name:
                        gold_symbols.append(symbol.name)
                
                if gold_symbols:
                    print(f"Found {len(gold_symbols)} Gold symbols:")
                    for i, sym in enumerate(gold_symbols, 1):
                        print(f"  {i}. {sym}")
                else:
                    print("No Gold symbols found on this account")
    
    # Cleanup
    print("\nShutting down MT5...")
    mt5.shutdown()
    print("Test complete")

if __name__ == "__main__":
    main()
