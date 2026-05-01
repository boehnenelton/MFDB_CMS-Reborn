import os
import sys
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def rename_page():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    # 1. Find the page
    pages = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Page")
    target_uuid = None
    category_slug = None
    
    for p in pages:
        if p["slug"] == "project-feature-walkthrough":
            target_uuid = p["page_uuid"]
            category_slug = p["category_fk"]
            break
            
    if not target_uuid:
        print("[!] Target page not found.")
        return

    # 2. Update the title and content
    print(f"[+] Renaming page {target_uuid} to 'Tabulated Json'...")
    full_data = cms.get_full_page_data(target_uuid)
    
    cms.update_page(
        page_uuid=target_uuid,
        title="Tabulated Json",
        category_slug=category_slug,
        page_type="video",
        content_data=full_data
    )
    
    cms.repack_system()
    print("[SUCCESS] Page renamed to 'Tabulated Json'.")

if __name__ == "__main__":
    rename_page()
