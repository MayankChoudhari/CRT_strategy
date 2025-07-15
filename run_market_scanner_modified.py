#!/usr/bin/env python
"""
run_market_scanner_modified.py - Enhanced Gold market scanner with improved MT5 connection

This script provides an enhanced interface to scan current Gold market conditions
with better MT5 connection handling based on the fix_mt5_connection approach.
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
import time
import subprocess
import platform

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from src import config
from market_scanner import scan_market

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("market_scanner")

def find_mt5_terminal():
    """Find MetaTrader 5 terminal installation paths"""
    logger.info("Looking for MetaTrader 5 terminal...")
    
    common_paths = [
        # Standard installation paths
        "C:\\Program Files\\MetaTrader 5",
        "C:\\Program Files (x86)\\MetaTrader 5",
        # Custom broker paths
        "C:\\Program Files\\MetaTrader 5 EXNESS",
        "C:\\Program Files (x86)\\MetaTrader 5 EXNESS",
        # More paths from fix script
        os.path.expanduser("~/AppData/Roaming/MetaQuotes/Terminal"),
        os.path.expandvars("%LOCALAPPDATA%\\Programs\\MetaTrader 5"),
    ]
    
    found_paths = []
    for path in common_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    return found_paths

def check_mt5_connection():
    """Check if MetaTrader 5 is connected and Gold symbol is available"""
    try:
        # Import MetaTrader5
        import MetaTrader5 as mt5
        
        logger.info("Initializing connection to MetaTrader 5 terminal...")
        
        # Try to initialize
        if not mt5.initialize():
            error_code = mt5.last_error()
            logger.error(f"Failed to initialize MT5 (Error code: {error_code})")
            
            if error_code[0] == 10013 or error_code[0] == -10005:  # Terminal not running
                logger.warning("MetaTrader 5 terminal is not running")
                  # Try to start terminal automatically
                terminal_paths = find_mt5_terminal()
                if terminal_paths:
                    try:
                        # Try terminal64.exe first, then terminal.exe
                        terminal64_path = os.path.join(terminal_paths[0], 'terminal64.exe')
                        terminal_path = os.path.join(terminal_paths[0], 'terminal.exe')
                        
                        if os.path.exists(terminal64_path):
                            logger.info(f"Attempting to start MetaTrader 5 from: {terminal64_path}")
                            subprocess.Popen([terminal64_path])
                        elif os.path.exists(terminal_path):
                            logger.info(f"Attempting to start MetaTrader 5 from: {terminal_path}")
                            subprocess.Popen([terminal_path])
                        else:
                            logger.warning(f"No terminal.exe or terminal64.exe found in {terminal_paths[0]}")
                            
                        logger.info("Waiting 10 seconds for MT5 to start...")
                        time.sleep(10)
                        
                        # Try initialization again
                        if mt5.initialize():
                            logger.info("Successfully initialized MT5 after starting the terminal")
                        else:
                            logger.error(f"Still failed to initialize MT5: {mt5.last_error()}")
                            return False
                    except Exception as e:
                        logger.error(f"Failed to start MT5 terminal: {e}")
                        return False
                else:
                    logger.error("Could not find MetaTrader 5 installation")
                    return False
            else:
                logger.error(f"Unknown MT5 error: {error_code}")
                return False
        else:
            logger.info("Successfully initialized MT5")
        
        # Try to login if not already logged in
        account_info = mt5.account_info()
        if account_info is None:
            logger.info(f"Logging in to MT5 account {config.MT5_LOGIN} on {config.MT5_SERVER}")
            
            login_result = mt5.login(
                login=config.MT5_LOGIN,
                password=config.MT5_PASSWORD,
                server=config.MT5_SERVER
            )
            
            if not login_result:
                logger.error(f"Failed to login to MT5: {mt5.last_error()}")
                mt5.shutdown()
                return False
            else:
                logger.info("Login successful")
        else:
            logger.info(f"Already logged in as {account_info.login} on {account_info.server}")
            
        # Check for symbol availability
        symbol_info = mt5.symbol_info(config.MT5_SYMBOL)
        if symbol_info is None:
            logger.error(f"Symbol {config.MT5_SYMBOL} not found")
            
            # Try to find gold symbols
            gold_symbols = []
            symbols = mt5.symbols_get()
            for symbol in symbols:
                if "GOLD" in symbol.name or "XAU" in symbol.name:
                    gold_symbols.append(symbol.name)
            
            if gold_symbols:
                logger.info(f"Available Gold symbols: {', '.join(gold_symbols)}")
                logger.info(f"Please update config.MT5_SYMBOL with one of these values")
                mt5.shutdown()
                return False
        
        # Get current price for Gold
        tick = mt5.symbol_info_tick(config.MT5_SYMBOL)
        if tick is None:
            logger.error(f"Could not get current price for {config.MT5_SYMBOL}")
            mt5.shutdown()
            return False
            
        logger.info(f"Connected to MT5. Current Gold ({config.MT5_SYMBOL}) price: ${tick.bid:.2f}/{tick.ask:.2f}")
        
        # All checks passed, MT5 is fully connected
        mt5.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"Error checking MT5 connection: {e}")
        return False

def run_market_scan(symbol=None, lookback_days=5, save_chart=True):
    """Run market scan for the specified symbol"""
    if symbol is None:
        symbol = config.MT5_SYMBOL
    
    print(f"\n{'='*80}")
    print(f"GOLD MARKET SCANNER - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    
    # Run the scan
    analysis = scan_market(symbol, lookback_days)
    
    # If scan was successful and save_chart is True
    if analysis and save_chart:
        chart_path = os.path.join(config.RESULTS_DIR, f"{symbol}_market_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.png")
        print(f"\nMarket scan chart saved to: {chart_path}")
    
    return analysis

def interactive_mode():
    """Run the market scanner in interactive mode"""
    print("\n" + "="*80)
    print("INTERACTIVE GOLD MARKET SCANNER")
    print("="*80)
    
    # Check MT5 connection first
    if not check_mt5_connection():
        print("\nCannot continue without MT5 connection. Please fix connection issues and try again.")
        print("Tip: Run fix_mt5_connection.py to diagnose and fix MetaTrader 5 connection issues.")
        return
    
    # Default values
    lookback_days = 5
    save_chart = True
    
    # Get user input
    try:
        lookback = input(f"\nEnter lookback period in days [default: {lookback_days}]: ")
        if lookback.strip():
            lookback_days = int(lookback)
        
        save = input(f"Save chart to file? (y/n) [default: y]: ").lower()
        if save == 'n':
            save_chart = False
    except ValueError:
        print("Invalid input. Using default values.")
    
    # Run the scan
    analysis = run_market_scan(config.MT5_SYMBOL, lookback_days, save_chart)
    
    if analysis:
        print("\n" + "="*80)
        print("MARKET ANALYSIS RESULTS")
        print("="*80)
        
        print(f"\nSymbol: {config.MT5_SYMBOL} (Gold)")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Lookback Period: {lookback_days} days")
        
        print("\n--- Daily Ranges ---")
        print(f"Average Daily Range: ${analysis['avg_daily_range']:.2f}")
        print(f"Current Day Range: ${analysis.get('current_day_range', 'N/A')}")
        print(f"Hourly Volatility: ${analysis.get('hourly_volatility', 'N/A')}")
        
        print("\n--- Key Price Levels ---")
        print(f"Today's High: ${analysis.get('today_high', 'N/A')}")
        print(f"Today's Low: ${analysis.get('today_low', 'N/A')}")
        print(f"Yesterday's High: ${analysis.get('yesterday_high', 'N/A')}")
        print(f"Yesterday's Low: ${analysis.get('yesterday_low', 'N/A')}")
        
        if 'crt_range_high' in analysis and 'crt_range_low' in analysis:
            print(f"\n--- CRT Analysis ---")
            print(f"CRT Range High: ${analysis['crt_range_high']}")
            print(f"CRT Range Low: ${analysis['crt_range_low']}")
            print(f"CRT Range Size: ${analysis['crt_range_size']}")
        
        if 'signals' in analysis:
            print(f"\n--- Trading Signals ---")
            for signal in analysis['signals']:
                print(f"- {signal}")
    else:
        print("\nMarket analysis failed. Check logs for details.")

def main():
    parser = argparse.ArgumentParser(description="Gold Market Scanner for CRT Trading System")
    parser.add_argument("-d", "--days", type=int, default=5, help="Lookback period in days")
    parser.add_argument("--no-save", action="store_true", help="Don't save chart to file")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        # Check MT5 connection first
        if not check_mt5_connection():
            print("\nCannot continue without MT5 connection. Please fix connection issues and try again.")
            print("Tip: Run fix_mt5_connection.py to diagnose and fix MetaTrader 5 connection issues.")
            return
            
        run_market_scan(config.MT5_SYMBOL, args.days, not args.no_save)

if __name__ == "__main__":
    main()
