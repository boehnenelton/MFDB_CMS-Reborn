import os
import sys
import json
from pathlib import Path

# Add Lib to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "Lib"
sys.path.append(str(LIB_DIR))

from lib_cms_mfdb import MFDB_CMS_Manager

def add_showcase():
    data_root = str(BASE_DIR / "Data")
    cms = MFDB_CMS_Manager(data_root)
    
    # 1. Mount system
    print("[+] Mounting system...")
    cms.mount_system(force=True)
    
    # 2. Prepare Category
    print("[+] Ensuring BEJSON category exists...")
    cms.add_category("BEJSON", "bejson", "Core BEJSON standards and tools.", "blog")
    
    # 3. Read the 5 files
    cli_test_dir = Path("/storage/emulated/0/dev/Projects/cli_test")
    files_to_read = [
        ("prompter.py", cli_test_dir / "prompter.py"),
        ("router.json", cli_test_dir / "router.json"),
        ("gemini_profile_template.bejson", cli_test_dir / "configuration/gemini_profile_template.bejson"),
        ("gemini_key_template.104a.bejson", cli_test_dir / "configuration/gemini_key_template.104a.bejson"),
        ("gemini_model_template.104a.bejson", cli_test_dir / "configuration/gemini_model_template.104a.bejson")
    ]
    
    source_files = []
    for name, path in files_to_read:
        if path.exists():
            print(f"[+] Reading {name}...")
            content = path.read_text()
            source_files.append({"filename": name, "content": content})
        else:
            print(f"[!] Warning: {name} not found at {path}")

    # 4. Create Page
    print("[+] Creating Project Rebuilder showcase page...")
    content_data = {
        "html_body": "<p>This showcase features the <strong>Headless Gemini CLI Orchestrator</strong>. It demonstrates standardized BEJSON schemas for profiles, models, and key registries, orchestrated by a robust Python engine with Round Robin rotation and rate limiting.</p>",
        "source_files": source_files
    }
    
    cms.create_page(
        title="Gemini CLI Orchestrator",
        category_slug="bejson",
        page_type="source-code",
        content_data=content_data
    )
    
    # 5. Repack and finish
    print("[+] Committing changes...")
    cms.repack_system()
    print("[SUCCESS] Page added to BEJSON category.")

if __name__ == "__main__":
    add_showcase()
