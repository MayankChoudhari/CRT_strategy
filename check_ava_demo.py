#!/usr/bin/env python
"""
check_ava_demo.py - Test connection to Ava-Demo account from README
"""

from datetime import datetime
import time

def main():
    print("=" * 60)
    print("AVA-DEMO MT5 ACCOUNT CHECKER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Import config
    try:
        from src import config
        print(f"\nUsing configuration from src/config.py:")
        print(f"Server: {config.MT5_SERVER}")
        print(f"Login: {config.MT5_LOGIN}")
        print(f"Symbol: {config.MT5_SYMBOL}")
    except ImportError:
        print("Could not import config. Make sure you're in the correct directory.")
        return
    
    # Import MT5
    try:
        print("\nImporting MetaTrader5...")
        import MetaTrader5 as mt5
        print(f"MetaTrader5 version: {mt5.__version__}")
    except ImportError:
        print("Could not import MetaTrader5. Install it with: pip install MetaTrader5")
        return
    
    # Initialize MT5
    print("\nInitializing MT5...")
    if not mt5.initialize():
        error = mt5.last_error()
        print(f"Failed to initialize MT5: {error}")
        return
    
    print("MT5 initialized successfully!")
    
    # Try to login
    print(f"\nAttempting to login to {config.MT5_SERVER} with account {config.MT5_LOGIN}...")
    login_result = mt5.login(
        login=config.MT5_LOGIN,
        password=config.MT5_PASSWORD,
        server=config.MT5_SERVER
    )
    
    if not login_result:
        error = mt5.last_error()
        print(f"Login failed: {error}")
        mt5.shutdown()
        return
    
    print("Login successful!")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info is not None:
        print(f"\nAccount Information:")
        print(f"  Login: {account_info.login}")
        print(f"  Server: {account_info.server}")
        print(f"  Name: {account_info.name}")
        print(f"  Balance: ${account_info.balance:.2f}")
    
    # Check for symbol
    print(f"\nChecking for symbol {config.MT5_SYMBOL}...")
    symbol_info = mt5.symbol_info(config.MT5_SYMBOL)
    
    if symbol_info is None:
        print(f"Symbol {config.MT5_SYMBOL} not found")
        
        # Try to find gold symbols
        print("\nSearching for available Gold symbols...")
        gold_symbols = []
        all_symbols = mt5.symbols_get()
        for symbol in all_symbols:
            if "XAU" in symbol.name or "GOLD" in symbol.name:
                gold_symbols.append(symbol.name)
        
        if gold_symbols:
            print(f"Available Gold symbols: {', '.join(gold_symbols)}")
            print(f"Please update config.MT5_SYMBOL with one of these values")
    else:
        print(f"Symbol {config.MT5_SYMBOL} is available!")
        print(f"Current price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
        
        # Get some recent candles
        print(f"\nFetching recent candles for {config.MT5_SYMBOL}...")
        candles = mt5.copy_rates_from_pos(config.MT5_SYMBOL, mt5.TIMEFRAME_H1, 0, 5)
        if candles is not None and len(candles) > 0:
            import pandas as pd
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            print("\nRecent hourly candles:")
            print(df[['time', 'open', 'high', 'low', 'close']].to_string(index=False))
    
    # Clean up
    mt5.shutdown()
    print("\nMT5 connection test completed!")

if __name__ == "__main__":
    main()
