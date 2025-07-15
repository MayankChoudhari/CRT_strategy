#!/usr/bin/env python
"""
check_all_accounts.py - Test all available MT5 account combinations

This script tests multiple account configurations to find a working one.
"""

import os
import time
from datetime import datetime
import logging

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mt5_account_check.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mt5_account_checker")

# Account configurations to test
ACCOUNTS = [
    {
        "name": "Exness (Original)",
        "server": "Exness-MT5Trial7",
        "login": 205568819,
        "password": "Sx!0SpVs",
        "symbols": ["XAUUSDm", "GOLD.e", "XAUUSDm.e"]
    },
    {
        "name": "Ava-Demo (README)",
        "server": "Ava-Demo 1-MT5",
        "login": 107032874,
        "password": "Sx!0SpVs",
        "symbols": ["GOLD", "XAUUSD", "XAU/USD"]
    },
    {
        "name": "STARTRADER (Test)",
        "server": "STARTRADERFinancial-Live",
        "login": 1358521,
        "password": "Sx!0SpVs",
        "symbols": ["XAUUSD.c", "GOLD", "XAU/USD"]
    }
]

def test_account(account):
    """Test connection to a specific MT5 account"""
    logger.info(f"Testing connection to {account['name']}")
    logger.info(f"Server: {account['server']}, Login: {account['login']}")
    
    try:
        import MetaTrader5 as mt5
        
        # Initialize MT5
        if not mt5.initialize():
            error = mt5.last_error()
            logger.error(f"Failed to initialize MT5: {error}")
            return False, None
        
        # Try to login
        logger.info(f"Logging in to {account['server']} with account {account['login']}...")
        login_result = mt5.login(
            login=account['login'],
            password=account['password'],
            server=account['server']
        )
        
        if not login_result:
            error = mt5.last_error()
            logger.error(f"Login failed: {error}")
            mt5.shutdown()
            return False, None
        
        logger.info("Login successful!")
        
        # Get account info
        account_info = mt5.account_info()
        if account_info is not None:
            logger.info(f"Connected to account: {account_info.login} on {account_info.server}")
            logger.info(f"Name: {account_info.name}, Balance: ${account_info.balance:.2f}")
        
        # Check available symbols
        working_symbols = []
        for symbol in account['symbols']:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is not None:
                logger.info(f"Symbol {symbol} is available!")
                working_symbols.append(symbol)
                
                # Get current price
                tick = mt5.symbol_info_tick(symbol)
                if tick is not None:
                    logger.info(f"{symbol} price: Bid=${tick.bid:.2f}, Ask=${tick.ask:.2f}")
            else:
                logger.warning(f"Symbol {symbol} not found")
        
        # Clean up
        mt5.shutdown()
        
        if working_symbols:
            return True, {
                "name": account['name'],
                "server": account['server'],
                "login": account['login'],
                "password": account['password'],
                "symbol": working_symbols[0],
                "working_symbols": working_symbols
            }
        else:
            logger.error(f"No working Gold symbols found for {account['name']}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error testing account {account['name']}: {str(e)}")
        return False, None

def main():
    print("=" * 80)
    print("METATRADER 5 ACCOUNT CHECKER".center(80))
    print("=" * 80)
    print(f"Testing {len(ACCOUNTS)} account configurations for Gold trading")
    
    working_configs = []
    
    for i, account in enumerate(ACCOUNTS, 1):
        print(f"\nTesting configuration {i}/{len(ACCOUNTS)}: {account['name']}")
        
        success, config = test_account(account)
        if success:
            working_configs.append(config)
            print(f"✅ Configuration {i} works!")
        else:
            print(f"❌ Configuration {i} failed!")
        
        # Wait a bit between tests
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY".center(80))
    print("=" * 80)
    
    if working_configs:
        print(f"Found {len(working_configs)} working configurations:")
        for i, config in enumerate(working_configs, 1):
            print(f"\nWorking Config #{i}: {config['name']}")
            print(f"  Server: {config['server']}")
            print(f"  Login: {config['login']}")
            print(f"  Symbols: {', '.join(config['working_symbols'])}")
        
        # Save the best config to a file
        best_config = working_configs[0]  # Use the first working config
        with open("working_mt5_config.py", "w") as f:
            f.write("# MT5 configuration generated by check_all_accounts.py\n")
            f.write(f"MT5_ENABLED = True\n")
            f.write(f"MT5_LOGIN = {best_config['login']}\n")
            f.write(f"MT5_PASSWORD = \"{best_config['password']}\"\n")
            f.write(f"MT5_SERVER = \"{best_config['server']}\"\n")
            f.write(f"MT5_SYMBOL = \"{best_config['symbol']}\"\n")
            f.write(f"MT5_INVESTOR_PASSWORD = \"Q*3iWqEw\"  # Default investor password\n")
            
        print(f"\nSaved best configuration to working_mt5_config.py")
    else:
        print("No working configurations found.")
        print("Please check that MetaTrader 5 is running and your credentials are correct.")

if __name__ == "__main__":
    main()
