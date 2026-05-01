import os
import sys
import json
from pathlib import Path

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB_DIR = os.path.join(PROJECT_ROOT, "Lib")
sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager

def convert_markdown_to_html(md_path):
    import re
    content = Path(md_path).read_text()
    
    # Simple conversion for standard markdown elements
    # Headers
    content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', content, flags=re.M)
    content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', content, flags=re.M)
    content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', content, flags=re.M)
    
    # Bold
    content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
    
    # Lists
    content = re.sub(r'^- (.*)$', r'<li>\1</li>', content, flags=re.M)
    # Wrap li in ul (simple logic)
    content = content.replace('<li>', '<ul><li>', 1).replace('</li>\n\n', '</li></ul>\n\n')
    
    # Links
    content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', content)
    
    # Paragraphs (crude)
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip() and not line.startswith('<'):
            new_lines.append(f'<p>{line}</p>')
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def run():
    cms = MFDB_CMS_Manager(os.path.join(PROJECT_ROOT, "Data"))
    
    print("[+] Mounting System...")
    cms.mount_system(force=True)
    
    # 1. Create Category
    print("[+] Creating 'Projects' category...")
    cms.add_category("Projects", "projects", "Detailed technical analysis and system projects.", "blog")
    
    # 2. Convert Document
    doc_path = "/storage/emulated/0/dev/docs/cms/Critical_Analysis_MFDB_CMS_v1.21.md"
    print(f"[+] Converting {doc_path} to HTML...")
    html_body = convert_markdown_to_html(doc_path)
    
    # 3. Create Page
    print("[+] Creating CMS Page...")
    content_data = {
        "html_body": html_body,
        "markdown_body": Path(doc_path).read_text(),
        "featured_img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=800"
    }
    
    page_uuid = cms.create_page(
        title="Critical Analysis MFDB CMS v1-21",
        category_slug="projects",
        page_type="article",
        content_data=content_data
    )
    
    print(f"[!] Page Created! UUID: {page_uuid}")
    
    # 4. Repack
    print("[+] Repacking and Committing to Archives...")
    cms.repack_system()
    
    print("[*] SUCCESS: Category and Page added to MFDB v1.21 archives.")

if __name__ == "__main__":
    run()
