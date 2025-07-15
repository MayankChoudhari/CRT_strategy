#!/usr/bin/env python
"""
manual_mt5_test.py - Interactive MetaTrader 5 connection test

This script provides a more interactive way to test MetaTrader 5 connection
with manual entry of credentials to troubleshoot login issues.
"""

import sys
import os
import time
import getpass
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60)

def main():
    print_header("METATRADER 5 MANUAL CONNECTION TEST")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if MetaTrader5 module is installed
    try:
        import MetaTrader5 as mt5
        print(f"\n✓ MetaTrader5 module is installed (version: {mt5.__version__})")
    except ImportError:
        print("\n✗ MetaTrader5 module is not installed")
        print("Please install it with: pip install MetaTrader5")
        return
    
    # Try to initialize MT5
    print("\nInitializing MetaTrader 5...")
    if not mt5.initialize():
        error = mt5.last_error()
        print(f"✗ Failed to initialize MT5. Error code: {error}")
        
        if error[0] == -10005:  # IPC timeout
            print("\nError indicates MetaTrader 5 terminal is not running.")
            print("Please start the MetaTrader 5 terminal first, then run this script again.")
            return
    else:
        print("✓ MT5 initialized successfully")
    
    # Display available terminals
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print("\n--- Terminal Information ---")
        print(f"Name: {terminal_info.name}")
        print(f"Path: {terminal_info.path}")
        print(f"Connected: {'Yes' if terminal_info.connected else 'No'}")
        print(f"Community Account: {terminal_info.community_account}")
        print(f"Connected to MQL5: {'Yes' if terminal_info.connected_mql5 else 'No'}")
        print(f"Auto Trading Allowed: {'Yes' if terminal_info.trade_allowed else 'No'}")
    
    # Get current account info
    account_info = mt5.account_info()
    if account_info:
        print("\n--- Current Account ---")
        print(f"Login: {account_info.login}")
        print(f"Server: {account_info.server}")
        print(f"Balance: ${account_info.balance}")
        print(f"Equity: ${account_info.equity}")
        
        # Show this account's available Gold symbols
        print("\nChecking available Gold symbols for this account...")
        gold_symbols = []
        symbols = mt5.symbols_get()
        for symbol in symbols:
            if "GOLD" in symbol.name or "XAU" in symbol.name:
                gold_symbols.append(symbol.name)
        
        if gold_symbols:
            print(f"\nFound {len(gold_symbols)} Gold symbols: {', '.join(gold_symbols)}")
        else:
            print("\nNo Gold symbols found for this account")
    else:
        print("\n✗ Not logged in to any account")
    
    # Test alternative login
    print("\n--- Manual Login Test ---")
    print("Let's try logging in with manually entered credentials:")
    
    try:
        server = input("Enter MT5 server name (e.g., 'Exness-MT5Trial7'): ")
        login = int(input("Enter MT5 account number: "))
        password = getpass.getpass("Enter password (input will be hidden): ")
        
        print(f"\nTrying to login with: Server={server}, Login={login}...")
        login_result = mt5.login(login=login, password=password, server=server)
        
        if login_result:
            print("✓ Login successful!")
            
            # Show account info after login
            account_info = mt5.account_info()
            print("\n--- Account Information ---")
            print(f"Login: {account_info.login}")
            print(f"Server: {account_info.server}")
            print(f"Balance: ${account_info.balance}")
            
            # Check Gold symbols
            print("\nChecking available Gold symbols...")
            gold_symbols = []
            symbols = mt5.symbols_get()
            for symbol in symbols:
                if "GOLD" in symbol.name or "XAU" in symbol.name:
                    gold_symbols.append(symbol.name)
            
            if gold_symbols:
                print(f"\nFound {len(gold_symbols)} Gold symbols: {', '.join(gold_symbols)}")
                
                # Get price for first Gold symbol
                gold_sym = gold_symbols[0]
                symbol_info = mt5.symbol_info(gold_sym)
                print(f"\nCurrent {gold_sym} price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
                print(f"Spread: {symbol_info.spread} points")
                
                print("\nRecommended config.py settings:")
                print(f"MT5_SERVER = \"{server}\"")
                print(f"MT5_LOGIN = {login}")
                print(f"MT5_SYMBOL = \"{gold_sym}\"")
            else:
                print("\nNo Gold symbols found for this account")
        else:
            print(f"✗ Login failed: {mt5.last_error()}")
    except ValueError:
        print("Invalid input. Account number must be an integer.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error during login test: {e}")
    
    # Shutdown MT5
    print("\nShutting down MT5...")
    mt5.shutdown()
    print("Test completed")

if __name__ == "__main__":
    main()
