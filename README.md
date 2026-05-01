# MFDB CMS Reborn
**Version 1.2.5**

MFDB CMS Reborn is a high-speed, lightweight, and standards-compliant Content Management System built on the **BEJSON (v104, 104a, 104db)** tabular data format. It uses positional integrity to ensure high-performance data access and seamless integration with AI-driven workflows.

## 🚀 Key Features
- **BEJSON Native:** Built on a strict tabular JSON standard for rapid parsing and LLM compatibility.
- **Multifile Database (MFDB):** Orchestrates manifests and entity files for a structured, modular database.
- **AI-Ready:** Standardized integration with Google Gemini 2026 models.
- **Multi-File Showcases:** Dedicated templates for presenting codebases and technical documentation.
- **Static Site Generation:** Rapidly builds SEO-optimized, dark-themed websites.
- **Atomic Mount-Commit:** Virtual mounting system to prevent database corruption.

## 📁 Project Structure
- `Data/`: Core MFDB archives and assets.
- `Lib/`: Backend logic and BEJSON/MFDB core libraries.
- `HTML_Skeletons/`: Jinja2-style templates for static generation.
- `Processing/www/`: The final published static website.
- `docs/`: Technical documentation and changelogs.

## 🛠 Management Tools
- **MFDB_CMS.py**: Main management dashboard.
- **MFDB_Editor.py**: Direct BEJSON data manipulation.
- **MFDB_Site_Manager.py**: Configuration and local preview server.
- **Lib/tools/MFDB_Builder.py**: The static site generator.

## 🔗 Path Integrity & Asset Management
During the April 2026 update, several path discrepancies were identified and resolved to ensure system portability:

1.  **"None" String Defensive Handling:**
    - **Issue:** Some BEJSON `featured_img` fields contained the string `"None"`, causing broken links like `../../assets/None`.
    - **Fix:** The builder now enforces a strict check: if a field is empty, a Python `None` object, or the literal string `"None"`, it defaults to `default-feature.png`.

2.  **Relative Prefixing (`rel_prefix`):**
    - To maintain portability without hard-coded domains, the system uses tiered relative paths:
        - **Homepage:** `assets/`
        - **Category Index:** `../assets/`
        - **Content Page:** `../../assets/`
    - All image tags and CSS links in skeletons now utilize the `{{ rel_prefix }}` variable.

3.  **Required Assets:**
    - The system now requires `assets/logo.png` and `assets/default-feature.png` to be present in the source `Data/assets` folder.

---
*Powered by BEJSON - The Strict Tabular JSON Standard.*
