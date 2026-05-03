import os
import sys
import shutil
import json
from pathlib import Path

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB_DIR = os.path.join(PROJECT_ROOT, "Lib")
sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager

def run():
    cms = MFDB_CMS_Manager(os.path.join(PROJECT_ROOT, "Data"))
    
    print("[!] PERFORMING FACTORY RESET...")
    cms.factory_reset()
    
    print("[+] Initializing Fresh System...")
    cms.initialize_system()
    cms.mount_system(force=True)
    
    # 1. Create Category
    print("[+] Creating 'Projects' category...")
    cms.add_category("Projects", "projects", "Detailed technical analysis and system projects.", "blog")
    
    # 1.5 Register Stock Image
    print("[+] Registering stock MFDB image...")
    stock_img_src = os.path.join(PROJECT_ROOT, "MFDBCMS.png")
    stock_img_name = "MFDBCMS.png"
    if os.path.exists(stock_img_src):
        with open(stock_img_src, "rb") as f:
            data = f.read()
            f_hash = cms.get_file_hash(data)
        shutil.copy2(stock_img_src, os.path.join(cms.assets_dir, stock_img_name))
        cms.add_asset(stock_img_name, stock_img_name, f_hash, len(data), "image/png")
    
    # 2. Complete Manual HTML Formatting (All 10 Chapters)
    print("[+] Generating Complete High-Quality HTML Analysis...")
    
    styled_html = """
<div class="auto-format">
    <h1>Critical Analysis: MFDB CMS Reborn</h1>
    
    <div class="meta-box" style="display: flex; justify-content: center; gap: 30px; margin-bottom: 40px; padding: 20px; background: #111; border: 1px dashed #444; border-radius: 8px; font-size: 0.9rem;">
        <div class="meta-item"><b>Date:</b> April 27, 2026</div>
        <div class="meta-item"><b>Version:</b> 1.21 (LATEST)</div>
        <div class="meta-item"><b>Author:</b> boehnenelton2024</div>
    </div>

    <section id="chapter-1">
        <h2>Chapter 1: Executive Summary & System Overview</h2>
        <p>The <b>MFDB CMS Reborn</b> represents a significant evolution in lightweight, schema-integrated systems. Built upon the robust <b>BEJSON (v104, 104a, 104db)</b> standards and the latest <b>MFDB v1.21 protocol</b>, this system offers a unique alternative to traditional database-driven platforms. By prioritizing <b>positional integrity</b> and tabular structures, it achieves high-performance data access without RDBMS overhead.</p>
        <p>At its core, the CMS is a multi-tier application comprising the <b>Portal</b>, <b>Editor</b>, and <b>Site Manager</b>. These are orchestrated via <code>lib_cms_mfdb.py</code>, leveraging the <b>Archive Transport</b> standard (.mfdb.zip), <b>Mount-Commit</b> patterns, and newly enforced <b>Validation Gates</b>.</p>
    </section>

    <section id="chapter-2">
        <h2>Chapter 2: Architectural Deep-Dive: MFDB v1.21</h2>
        <p>Transitioning to <b>v1.21</b> formalizes the "Archive-as-Database" paradigm. The core lifecycle—the Mount-Commit pattern—has been enhanced with <b>Sticky Mounting</b> and <b>Validation Gates</b>.</p>
        <h3>Sticky Mounting</h3>
        <p>Previous iterations required full extraction for every session. v1.21 "Sticky Mount" reuses existing workspace files if the <b>lock hash</b> matches the archive. This significantly reduces file system I/O latency on mobile storage.</p>
        <h3>The Validation Gate</h3>
        <p>The <b>Validation Gate</b> is the zero-defect enforcer. Before any data is committed to the master archive, the system runs exhaustive tests for positional accuracy and relational parity. If checks fail, the system <b>refuses to write</b>, preventing corruption persistence.</p>
    </section>

    <section id="chapter-3">
        <h2>Chapter 3: Data Strategy: Global vs. Content</h2>
        <p>The system maintains a dual-database architecture: <code>global_master.mfdb.zip</code> and <code>content_master.mfdb.zip</code>. This separation ensures administrative persistence while keeping site data ephemeral and portable.</p>
        <ul>
            <li><b>Global Database:</b> Houses SiteConfig, AuthorProfiles, and MediaAsset registries.</li>
            <li><b>Content Database:</b> Focuses on Categories, Pages, and HTML bodies.</li>
        </ul>
        <p>This isolation allows developers to maintain a consistent "System Context" across multiple projects by simply swapping the content archive.</p>
    </section>

    <section id="chapter-4">
        <h2>Chapter 4: The Content Lifecycle</h2>
        <p>The ultimate output is a collection of high-performance static HTML files. Key mechanisms include:</p>
        <h3>Dirty State Tracking</h3>
        <p>A sentinel monitors if workspace files are out of sync with archives. The system <b>refuses to build</b> if in a "Dirty State," ensuring the generated site reflects "Committed Truth."</p>
        <h3>The Build Pipeline</h3>
        <p>Handled by <code>MFDB_Builder.py</code>, the pipeline merges Jinja2 skeletons with BEJSON data. While decoupled for performance, it currently lacks granular error streaming from the build subprocess.</p>
    </section>

    <section id="chapter-5">
        <h2>Chapter 5: Security & Integrity</h2>
        <p>Security is defined as <b>Structural Soundness</b>. In a positional index system, "Bad Data" is the primary threat. v1.21 handles this through a three-tiered validation strategy: BEJSON level, MFDB level, and Application level business logic.</p>
        <p>The <code>.mfdb_lock</code> mechanism provides session safety by tracking the Process ID (PID) and timestamp of the active writer, preventing concurrent archive corruption.</p>
    </section>

    <section id="chapter-6">
        <h2>Chapter 6: UI/UX Evaluation</h2>
        <p>The "Brutalist" design philosophy prioritizes function over form. Recent reorganization of the sidebar into <b>Configuration</b> and <b>Overview</b> sections reduces cognitive load.</p>
        <h3>Statistics Hub</h3>
        <p>The dashboard now provides real-time counts of nodes, policies, and switches, with <b>Service Dots</b> providing instant visual feedback on automation health.</p>
    </section>

    <section id="chapter-7">
        <h2>Chapter 7: Media & Asset Management</h2>
        <p>Uses a <b>Registry-First</b> model where SHA-256 hashes prevent duplicate uploads. Content-addressable storage ensures efficiency, but the library currently lacks <b>Reference Awareness</b>—deleting an asset can break existing page links.</p>
    </section>

    <section id="chapter-8">
        <h2>Chapter 8: Master Dev Agent Protocol</h2>
        <p>The system is "Development-Native." Its transparency allows AI agents to instantly audit state and perform batch updates. <b>CLI Parity</b> ensures that every portal action can be replicated via terminal commands, supporting high-autonomy workflows.</p>
    </section>

    <section id="chapter-9">
        <h2>Chapter 9: Critical Vulnerabilities</h2>
        <ul>
            <li><b>Linear Repack Overhead:</b> Large databases suffer from ZIP compression latency during commit.</li>
            <li><b>Single-Writer Bottleneck:</b> The lock mechanism excludes all other processes, limiting multi-service concurrency.</li>
            <li><b>104db Bloat:</b> Multi-entity BEJSON files suffer from exponential null-padding growth; the MFDB multifile approach is a necessary mitigation.</li>
        </ul>
    </section>

    <section id="chapter-10">
        <h2>Chapter 10: Roadmap & Vision</h2>
        <p>The future of MFDB CMS Reborn is centered on <b>Verify, Validate, and Evolve</b>. Immediate actions focus on eliminating redundancy and hardening relational maps.</p>
        
        <div class="roadmap-item fixed" style="margin-bottom: 15px; padding: 15px; border-left: 4px solid #de2626; background: rgba(222, 38, 38, 0.05); border-radius: 0 8px 8px 0;"><b>[FIXED] Version 1.21 Alignment:</b> All master libraries updated to the latest standard.</div>
        <div class="roadmap-item fixed" style="margin-bottom: 15px; padding: 15px; border-left: 4px solid #de2626; background: rgba(222, 38, 38, 0.05); border-radius: 0 8px 8px 0;"><b>[FIXED] Sticky Mount Protocol:</b> Optimized startup for mobile environments.</div>
        <div class="roadmap-item fixed" style="margin-bottom: 15px; padding: 15px; border-left: 4px solid #de2626; background: rgba(222, 38, 38, 0.05); border-radius: 0 8px 8px 0;"><b>[FIXED] Validation Gate:</b> Refusal to write malformed archives.</div>
        <div class="roadmap-item" style="margin-bottom: 15px; padding: 15px; border-left: 4px solid #444; background: rgba(255,255,255,0.01); border-radius: 0 8px 8px 0;"><b>[PLANNED] Template Extraction:</b> Moving HTML blocks to external Jinja2 files.</div>
        <div class="roadmap-item" style="margin-bottom: 15px; padding: 15px; border-left: 4px solid #444; background: rgba(255,255,255,0.01); border-radius: 0 8px 8px 0;"><b>[PLANNED] Asset Usage Check:</b> Scanning references before allowing asset deletion.</div>
    </section>

    <hr>
    <p style="text-align: center; font-size: 0.8rem; color: #555;"><i>End of Document - Generated by MFDB Automation Engine</i></p>
</div>
"""
    
    # 3. Create Page
    print("[+] Creating CMS Page...")
    analysis_path = "/data/data/com.termux/files/home/lib/docs/cms/Critical_Analysis_MFDB_CMS_v1.21.md"
    content_data = {
        "html_body": styled_html,
        "markdown_body": Path(analysis_path).read_text(),
        "featured_img": stock_img_name
    }
    
    page_uuid = cms.create_page(
        title="Critical Analysis MFDB CMS v1-21",
        category_slug="projects",
        page_type="article",
        content_data=content_data
    )
    
    # 4. Repack and Build
    print("[+] Repacking and Committing to Archives...")
    cms.repack_system()
    
    print("[+] Triggering Static Build...")
    builder_path = os.path.join(LIB_DIR, "tools", "MFDB_Builder.py")
    import subprocess
    subprocess.run([sys.executable, builder_path], cwd=PROJECT_ROOT)
    
    print("[*] SUCCESS: System reset and setup with complete 10-chapter analysis.")

if __name__ == "__main__":
    run()
