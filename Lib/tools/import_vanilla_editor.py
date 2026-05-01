import os
import sys
import shutil
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager

def import_app():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    cms.mount_system(force=True)
    
    # 1. Ensure Apps category exists
    print("[+] Ensuring Apps category exists...")
    cms.add_category("Apps", "apps", "Interactive BEJSON tools and utilities.", "blog")
    
    # 2. Create the StandaloneApp record
    print("[+] Registering BEJSON Vanilla Editor v7.4 in database...")
    app_name = "BEJSON Vanilla Editor v7.4"
    app_desc = "The industrial-grade BEJSON editor focusing on data integrity, AES-256-GCM encryption, and precise field management."
    
    app_uuid = cms.create_app(
        name=app_name,
        description=app_desc,
        category_fk="apps",
        featured_img="vanilla-editor-v74.png",
        entry_file="index.html"
    )
    
    # 3. Handle physical files
    app_storage_dir = Path(cms.apps_dir) / app_uuid
    os.makedirs(app_storage_dir, exist_ok=True)
    
    source_html = Path("/storage/emulated/0/dev/Projects/BEJSON_Vanilla_Editor_v7.4-release-main/bejson-editor.html")
    dest_html = app_storage_dir / "index.html"
    
    print(f"[+] Copying application files to {app_uuid}...")
    shutil.copy2(source_html, dest_html)
    
    # 4. Finish
    cms.repack_system()
    print(f"[SUCCESS] App imported. UUID: {app_uuid}")

if __name__ == "__main__":
    import_app()
