"""
Library:     lib_be_core.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL) CoreEvo fork
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
from pathlib import Path
_DEFAULT_BEC_ROOT = str(Path(__file__).resolve().parent.parent.parent)

def get_bec_root():
    root_env = os.environ.get("BEC_ROOT")
    if root_env:
        return root_env
        
    # Default behavior if env var not set
    root_file = os.path.join(_DEFAULT_BEC_ROOT, "data/state/BEC_ROOT.txt")
    if os.path.exists(root_file):
        with open(root_file, 'r') as f:
            return f.read().strip()
    return _DEFAULT_BEC_ROOT

# State Management - Save a key-value pair to a manager state file
def save_state(manager, key, value):
    root = get_bec_root()
    state_file = os.path.join(root, f"data/state/{manager}_manager_state.txt")
    
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    
    lines = []
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            lines = f.readlines()
            
    key_found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            key_found = True
        else:
            new_lines.append(line)
            
    if not key_found:
        new_lines.append(f"{key}={value}\n")
        
    with open(state_file, 'w') as f:
        f.writelines(new_lines)
        f.flush()
        os.fsync(f.fileno())

# State Management - Load a value by key from a manager state file
def load_state(manager, key):
    root = get_bec_root()
    state_file = os.path.join(root, f"data/state/{manager}_manager_state.txt")
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
    return ""

def load_all_state(manager):
    root = get_bec_root()
    state_file = os.path.join(root, f"data/state/{manager}_manager_state.txt")
    state_dict = {}
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            for line in f:
                if "=" in line:
                    k, v = line.split("=", 1)
                    state_dict[k.strip()] = v.strip()
    return state_dict
