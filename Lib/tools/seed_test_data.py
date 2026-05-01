"""
Seed Test Data - Professional Suite & NexusDraw App
"""
import os
import sys
import shutil

# Add Lib to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "Lib")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager

def seed():
    DATA_ROOT = os.path.join(BASE_DIR, "Data")
    cms = MFDB_CMS_Manager(DATA_ROOT)
    
    print("Executing Factory Reset...")
    cms.factory_reset()
    cms.initialize_system()

    # Create Categories
    print("Setting up categories...")
    cms.add_category("Education", "course", "In-depth learning paths and crash courses.", "blog")
    cms.add_category("Open Source", "libraries", "Professional grade source code repositories.", "card-grid")
    cms.add_category("Utilities", "apps", "Interactive high-performance standalone tools.", "blog")

    # 1. Standard Article: BEJSON Crash Course
    cms.create_page(
        "BEJSON & MFDB Crash Course", "course", "article", 
        {
            "html_body": "<h2>Mastering the Standard</h2><p>Complete guide to positional integrity and multi-file database orchestration.</p>",
            "featured_img": ""
        }
    )

    # 2. Source Code: Python
    cms.create_page(
        "BEJSON CMS Python SDK", "libraries", "source-code", 
        {
            "html_body": "Official Python client for atomic MFDB operations.",
            "source_files": [{"filename": "main.py", "content": "print('Python Core Active')"}]
        }
    )

    # 3. Source Code: Bash
    cms.create_page(
        "Core Shell Automators", "libraries", "source-code", 
        {
            "html_body": "CI/CD pipelines for static site generation.",
            "source_files": [{"filename": "deploy.sh", "content": "echo 'Deploying...'"}]
        }
    )

    # 4. Source Code: JavaScript
    cms.create_page(
        "NexusJS Frontend Core", "libraries", "source-code", 
        {
            "html_body": "High-performance vanilla JS components.",
            "source_files": [{"filename": "core.js", "content": "console.log('JS Core Active')"}]
        }
    )

    # 5. Import Standalone App: NexusDraw
    print("Registering NexusDraw App...")
    app_uuid = cms.create_app(
        "NexusDraw", 
        "A minimalist high-contrast drawing utility restricted to black, white, and red.",
        "apps", 
        "", # No featured img yet
        "index.html"
    )
    # Deploy app file
    app_dir = os.path.join(cms.apps_dir, app_uuid)
    os.makedirs(app_dir, exist_ok=True)
    # Copy from project root to app storage
    shutil.copy(os.path.join(os.path.dirname(BASE_DIR), "MFDB-CMS-Reborn/drawing-app.html"), os.path.join(app_dir, "index.html"))

    print("Seed complete.")

if __name__ == "__main__":
    seed()
