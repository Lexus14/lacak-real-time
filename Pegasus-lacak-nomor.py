"""
PEGASUS LACAK NOMOR - LEGACY VERSION (DEPRECATED)

This is the legacy version (v1.0) of Pegasus Lacak Nomor.
This version has been DEPRECATED and should NOT be used.

PLEASE USE: main.py instead

The legacy version used simulation mode which has been removed from the application.
Only real tracking via API/Database is supported now.

To use the current version:
    python main.py

Created by: Letda Kes dr. Sobri
"""

import sys
from colorama import init, Fore, Style

init()

def main():
    print(f"""
    {Fore.RED}╔════════════════════════════════════════════════════════════════════════════╗
    ║                              DEPRECATED FILE                              ║
    ╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    
    {Fore.YELLOW}[!] This legacy version (v1.0) is DEPRECATED.
    [!] Simulation mode has been removed from the application.
    
    {Fore.GREEN}[✓] Please use: python main.py
    {Fore.GREEN}[✓] Current version: v3.0 with Real Tracking
    
    {Style.RESET_ALL}""")

if __name__ == "__main__":
    main()
    sys.exit(1)
