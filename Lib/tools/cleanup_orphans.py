import os
import sys
import json
from pathlib import Path

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB_DIR = os.path.join(PROJECT_ROOT, "Lib")
sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def run():
    cms = MFDB_CMS_Manager(os.path.join(PROJECT_ROOT, "Data"))
    cms.mount_system(force=True)
    
    # Target UUID to remove
    target_uuid = "d5dd139e-17bc-4c2c-99ea-1b58a9686dc4"
    
    print(f"[+] Removing orphaned page: {target_uuid}")
    
    # 1. Remove from Page entity
    pages = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Page")
    for i, p in enumerate(pages):
        if p["page_uuid"] == target_uuid:
            MFDBCore.mfdb_core_remove_entity_record(cms.content_manifest, "Page", i)
            print("    [OK] Removed from Page entity.")
            break
            
    # 2. Remove from PageContent entity
    contents = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "PageContent")
    for i, c in enumerate(contents):
        if c["page_uuid_fk"] == target_uuid:
            MFDBCore.mfdb_core_remove_entity_record(cms.content_manifest, "PageContent", i)
            print("    [OK] Removed from PageContent entity.")
            break
            
    cms.repack_system()
    print("[*] Cleanup complete and repacked.")

if __name__ == "__main__":
    run()
