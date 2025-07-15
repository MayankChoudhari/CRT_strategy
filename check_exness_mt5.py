#!/usr/bin/env python
"""
Check MetaTrader 5 connection using the specific Exness installation
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("check_exness_mt5")

def start_exness_mt5():
    """Start the MetaTrader 5 Exness terminal if it's not already running"""
    mt5_path = r'C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe'
    
    logger.info(f"Checking Exness MetaTrader 5 at: {mt5_path}")
    
    if not os.path.exists(mt5_path):
        logger.error(f"Exness MetaTrader 5 not found at: {mt5_path}")
        return False
    
    try:
        # Check if terminal is already running
        logger.info("Starting Exness MetaTrader 5 terminal...")
        process = subprocess.Popen([mt5_path])
        logger.info(f"Started Exness MT5 with PID: {process.pid}")
        return True
    except Exception as e:
        logger.error(f"Failed to start Exness MT5: {str(e)}")
        return False

def check_mt5_connection():
    """Check connection to MetaTrader 5"""
    try:
        # Import MetaTrader 5
        import MetaTrader5 as mt5
        
        logger.info(f"MetaTrader 5 module version: {mt5.__version__}")
        
        # Initialize MT5
        logger.info("Initializing connection to MetaTrader 5...")
        if not mt5.initialize():
            error_code = mt5.last_error()
            logger.error(f"Failed to initialize MT5: {error_code}")
            
            if error_code[0] == -10005:  # IPC timeout
                logger.warning("MT5 terminal is not running. Starting it now...")
                if not start_exness_mt5():
                    return False
                
                # Wait a bit and try again
                import time
                logger.info("Waiting 10 seconds for MT5 to start...")
                time.sleep(10)
                
                # Try to initialize again
                if not mt5.initialize():
                    logger.error(f"Still failed to initialize MT5: {mt5.last_error()}")
                    return False
            else:
                return False
        
        # Check account info
        account_info = mt5.account_info()
        if account_info is None:
            logger.warning("No account information available. Need to login.")
        else:
            logger.info(f"Connected to account: {account_info.login} on {account_info.server}")
            logger.info(f"Account balance: ${account_info.balance}")
        
        # Check for XAUUSDm symbol
        symbol_info = mt5.symbol_info("XAUUSDm")
        if symbol_info is None:
            logger.error("XAUUSDm symbol not found")
            
            # Try to find available Gold symbols
            gold_symbols = []
            all_symbols = mt5.symbols_get()
            for symbol in all_symbols:
                if "XAU" in symbol.name or "GOLD" in symbol.name:
                    gold_symbols.append(symbol.name)
            
            if gold_symbols:
                logger.info(f"Available Gold symbols: {', '.join(gold_symbols)}")
            
            # Shutdown MT5
            mt5.shutdown()
            return False
        
        logger.info(f"XAUUSDm symbol found:")
        logger.info(f"  Current price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
        
        # Shutdown MT5
        mt5.shutdown()
        logger.info("MT5 connection check completed successfully")
        return True
    
    except ImportError:
        logger.error("MetaTrader5 module not installed. Please install it with: pip install MetaTrader5")
        return False
    except Exception as e:
        logger.error(f"Error checking MT5 connection: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("EXNESS METATRADER 5 CONNECTION CHECK".center(60))
    print("="*60)
    
    check_mt5_connection()
