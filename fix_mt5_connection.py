#!/usr/bin/env python
"""
fix_mt5_connection.py - Troubleshoot and fix MetaTrader 5 connection issues

This script provides step-by-step diagnostics and attempts to fix common issues
with MetaTrader 5 connectivity for automated trading.
"""

import os
import sys
import time
import subprocess
from datetime import datetime
import platform

def print_header(text):
    """Print a header with formatting"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️ {text}")

def check_python_installation():
    """Check Python installation details"""
    print_header("PYTHON ENVIRONMENT")
    
    print(f"Python version: {platform.python_version()}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check pip installation
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_success("pip is properly installed")
    except:
        print_error("pip is not properly installed or accessible")

def check_mt5_module():
    """Check MetaTrader5 module installation"""
    print_header("METATRADER 5 MODULE")
    
    try:
        import MetaTrader5 as mt5
        print_success(f"MetaTrader5 module is installed (version: {mt5.__version__})")
        print(f"Module path: {os.path.dirname(mt5.__file__)}")
        return mt5
    except ImportError as e:
        print_error(f"Failed to import MetaTrader5 module: {e}")
        print_info("Attempting to install MetaTrader5 module...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "MetaTrader5"], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print_success("MetaTrader5 module installed successfully")
            
            # Try importing again
            try:
                import MetaTrader5 as mt5
                print_success(f"MetaTrader5 module is now installed (version: {mt5.__version__})")
                return mt5
            except ImportError as e:
                print_error(f"Still unable to import MetaTrader5 module: {e}")
                return None
        except Exception as e:
            print_error(f"Failed to install MetaTrader5 module: {e}")
            print_info("You can try installing it manually with: pip install MetaTrader5")
            return None

def find_mt5_terminal():
    """Find MetaTrader 5 terminal installation"""
    print_header("METATRADER 5 TERMINAL")
    
    # Common MT5 installation paths
    common_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'MetaTrader 5'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'MetaTrader 5'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'MetaTrader 5'),
        # Add more common paths here
    ]
      # Check common paths
    found_paths = []
    
    # Add broker-specific MT5 paths
    broker_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'MetaTrader 5 EXNESS'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'STARTRADER Financial MetaTrader 5'),
        # Add other potential broker paths
    ]
    
    common_paths.extend(broker_paths)
    
    for path in common_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    if found_paths:
        print_success("Found MetaTrader 5 installation(s):")
        for i, path in enumerate(found_paths, 1):
            print(f"  {i}. {path}")
        return found_paths
    else:
        print_error("Could not find MetaTrader 5 installation in common paths")
        print_warning("Please make sure MetaTrader 5 is installed")
        print_info("If installed in a non-standard location, please locate terminal.exe manually")
        return None

def check_mt5_connection(mt5):
    """Check connection to MetaTrader 5 terminal"""
    if mt5 is None:
        return False
        
    print_header("METATRADER 5 CONNECTION")
    
    print_info("Initializing connection to MetaTrader 5 terminal...")
    
    # Try to initialize
    try:
        if not mt5.initialize():
            error_code = mt5.last_error()
            print_error(f"Failed to initialize MT5 (Error code: {error_code})")
            
            if error_code == 10013:
                print_warning("This error indicates that the MetaTrader 5 terminal is not running.")
                print_info("Please start the MetaTrader 5 terminal and try again.")
                
                # Try to start terminal automatically                terminal_paths = find_mt5_terminal()
                if terminal_paths:
                    try:
                        # Try both terminal.exe and terminal64.exe (64-bit version)
                        terminal_path = os.path.join(terminal_paths[0], 'terminal.exe')
                        terminal64_path = os.path.join(terminal_paths[0], 'terminal64.exe')
                        
                        if os.path.exists(terminal64_path):
                            print_info(f"Attempting to start MetaTrader 5 automatically from: {terminal64_path}")
                            subprocess.Popen([terminal64_path])
                        elif os.path.exists(terminal_path):
                            print_info(f"Attempting to start MetaTrader 5 automatically from: {terminal_path}")
                            subprocess.Popen([terminal_path])
                        else:
                            print_warning(f"No terminal.exe or terminal64.exe found in {terminal_paths[0]}")
                            
                        print_info("Waiting 10 seconds for MT5 to start...")
                        time.sleep(10)
                        
                        # Try initialization again
                        if mt5.initialize():
                            print_success("Successfully initialized MT5 after starting the terminal")
                        else:
                            print_error(f"Still failed to initialize MT5: {mt5.last_error()}")
                    except Exception as e:
                        print_error(f"Failed to start MT5 terminal: {e}")
            elif error_code == 10018:
                print_warning("This error indicates network connection issues.")
                print_info("Check your internet connection and MT5 terminal settings.")
            else:
                print_warning(f"Unknown error occurred. Error code: {error_code}")
                print_info("Make sure MT5 terminal is running and properly configured.")
            
            return False
        else:
            print_success("Successfully initialized MT5")
    except Exception as e:
        print_error(f"Unexpected error during initialization: {e}")
        return False
    
    # Check terminal information
    try:
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            print_error("Failed to get terminal information")
            return False
            
        print_info("Terminal Information:")
        print(f"  Terminal name: {terminal_info.name}")
        print(f"  Terminal path: {terminal_info.path}")
        print(f"  Connected to broker: {'Yes' if terminal_info.connected else 'No'}")
        print(f"  Auto trading allowed: {'Yes' if terminal_info.trade_allowed else 'No'}")
        
        if not terminal_info.connected:
            print_warning("Terminal is not connected to the broker")
            print_info("Check your internet connection and make sure you're logged in to your account")
            
        if not terminal_info.trade_allowed:
            print_warning("Auto trading is not allowed in the terminal")
            print_info("Please enable auto trading in MT5:")
            print_info("  1. Open MT5 terminal")
            print_info("  2. Click the 'Auto Trading' button in the toolbar (or press Ctrl+E)")
            print_info("  3. Go to Tools > Options > Expert Advisors > Allow automated trading")
    except Exception as e:
        print_error(f"Error getting terminal information: {e}")
    
    # Try to get account information
    try:
        account_info = mt5.account_info()
        if account_info is None:
            print_warning("Failed to get account information")
            print_info("Make sure you're logged in to your trading account")
        else:
            print_success("Successfully connected to trading account")
            print_info("Account Information:")
            print(f"  Login: {account_info.login}")
            print(f"  Server: {account_info.server}")
            print(f"  Currency: {account_info.currency}")
            print(f"  Balance: {account_info.balance}")
            print(f"  Equity: {account_info.equity}")
            print(f"  Margin: {account_info.margin}")
            print(f"  Free Margin: {account_info.margin_free}")
            print(f"  Leverage: 1:{account_info.leverage}")
    except Exception as e:
        print_error(f"Error getting account information: {e}")
    
    # Check for Gold symbols
    try:
        symbols = mt5.symbols_get()
        if symbols is None:
            print_warning("Failed to get symbols")
            print_info("Make sure you have an active internet connection")
        else:
            print_success(f"Found {len(symbols)} trading symbols")
            
            # Check for Gold symbols
            gold_symbols = [s for s in symbols if "GOLD" in s.name or "XAU" in s.name]
            if gold_symbols:
                print_success(f"Found {len(gold_symbols)} Gold-related symbols:")
                for i, symbol in enumerate(gold_symbols, 1):
                    print(f"  {i}. {symbol.name}")
                    
                    # Check if we can get the current price
                    symbol_info = mt5.symbol_info(symbol.name)
                    if symbol_info and symbol_info.bid > 0:
                        print(f"     Current price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
                    else:
                        print(f"     Could not get current price")
            else:
                print_warning("No Gold-related symbols found")
                print_info("Make sure your broker provides Gold (XAUUSD) trading")
    except Exception as e:
        print_error(f"Error checking symbols: {e}")
    
    # Test specific symbol
    try:
        # Import config
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src import config
        
        symbol = config.MT5_SYMBOL
        print_info(f"Testing connection for symbol: {symbol}")
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print_error(f"Symbol {symbol} not found")
            print_info(f"Check if the symbol name is correct in config.py (MT5_SYMBOL = '{symbol}')")
        else:
            print_success(f"Symbol {symbol} found")
            print_info(f"Symbol Information:")
            print(f"  Description: {symbol_info.description}")
            print(f"  Path: {symbol_info.path}")
            print(f"  Contract size: {symbol_info.trade_contract_size}")
            print(f"  Digits: {symbol_info.digits}")
            print(f"  Current price: Bid=${symbol_info.bid:.2f}, Ask=${symbol_info.ask:.2f}")
    except Exception as e:
        print_error(f"Error testing symbol: {e}")
    
    # Clean up
    mt5.shutdown()
    print_info("MT5 connection test complete")
    
    return True

def main():
    """Main function"""
    print_header("METATRADER 5 CONNECTION FIXER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run checks
    check_python_installation()
    mt5 = check_mt5_module()
    find_mt5_terminal()
    connection_ok = check_mt5_connection(mt5)
    
    print_header("FIX SUMMARY")
    if connection_ok:
        print_success("MetaTrader 5 connection is working correctly!")
        print_info("You can now run the Gold trading system.")
    else:
        print_warning("Some issues were found with your MetaTrader 5 connection.")
        print_info("Please address the problems identified above and try again.")
        
        print("\nCommon Solutions:")
        print("1. Make sure MetaTrader 5 terminal is running")
        print("2. Enable Auto Trading in the terminal")
        print("3. Log in to your trading account")
        print("4. Check your internet connection")
        print("5. Verify the symbol name in config.py")
        print("6. If using a demo account, make sure it hasn't expired")

if __name__ == "__main__":
    main()
