import subprocess
import time
import os
import sys
import psutil

# Path to your Exness MT5 terminal (portable mode)
MT5_PATHS = [
    os.path.join(os.getcwd(), "MetaTrader 5 EXNESS", "terminal64.exe"),
    os.path.join(os.getcwd(), "MetaTrader 5 EXNESS", "terminal.exe"),
    r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe",
    r"C:\Program Files\MetaTrader 5 EXNESS\terminal.exe"
]
MT5_PATH = None
for path in MT5_PATHS:
    if os.path.exists(path):
        MT5_PATH = path
        break
if MT5_PATH is None:
    print("Could not find Exness MT5 terminal (terminal64.exe or terminal.exe). Please check the path.")
    sys.exit(1)
MT5_WORKDIR = os.path.dirname(MT5_PATH)
STRATEGY_SCRIPT = "exness_crt_trader.py"  # Your Exness strategy script

def start_mt5():
    # Check if MT5 is already running from this folder
    try:
        for proc in psutil.process_iter(['name', 'cwd']):
            if proc.info['name'] and 'terminal64.exe' in proc.info['name'].lower():
                if proc.info['cwd'] and os.path.normcase(proc.info['cwd']) == os.path.normcase(MT5_WORKDIR):
                    print("Exness MT5 already running in portable mode.")
                    return
    except ImportError:
        print("psutil not installed, skipping process check.")
    print(f"Starting Exness MT5 terminal from {MT5_PATH} ...")
    subprocess.Popen([MT5_PATH, "/portable"], cwd=MT5_WORKDIR)
    time.sleep(10)  # Wait for terminal to initialize

def run_strategy():
    print("Running Exness CRT strategy...")
    subprocess.run([sys.executable, STRATEGY_SCRIPT])

def detect_conflicting_mt5_terminals():
    conflicting = []
    for proc in psutil.process_iter(['name', 'exe', 'cwd', 'cmdline']):
        try:
            name = proc.info['name']
            exe = proc.info.get('exe')
            cwd = proc.info.get('cwd')
            cmdline = proc.info.get('cmdline')
            if name and ('terminal64.exe' in name.lower() or 'terminal.exe' in name.lower()):
                # If not Exness folder, it's a conflict
                if cwd and os.path.normcase(cwd) != os.path.normcase(MT5_WORKDIR):
                    conflicting.append({'pid': proc.pid, 'exe': exe, 'cwd': cwd, 'cmdline': cmdline})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return conflicting

if __name__ == "__main__":
    conflicts = detect_conflicting_mt5_terminals()
    if conflicts:
        print("WARNING: Conflicting MetaTrader 5 terminals detected!\n")
        for c in conflicts:
            print(f"PID: {c['pid']} | Path: {c['exe']} | CWD: {c['cwd']} | CMD: {c['cmdline']}")
        print("\nPlease close all non-Exness MT5 terminals before running this bot. Exiting.")
        sys.exit(1)
    start_mt5()
    run_strategy()
