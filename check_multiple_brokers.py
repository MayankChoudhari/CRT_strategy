#!/usr/bin/env python
"""
check_multiple_brokers.py - Test different broker configurations for MT5

This script attempts to connect to MetaTrader 5 using different broker credentials
to find a working configuration for the Gold trading system.
"""

import sys
import os
import time
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60)

def main():
    print_header("METATRADER 5 BROKER CONNECTION TEST")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        import MetaTrader5 as mt5
        print(f"\n✓ MetaTrader5 module is installed (version: {mt5.__version__})")
    except ImportError:
        print("\n✗ MetaTrader5 module is not installed")
        print("Please install it with: pip install MetaTrader5")
        return
    
    # Broker configurations to try
    broker_configs = [
        {
            "name": "EXNESS",
            "server": "Exness-MT5Trial7",
            "login": 205568819,
            "password": "Sx!0SpVs",
            "symbol": "XAUUSDm"
        },
        {
            "name": "STARTRADER Financial",
            "server": "STARTRADERFinancial-Live",
            "login": 1358521, 
            "password": "Sx!0SpVs",
            "symbol": "XAUUSD.c"
        },
        {
            "name": "Demo Account",
            "server": "MetaQuotes-Demo",
            "login": 5000000000,  # Demo login
            "password": "password",  # Demo password
            "symbol": "XAUUSD"
        }
    ]
    
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
        
        # Display terminal info
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print("\n--- Terminal Information ---")
            print(f"Name: {terminal_info.name}")
            print(f"Path: {terminal_info.path}")
            print(f"Connected: {'Yes' if terminal_info.connected else 'No'}")
            print(f"Auto Trading Allowed: {'Yes' if terminal_info.trade_allowed else 'No'}")
    
    # Test each broker configuration
    for i, config in enumerate(broker_configs):
        print("\n" + "-"*60)
        print(f"Testing Broker #{i+1}: {config['name']}")
        print(f"Server: {config['server']}, Login: {config['login']}")
        print("-"*60)
        
        try:
            # Try to login
            print(f"Attempting to login...")
            login_result = mt5.login(
                login=config['login'],
                password=config['password'],
                server=config['server']
            )
            
            if login_result:
                print("✓ Login successful!")
                
                # Get account info
                account_info = mt5.account_info()
                print("\n--- Account Information ---")
                print(f"Login: {account_info.login}")
                print(f"Server: {account_info.server}")
                print(f"Balance: ${account_info.balance}")
                
                # Check Gold symbol
                symbol = config['symbol']
                print(f"\nChecking symbol: {symbol}")
                symbol_info = mt5.symbol_info(symbol)
                
                if symbol_info:
                    print(f"✓ Symbol {symbol} found!")
                    print(f"Description: {symbol_info.description}")
                    print(f"Current price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
                    
                    # Check for other Gold symbols
                    print("\nLooking for other Gold symbols...")
                    gold_symbols = []
                    symbols = mt5.symbols_get()
                    for sym in symbols:
                        if "GOLD" in sym.name or "XAU" in sym.name:
                            gold_symbols.append(sym.name)
                    
                    if gold_symbols:
                        print(f"Found {len(gold_symbols)} Gold symbols: {', '.join(gold_symbols)}")
                    else:
                        print("No other Gold symbols found")
                    
                    print("\n✅ SUCCESS! Use these settings in your config.py:")
                    print(f"MT5_SERVER = \"{config['server']}\"")
                    print(f"MT5_LOGIN = {config['login']}")
                    if gold_symbols:
                        print(f"MT5_SYMBOL = \"{gold_symbols[0]}\"  # Or choose another: {', '.join(gold_symbols[1:])}")
                    else:
                        print(f"MT5_SYMBOL = \"{symbol}\"")
                        
                    # Save working configuration to a file
                    with open("working_mt5_config.txt", "w") as f:
                        f.write(f"# Working MT5 Configuration - {datetime.now()}\n")
                        f.write(f"MT5_SERVER = \"{config['server']}\"\n")
                        f.write(f"MT5_LOGIN = {config['login']}\n")
                        f.write(f"MT5_PASSWORD = \"{config['password']}\"\n")
                        if gold_symbols:
                            f.write(f"MT5_SYMBOL = \"{gold_symbols[0]}\"  # Available: {', '.join(gold_symbols)}\n")
                        else:
                            f.write(f"MT5_SYMBOL = \"{symbol}\"\n")
                    
                    print("\nConfiguration saved to working_mt5_config.txt")
                    
                else:
                    print(f"✗ Symbol {symbol} not found")
                    print("Available symbols may be different for this broker")
            else:
                print(f"✗ Login failed: {mt5.last_error()}")
                
        except Exception as e:
            print(f"Error testing broker: {e}")
        
        # Logout before trying next broker
        mt5.login(0)
        print("Logged out")
    
    # Shutdown MT5
    print("\nShutting down MT5...")
    mt5.shutdown()
    print("Test completed")

if __name__ == "__main__":
    main()
