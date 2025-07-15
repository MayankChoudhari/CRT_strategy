#!/usr/bin/env python
"""
run_gold_live.py - Simplified Gold trading system for live testing

This script provides a straightforward way to run the Gold CRT trading system
with better error handling and simplified setup.
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
import traceback
import subprocess

# Configure logging
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "gold_live_test.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ])
logger = logging.getLogger("gold_live")

def start_mt5():
    """Start MetaTrader 5 terminal if not already running"""
    logger.info("Checking if MetaTrader 5 is running...")
    
    # Common paths for terminal64.exe
    mt5_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'MetaTrader 5 EXNESS', 'terminal64.exe'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'STARTRADER Financial MetaTrader 5', 'terminal64.exe'),
    ]
    
    # Try each path
    for path in mt5_paths:
        if os.path.exists(path):
            logger.info(f"Found MT5 at: {path}")
            try:
                # Start MT5
                subprocess.Popen([path])
                logger.info(f"Started MetaTrader 5 from {path}")
                logger.info("Waiting 15 seconds for MT5 to initialize...")
                time.sleep(15)
                return True
            except Exception as e:
                logger.error(f"Failed to start MT5: {e}")
    
    logger.error("Could not find MetaTrader 5 terminal executable")
    return False

def run_gold_trading():
    """Main function to run Gold trading"""
    logger.info("="*80)
    logger.info("GOLD CRT TRADING SYSTEM - LIVE TEST")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now()}")
    
    try:
        # Import MetaTrader5
        import MetaTrader5 as mt5
        logger.info(f"MetaTrader5 version: {mt5.__version__}")
        
        # Initialize MT5
        logger.info("Initializing MetaTrader5...")
        if not mt5.initialize():
            error = mt5.last_error()
            logger.error(f"Failed to initialize MT5: {error}")
            
            if error[0] == -10005:  # IPC timeout
                logger.warning("MetaTrader 5 terminal is not running. Attempting to start it...")
                if start_mt5():
                    # Try initialization again
                    if not mt5.initialize():
                        logger.error(f"Still failed to initialize MT5: {mt5.last_error()}")
                        return False
                    else:
                        logger.info("Successfully initialized MT5 after starting the terminal")
                else:
                    return False
            else:
                return False
        
        # Get terminal information
        terminal_info = mt5.terminal_info()
        logger.info(f"Terminal name: {terminal_info.name}")
        logger.info(f"Terminal path: {terminal_info.path}")
        logger.info(f"Connected to broker: {'Yes' if terminal_info.connected else 'No'}")
        logger.info(f"Auto trading allowed: {'Yes' if terminal_info.trade_allowed else 'No'}")
        
        # Login to account
        # Testing multiple broker configurations
        broker_configs = [
            {
                "name": "EXNESS",
                "server": "Exness-MT5Trial7", 
                "login": 205568819,
                "password": "Sx!0SpVs",
                "symbol": "XAUUSDm"
            },
            {
                "name": "STARTRADER",
                "server": "STARTRADERFinancial-Live",
                "login": 1358521,
                "password": "Sx!0SpVs",
                "symbol": "XAUUSD.c"
            },
            {
                "name": "Demo",
                "server": "MetaQuotes-Demo",
                "login": 5000000000,
                "password": "password",
                "symbol": "XAUUSD"
            }
        ]
        
        # Try each broker configuration
        login_success = False
        working_config = None
        
        for config in broker_configs:
            logger.info(f"Trying to login to {config['name']} ({config['server']})...")
            
            login_result = mt5.login(
                login=config['login'],
                password=config['password'],
                server=config['server']
            )
            
            if login_result:
                logger.info(f"Successfully logged in to {config['name']}!")
                login_success = True
                working_config = config
                break
            else:
                logger.warning(f"Failed to login to {config['name']}: {mt5.last_error()}")
        
        if not login_success:
            logger.error("Failed to login to any broker. Cannot continue.")
            mt5.shutdown()
            return False
        
        # Get account information
        account_info = mt5.account_info()
        logger.info(f"Account: {account_info.login}")
        logger.info(f"Server: {account_info.server}")
        logger.info(f"Balance: ${account_info.balance}")
        logger.info(f"Equity: ${account_info.equity}")
        
        # Check Gold symbol
        symbol = working_config['symbol']
        logger.info(f"Testing symbol: {symbol}")
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found")
            
            # Try to find any Gold symbols
            logger.info("Searching for available Gold symbols...")
            gold_symbols = []
            symbols = mt5.symbols_get()
            for s in symbols:
                if "GOLD" in s.name or "XAU" in s.name:
                    gold_symbols.append(s.name)
            
            if gold_symbols:
                logger.info(f"Found {len(gold_symbols)} Gold symbols: {', '.join(gold_symbols)}")
                symbol = gold_symbols[0]
                logger.info(f"Using {symbol} instead")
                
                symbol_info = mt5.symbol_info(symbol)
            else:
                logger.error("No Gold symbols found. Cannot continue.")
                mt5.shutdown()
                return False
        
        # Display Gold price
        logger.info(f"Current {symbol} price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
        logger.info(f"Spread: {symbol_info.spread} points")
        
        # Save working configuration for future use
        with open("working_mt5_config.txt", "w") as f:
            f.write(f"# Working MetaTrader 5 Configuration - {datetime.now()}\n")
            f.write(f"MT5_SERVER = \"{working_config['server']}\"\n")
            f.write(f"MT5_LOGIN = {working_config['login']}\n")
            f.write(f"MT5_PASSWORD = \"{working_config['password']}\"\n")
            f.write(f"MT5_SYMBOL = \"{symbol}\"\n")
        
        logger.info("Working configuration saved to working_mt5_config.txt")
        logger.info("Use these settings in your src/config.py file")
        
        # Collect recent price data for analysis
        logger.info(f"Collecting recent {symbol} price data for analysis...")
        
        # Get 1-hour data (100 bars)
        logger.info("Fetching 1-hour data...")
        data_1h = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
        if data_1h is not None:
            logger.info(f"Downloaded {len(data_1h)} 1-hour bars")
            
            # Calculate daily range
            daily_ranges = []
            for i in range(0, min(10, len(data_1h)), 24):
                if i+24 <= len(data_1h):
                    day_high = max([bar[2] for bar in data_1h[i:i+24]])
                    day_low = min([bar[3] for bar in data_1h[i:i+24]])
                    daily_range = day_high - day_low
                    daily_ranges.append(daily_range)
            
            if daily_ranges:
                avg_range = sum(daily_ranges) / len(daily_ranges)
                logger.info(f"Average daily range: ${avg_range:.2f}")
        else:
            logger.error(f"Failed to get 1-hour data for {symbol}")
        
        # Get 5-minute data (100 bars)
        logger.info("Fetching 5-minute data...")
        data_5m = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
        if data_5m is not None:
            logger.info(f"Downloaded {len(data_5m)} 5-minute bars")
            
            # Show latest price action
            latest = data_5m[-1]
            logger.info(f"Latest bar: Time={datetime.fromtimestamp(latest[0])}")
            logger.info(f"OHLC: ${latest[1]:.2f}, ${latest[2]:.2f}, ${latest[3]:.2f}, ${latest[4]:.2f}")
        else:
            logger.error(f"Failed to get 5-minute data for {symbol}")
        
        # Monitor for CRT trading opportunities
        logger.info("\nStarting CRT trading monitor...")
        logger.info("Press Ctrl+C to stop monitoring")
        
        # Simple monitoring loop
        update_interval = 5  # minutes
        last_update = None
        current_crt_high = None
        current_crt_low = None
        current_hour = None
        
        try:
            while True:
                current_time = datetime.now()
                
                # Check if we need to update data
                if last_update is None or (current_time - last_update).total_seconds() >= update_interval * 60:
                    logger.info(f"Updating data at {current_time}")
                    
                    # Get latest 5-minute candle
                    latest_5m = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1)
                    if latest_5m is not None:
                        candle = latest_5m[0]
                        candle_time = datetime.fromtimestamp(candle[0])
                        logger.info(f"Latest candle: {candle_time}")
                        logger.info(f"OHLC: ${candle[1]:.2f}, ${candle[2]:.2f}, ${candle[3]:.2f}, ${candle[4]:.2f}")
                        
                        # Check if we're in a new hour to update CRT range
                        candle_hour = candle_time.hour
                        if current_hour != candle_hour:
                            # Get latest 1-hour candle
                            latest_1h = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 1)
                            if latest_1h is not None:
                                hour_candle = latest_1h[0]
                                current_hour = candle_hour
                                current_crt_high = hour_candle[2]  # High
                                current_crt_low = hour_candle[3]   # Low
                                
                                logger.info(f"New CRT Range: High=${current_crt_high:.2f}, Low=${current_crt_low:.2f}")
                                logger.info(f"CRT Range size: ${current_crt_high - current_crt_low:.2f}")
                        
                        # Check for CRT signals
                        if current_crt_high is not None and current_crt_low is not None:
                            # Check for liquidity grab and close back inside
                            high_sweep = candle[2] > current_crt_high and candle[4] < current_crt_high
                            low_sweep = candle[3] < current_crt_low and candle[4] > current_crt_low
                            
                            if high_sweep:
                                logger.info("🔴 SHORT SIGNAL DETECTED!")
                                logger.info(f"Price swept above CRT high (${current_crt_high:.2f}) to ${candle[2]:.2f} then closed back inside at ${candle[4]:.2f}")
                                
                                # Calculate potential profit targets
                                tp1 = (current_crt_high + current_crt_low) / 2  # Mid of range
                                tp2 = current_crt_low
                                risk = candle[2] - candle[4]
                                rr1 = (candle[4] - tp1) / risk
                                rr2 = (candle[4] - tp2) / risk
                                
                                logger.info(f"Entry: ${candle[4]:.2f}, Stop Loss: ${candle[2]:.2f}")
                                logger.info(f"TP1: ${tp1:.2f} (mid-range), TP2: ${tp2:.2f} (range low)")
                                logger.info(f"Risk: ${risk:.2f}, R:R to TP1: {abs(rr1):.2f}, R:R to TP2: {abs(rr2):.2f}")
                                
                            elif low_sweep:
                                logger.info("🟢 LONG SIGNAL DETECTED!")
                                logger.info(f"Price swept below CRT low (${current_crt_low:.2f}) to ${candle[3]:.2f} then closed back inside at ${candle[4]:.2f}")
                                
                                # Calculate potential profit targets
                                tp1 = (current_crt_high + current_crt_low) / 2  # Mid of range
                                tp2 = current_crt_high
                                risk = candle[4] - candle[3]
                                rr1 = (tp1 - candle[4]) / risk
                                rr2 = (tp2 - candle[4]) / risk
                                
                                logger.info(f"Entry: ${candle[4]:.2f}, Stop Loss: ${candle[3]:.2f}")
                                logger.info(f"TP1: ${tp1:.2f} (mid-range), TP2: ${tp2:.2f} (range high)")
                                logger.info(f"Risk: ${risk:.2f}, R:R to TP1: {abs(rr1):.2f}, R:R to TP2: {abs(rr2):.2f}")
                    else:
                        logger.error("Failed to get latest 5-minute data")
                    
                    last_update = current_time
                
                # Sleep before next check
                time.sleep(30)
        
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        
        # Clean up
        mt5.shutdown()
        logger.info("MetaTrader 5 connection closed")
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

if __name__ == "__main__":
    run_gold_trading()
