import os
import subprocess

# Exness MetaTrader 5 path
mt5_path = r'C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe'

print(f"Checking Exness MT5 path: {mt5_path}")
if os.path.exists(mt5_path):
    print(f"✅ File exists: {mt5_path}")
    
    try:
        print("Starting Exness MT5 terminal...")
        process = subprocess.Popen([mt5_path])
        print(f"Process started with PID: {process.pid}")
        print("Please check if MetaTrader 5 is running.")
    except Exception as e:
        print(f"❌ Error starting MT5: {e}")
else:
    print(f"❌ File not found: {mt5_path}")
