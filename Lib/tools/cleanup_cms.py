import os
import sys
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def cleanup():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    # 1. Cleanup Duplicate Categories
    print("[+] Cleaning up duplicate categories...")
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    seen_slugs = set()
    indices_to_remove = []
    
    for i, cat in enumerate(cats):
        if cat["slug"] in seen_slugs:
            indices_to_remove.append(i)
            print(f"    - Found duplicate category: {cat['name']} ({cat['slug']})")
        else:
            seen_slugs.add(cat["slug"])
            
    # Remove from end to preserve indices
    for idx in reversed(indices_to_remove):
        MFDBCore.mfdb_core_remove_entity_record(cms.content_manifest, "Category", idx)

    # 2. Cleanup Old Pages
    print("[+] Cleaning up old pages...")
    pages = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Page")
    page_indices_to_remove = []
    
    # Define "old" pages to remove
    to_remove = ["critical-analysis-mfdb-cms-v1-21"]
    
    for i, p in enumerate(pages):
        if p["slug"] in to_remove:
            page_indices_to_remove.append(i)
            print(f"    - Removing old page: {p['title']}")
            
            # Also need to remove from PageContent
            crecs = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "PageContent")
            for ci, c in enumerate(crecs):
                if c["page_uuid_fk"] == p["page_uuid"]:
                    MFDBCore.mfdb_core_remove_entity_record(cms.content_manifest, "PageContent", ci)
                    print(f"    - Removed content for: {p['title']}")
                    break

    for idx in reversed(page_indices_to_remove):
        MFDBCore.mfdb_core_remove_entity_record(cms.content_manifest, "Page", idx)

    cms.repack_system()
    print("[SUCCESS] Database cleanup complete.")

if __name__ == "__main__":
    cleanup()
