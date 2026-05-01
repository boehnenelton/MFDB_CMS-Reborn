import os
import sys
import hashlib
import shutil
from datetime import datetime, timezone

# Add Lib to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB_DIR = os.path.join(PROJECT_ROOT, "Lib")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

DATA_ROOT = os.path.join(PROJECT_ROOT, "Data")
cms = MFDB_CMS_Manager(DATA_ROOT)

def setup_test_data():
    print("Initializing system...")
    cms.initialize_system()
    
    # 1. Import the image
    img_name = "MFDBCMS.png"
    img_path = os.path.join(PROJECT_ROOT, img_name)
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        f_hash = hashlib.sha256(data).hexdigest()
        dest_path = os.path.join(cms.assets_dir, img_name)
        shutil.copy2(img_path, dest_path)
        cms.add_asset(img_name, img_name, f_hash, len(data), "image/png")
        print(f"Asset {img_name} added.")
    else:
        print(f"Error: {img_name} not found at {img_path}")
        return

    # 2. Create Categories
    print("Creating categories...")
    cms.add_category("Official News", "news", "System updates and news.", "blog")
    cms.add_category("Documentation", "docs", "How to use the MFDB CMS.", "card-grid")
    cms.add_category("Showcase", "showcase", "Built with MFDB.", "gallery")

    # 3. Create Pages
    print("Creating pages...")
    cms.create_page(
        title="Welcome to MFDB CMS Reborn",
        category_slug="news",
        page_type="article",
        content_data={
            "featured_img": img_name,
            "html_body": "<p>This is a fresh start for the MFDB CMS. Performance and tabular integrity at its core.</p>"
        }
    )

    cms.create_page(
        title="Understanding BEJSON 104a",
        category_slug="docs",
        page_type="article",
        content_data={
            "featured_img": img_name,
            "html_body": "<p>BEJSON 104a is the manifest standard for MFDB databases.</p>"
        }
    )

    cms.create_page(
        title="Responsive Design Demo",
        category_slug="showcase",
        page_type="article",
        content_data={
            "featured_img": img_name,
            "html_body": "<p>Testing the new mobile-first responsive layout with the docked toolbar.</p>"
        }
    )

    print("Test data setup complete.")

if __name__ == "__main__":
    setup_test_data()
