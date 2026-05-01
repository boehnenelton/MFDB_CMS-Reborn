import os
import sys
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def add_crash_course():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    # 1. Read the Crash Course Markdown
    cc_path = Path("/storage/emulated/0/dev/BEJSON_CRASH_COURSE13.1.md")
    if not cc_path.exists():
        print(f"[!] Error: Crash course not found at {cc_path}")
        return
        
    markdown_content = cc_path.read_text()
    
    # 2. Get Author UUID
    authors = cms.get_authors()
    author_uuid = authors[0]["author_uuid"] if authors else ""
    
    # 3. Create Article Page
    print("[+] Creating Crash Course article page...")
    content_data = {
        "html_body": "<h1>BEJSON & MFDB Crash Course</h1><p>Comprehensive guide to the BEJSON tabular data format and the Multifile Database (MFDB) v1.2 specification.</p>",
        "markdown_body": markdown_content,
        "author_fk": author_uuid,
        "featured_img": "bejson-banner.png" # Placeholder if exists
    }
    
    cms.create_page(
        title="BEJSON & MFDB Crash Course",
        category_slug="bejson",
        page_type="article",
        content_data=content_data
    )
    
    cms.repack_system()
    print("[SUCCESS] Crash Course added to BEJSON category.")

if __name__ == "__main__":
    add_crash_course()
