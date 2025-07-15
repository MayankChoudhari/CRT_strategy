#!/usr/bin/env python
"""
run_live_trading.py - Script to run the Gold CRT trading system in live mode

This script automatically starts the MetaTrader 5 terminal if needed and then
runs the live trading system with the configured parameters.
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
import platform
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("crt_trading.runner")

def start_metatrader():
    """Start the MetaTrader 5 terminal if not already running"""
    logger.info("Attempting to start MetaTrader 5...")
    
    # Check common MT5 locations
    mt5_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'MetaTrader 5 EXNESS', 'terminal64.exe'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'MetaTrader 5 EXNESS', 'terminal.exe'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'STARTRADER Financial MetaTrader 5', 'terminal64.exe'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'MetaTrader 5', 'terminal64.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'MetaTrader 5', 'terminal.exe')
    ]
    
    # Try each path
    for path in mt5_paths:
        if os.path.exists(path):
            logger.info(f"Found MetaTrader 5 at: {path}")
            try:
                # Start the terminal
                subprocess.Popen([path])
                logger.info("Started MetaTrader 5 terminal")
                logger.info("Waiting 15 seconds for MT5 to initialize...")
                time.sleep(15)
                return True
            except Exception as e:
                logger.error(f"Failed to start MetaTrader 5: {e}")
    
    logger.error("Could not find MetaTrader 5 terminal executable")
    return False

def check_mt5_connection():
    """Check if we can connect to MetaTrader 5"""
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            error_code = mt5.last_error()
            logger.error(f"Failed to initialize MT5: {error_code}")
            
            if error_code[0] == -10005:  # IPC timeout
                logger.warning("MetaTrader 5 terminal is not running. Attempting to start it...")
                if start_metatrader():
                    # Try initialization again
                    if mt5.initialize():
                        logger.info("Successfully initialized MT5 after starting the terminal")
                        mt5.shutdown()
                        return True
                    else:
                        logger.error(f"Still failed to initialize MT5: {mt5.last_error()}")
            return False
        else:
            logger.info("Successfully connected to MetaTrader 5")
            mt5.shutdown()
            return True
            
    except ImportError:
        logger.error("MetaTrader5 module is not installed")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking MT5 connection: {e}")
        return False

def run_live_trading(interval=5):
    """Run the live trading script"""
    logger.info("="*80)
    logger.info(f"Starting Gold CRT Trading System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # First check MT5 connection
    if not check_mt5_connection():
        logger.error("Cannot establish connection to MetaTrader 5. Please ensure:")
        logger.error("1. MetaTrader 5 is installed")
        logger.error("2. You're logged in to your trading account")
        logger.error("3. Auto trading is enabled")
        return False
    
    # Run the live trading script
    logger.info("Starting live trading...")
    
    try:
        from live_trading import run_live_trading as run_live
        result = run_live(interval=interval)
        return result
    except ImportError:
        logger.error("Could not import live_trading module")
        return False
    except Exception as e:
        logger.error(f"Error running live trading: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='CRT Gold Trading System - Live Trading')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in minutes (default: 5)')
    args = parser.parse_args()
    
    try:
        # Start the trading system
        run_live_trading(interval=args.interval)
    except KeyboardInterrupt:
        logger.info("Trading stopped by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
