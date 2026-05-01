import os
import sys
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def finalize():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    # 1. Create Author
    print("[+] Creating Author: Elton Boehnen...")
    author_uuid = cms.add_author(
        name="Elton Boehnen",
        bio="Lead Architect of the BEJSON standard and developer of the MFDB CMS ecosystem.",
        image_url="author-elton.png" # Placeholder
    )
    
    # 2. Update Pages with Author
    # We need to find the pages we just created in the content manifest
    pages = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Page")
    
    for p in pages:
        if p["slug"] in ["gemini-cli-orchestrator", "gemini-schema-standardization"]:
            print(f"[+] Updating page '{p['title']}' with author...")
            # We use update_page but we only want to change author_fk
            # The lib_cms_mfdb update_page needs the full content_data
            full_data = cms.get_full_page_data(p["page_uuid"])
            full_data["author_fk"] = author_uuid
            cms.update_page(
                page_uuid=p["page_uuid"],
                title=p["title"],
                category_slug=p["category_fk"],
                page_type=p["page_type"],
                content_data=full_data
            )

    cms.repack_system()
    print("[SUCCESS] Pages updated with author and date metadata.")

if __name__ == "__main__":
    finalize()
