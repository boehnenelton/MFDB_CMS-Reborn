#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import signal

# Configuration
PORT_CMS = 5005
PORT_EDITOR = 5006
PORT_MANAGER = 5007
# Since this tool is in Lib/tools/, project root is two levels up
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SERVICES = {
    "CMS": {"file": "MFDB_CMS.py", "port": PORT_CMS},
    "Editor": {"file": "MFDB_Editor.py", "port": PORT_EDITOR},
    "Manager": {"file": "MFDB_Site_Manager.py", "port": PORT_MANAGER}
}

def get_pids():
    pids = {}
    try:
        output = subprocess.check_output(["ps", "-A", "-o", "pid,args"]).decode()
        for line in output.splitlines():
            for name, svc in SERVICES.items():
                if svc["file"] in line and "python" in line:
                    pids[name] = line.strip().split()[0]
    except:
        pass
    return pids

def start():
    pids = get_pids()
    for name, svc in SERVICES.items():
        if name in pids:
            print(f"[-] {name} is already running (PID {pids[name]})")
        else:
            print(f"[+] Starting {name}...")
            # Keep logs in project root
            log_path = os.path.join(PROJECT_ROOT, f"{name.lower()}.log")
            log_file = open(log_path, "w")
            subprocess.Popen([sys.executable, svc["file"]], 
                             cwd=PROJECT_ROOT, 
                             stdout=log_file, 
                             stderr=log_file)
            print(f"    URL: http://127.0.0.1:{svc['port']}")
    print("\n[!] Use 'termux-open http://127.0.0.1:5005' to open in browser.")

def stop():
    pids = get_pids()
    if not pids:
        print("[-] No services are running.")
        return
    for name, pid in pids.items():
        print(f"[!] Stopping {name} (PID {pid})...")
        os.kill(int(pid), signal.SIGTERM)

def status():
    pids = get_pids()
    print("\n--- MFDB Service Status ---")
    for name, svc in SERVICES.items():
        state = f"RUNNING (PID {pids[name]})" if name in pids else "STOPPED"
        print(f"{name:10} : {state}")
    print("---------------------------\n")

def open_browser():
    print("[+] Opening CMS Portal...")
    subprocess.run(["termux-open", f"http://127.0.0.1:{PORT_CMS}"])

def usage():
    print("Usage: python3 mfdb_control.py [start|stop|status|open]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
    else:
        cmd = sys.argv[1].lower()
        if cmd == "start": start()
        elif cmd == "stop": stop()
        elif cmd == "status": status()
        elif cmd == "open": open_browser()
        else: usage()
