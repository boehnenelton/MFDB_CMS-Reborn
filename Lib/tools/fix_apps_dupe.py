import os
import sys
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def fix_dupe():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    print("[+] Consolidating 'Apps' categories...")
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    
    apps_indices = []
    for i, cat in enumerate(cats):
        if cat["slug"] == "apps":
            apps_indices.append(i)
            
    if len(apps_indices) > 1:
        # Keep the first one, remove the rest (start from back)
        to_remove = apps_indices[1:]
        for idx in reversed(to_remove):
            print(f"    - Removing duplicate at index {idx}")
            MFDBCore.mfdb_core_remove_entity_record(cms.content_manifest, "Category", idx)
        
        cms.repack_system()
        print("[SUCCESS] Categories consolidated.")
    else:
        print("[*] No duplicate Apps category found.")

if __name__ == "__main__":
    fix_dupe()
