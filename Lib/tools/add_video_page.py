import os
import sys
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def add_video():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    # 1. Ensure Resources category exists
    print("[+] Ensuring Resources category exists...")
    cms.add_category("Resources", "resources", "Video tutorials and external assets.", "blog")
    
    # 2. Get Author UUID
    authors = cms.get_authors()
    author_uuid = authors[0]["author_uuid"] if authors else ""
    
    # 3. Create Video Page
    print("[+] Creating Video Page...")
    video_id = "a3eAPR8JIs0"
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    
    content_data = {
        "html_body": "This video provides an in-depth walkthrough of the project features and implementation details.",
        "video_url": embed_url,
        "author_fk": author_uuid
    }
    
    cms.create_page(
        title="Project Feature Walkthrough",
        category_slug="resources",
        page_type="video",
        content_data=content_data
    )
    
    cms.repack_system()
    print("[SUCCESS] Video page added to Resources category.")

if __name__ == "__main__":
    add_video()
