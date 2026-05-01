"""
Library:     lib_bejson_server.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL) CoreEvo fork
Date:        2026-04-23
Description: Flask server management with port randomization, registration, and auto-launch.
"""
import os
import socket
import random
import subprocess
import sys
import json
import time
from datetime import datetime

# JURISDICTIONS: ["PYTHON", "WEB_ARCHITECTURE", "CORE_COMMAND"]

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_random_available_port(start=5001, end=5020):
    ports = list(range(start, end + 1))
    random.shuffle(ports)
    for port in ports:
        if not is_port_in_use(port):
            return port
    return None

def register_server(name, port):
    reg_path = '/data/data/com.termux/files/home/CoreEvolution/Registry/Environment_Registry.bejson.json'
    if not os.path.exists(reg_path): return
    try:
        with open(reg_path, 'r') as f:
            data = json.load(f)
        data['Values'] = [v for v in data['Values'] if not (v[0] == 'Running_Server' and v[3] == name)]
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        url = f"http://localhost:{port}"
        record = ['Running_Server', now, 'ServerLib', name, url, None, None, str(port), 'ONLINE', 'Global']
        data['Values'].append(record)
        with open(reg_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f" [ServerLib] REGISTERED: {name} on {url}")
    except Exception as e:
        print(f" [ServerLib] Registration Error: {e}")

def unregister_server(name):
    reg_path = '/data/data/com.termux/files/home/CoreEvolution/Registry/Environment_Registry.bejson.json'
    if not os.path.exists(reg_path): return
    try:
        with open(reg_path, 'r') as f:
            data = json.load(f)
        data['Values'] = [v for v in data['Values'] if not (v[0] == 'Running_Server' and v[3] == name)]
        with open(reg_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f" [ServerLib] UNREGISTERED: {name}")
    except Exception as e:
        print(f" [ServerLib] Unregistration Error: {e}")

def start_flask_server_random(app_path, name=None, debug=False):
    port = get_random_available_port()
    if port is None:
        print("FAIL | No available ports.")
        return False

    app_name = name or os.path.splitext(os.path.basename(app_path))[0]
    register_server(app_name, port)
    
    url = f"http://localhost:{port}"
    print(f"--- BEJSON SERVER STARTER ---")
    print(f"Name: {app_name}")
    print(f"Port: {port}")
    print(f"OPEN_URL:{url}")
    # Mandate: Copy URL to clipboard
    try:
        subprocess.run(["termux-clipboard-set", url])
        print(" [ServerLib] URL copied to clipboard.")
    except:
        pass

    
    # Mandate: Auto-launch
    try:
        subprocess.Popen(['termux-open-url', url])
    except:
        pass
    
    env = os.environ.copy()
    env['FLASK_APP'] = app_path
    env['FLASK_DEBUG'] = '1' if debug else '0'
    
    try:
        subprocess.run(['flask', 'run', '--host=0.0.0.0', '--port', str(port)], env=env)
    finally:
        unregister_server(app_name)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        start_flask_server_random(sys.argv[1])
    else:
        print("Usage: python3 lib_bejson_server.py <app_path>")
