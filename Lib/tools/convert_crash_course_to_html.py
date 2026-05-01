import os
import sys
import markdown
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

def convert():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    # 1. Read Markdown
    cc_path = Path("/storage/emulated/0/dev/BEJSON_CRASH_COURSE13.1.md")
    md_content = cc_path.read_text()
    
    # 2. Convert to HTML
    # We use 'extra' for tables and 'fenced_code' for code blocks
    html_output = markdown.markdown(md_content, extensions=['extra', 'fenced_code', 'toc'])
    
    # 3. Find the page
    pages = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Page")
    target_uuid = None
    for p in pages:
        if p["slug"] == "bejson-&-mfdb-crash-course":
            target_uuid = p["page_uuid"]
            break
            
    if not target_uuid:
        print("[!] Crash Course page not found.")
        return

    # 4. Update html_body
    print(f"[+] Updating HTML content for {target_uuid}...")
    full_data = cms.get_full_page_data(target_uuid)
    full_data["html_body"] = f'<div class="auto-format">{html_output}</div>'
    
    cms.update_page(
        page_uuid=target_uuid,
        title=full_data["title"],
        category_slug=full_data["category_fk"],
        page_type="article",
        content_data=full_data
    )
    
    cms.repack_system()
    print("[SUCCESS] Content converted to HTML and updated.")

if __name__ == "__main__":
    convert()
