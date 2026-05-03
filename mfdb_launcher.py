"""
Project: MFDB CMS Reborn
Project Version: v1.3
MFDB Version: v1.3
"""
#!/usr/bin/env python3
import os
import sys
import time

def clear():
    os.system('clear')

def print_banner():
    print("\033[1;31m" + "="*40)
    print("      MFDB CMS REBORN - PORTAL       ")
    print("="*40 + "\033[0m")

def menu():
    while True:
        clear()
        print_banner()
        print("\033[1;37m1.\033[0m \033[1;32m[START]\033[0m  Launch CMS, Editor & Manager")
        print("\033[1;37m2.\033[0m \033[1;31m[STOP]\033[0m   Shutdown All Services")
        print("\033[1;37m3.\033[0m \033[1;34m[STATUS]\033[0m Check Process Health")
        print("\033[1;37m4.\033[0m \033[1;35m[OPEN]\033[0m   Launch Portal in Browser")
        print("\033[1;37m5.\033[0m \033[1;33m[RESTART]\033[0m Bounce Services")
        print("\033[1;37m6.\033[0m [EXIT]    Close Launcher")
        print("\033[1;31m" + "="*40 + "\033[0m")
        
        choice = input("\n\033[1;37mSelect Action > \033[0m")
        
        if choice == '1':
            os.system('python3 Lib/tools/mfdb_control.py start')
            input("\nPress Enter to return to menu...")
        elif choice == '2':
            os.system('python3 Lib/tools/mfdb_control.py stop')
            input("\nPress Enter to return to menu...")
        elif choice == '3':
            os.system('python3 Lib/tools/mfdb_control.py status')
            input("\nPress Enter to return to menu...")
        elif choice == '4':
            os.system('python3 Lib/tools/mfdb_control.py open')
        elif choice == '5':
            os.system('python3 Lib/tools/mfdb_control.py stop')
            time.sleep(1)
            os.system('python3 Lib/tools/mfdb_control.py start')
            input("\nPress Enter to return to menu...")
        elif choice == '6':
            print("Exiting launcher.")
            break
        else:
            print("Invalid choice, try again.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nExiting...")
