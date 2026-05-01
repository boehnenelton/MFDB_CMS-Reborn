# MFDB CMS Reborn

**Status:** Production | **Standard:** MFDB v1.3 (Federation)

---

## 1. 🏗 Architecture Overview

**MFDB CMS Reborn** is the flagship v1.3 Content Management System for the Boehnen Elton JSON (BEJSON) ecosystem. It is a high-performance, archive-based system designed for managing complex, interrelated content structures with absolute data integrity. Unlike traditional databases, it operates on a "database-as-files" principle, packaging entire content stores into portable `.mfdb.zip` archives.

The architecture is built on three pillars, ensuring a strict separation of concerns between data persistence, user interaction, and site generation.

### 1.1. The MFDB (Multi-File Database) Core

The entire system state is persisted within two primary MFDB archives located in the `/Data` directory:

*   **`global_master.mfdb.zip`**: Contains all site-wide configurations and shared assets. This includes navigation links, author profiles, social media links, advertising units, and global site settings. It acts as the central hub for data that applies across the entire generated website.

*   **`content_master.mfdb.zip`**: Houses the primary content entities. This includes all pages, articles, video metadata, source code examples, and the categorical relationships that bind them together.

Each archive is a self-contained database, adhering to the Level 3 MFDB standard. It contains a `104a.mfdb.bejson` manifest at its root, which registers every BEJSON entity file within the archive. This structure allows for unparalleled portability and atomic updates.

### 1.2. The Mount-Commit Operational Pattern

The CMS operates exclusively on a **Mount-Commit** pattern, the cornerstone of the MFDB v1.3 standard. This ensures data integrity and prevents race conditions.

1.  **Mount:** When an operation begins (e.g., starting the editor or rebuilding the site), the Python orchestrator (`MFDB_CMS.py` or `MFDB_Editor.py`) mounts the `.mfdb.zip` archives. It extracts their contents into a temporary, transactional `/Data/workspace/` directory and creates a `.mfdb_lock` file to prevent concurrent modifications.

2.  **Edit:** The user or an automated tool interacts with the extracted BEJSON files within the workspace. For instance, the `MFDB_Editor.py` Flask application provides a web interface to modify records in these files directly.

3.  **Commit:** Once modifications are complete, the controlling script triggers a "commit." It repacks the contents of the `/Data/workspace/` directory back into the corresponding `.mfdb.zip` archive, overwriting the old version. This is an atomic operation.

4.  **Unmount:** The temporary workspace directory is purged, and the `.mfdb_lock` file is removed, completing the transaction.

This pattern guarantees that the primary database archives are only ever touched by a complete, validated transaction.

### 1.3. Python Orchestration Layer

A suite of high-level Python scripts orchestrates all CMS operations. They act as the entry points for all user and system actions.

*   **`MFDB_CMS.py`**: The primary build engine. This script reads the mounted MFDB archives, processes the content relationships, and uses the `HTML_Skeletons` to generate the final static HTML website in the `/Processing/www` directory.

*   **`MFDB_Editor.py`**: The interactive content editor. It launches a Flask-based web application, providing a GUI for CRUD (Create, Read, Update, Delete) operations on the BEJSON entities.

*   **`MFDB_Site_Manager.py`**: A powerful administrative tool for performing high-level site management tasks, such as triggering a full site rebuild, managing configurations, or performing content integrity checks.

*   **`mfdb_launcher.py`**: A convenience script for launching the various CMS components with the correct environment settings.

---

## 2. 🚀 Setup & Deployment (Mobile/Termux First)

This system is optimized for a Termux environment on Android, providing a full-featured development and deployment platform on mobile.

### 2.1. Prerequisites

*   **Termux Environment:** A working Termux installation on Android.
*   **Python 3.10+:** Ensure Python is installed (`pkg install python`).
*   **Git:** For cloning the repository (`pkg install git`).
*   **Unzip:** For managing MFDB archives (`pkg install unzip`).

### 2.2. Installation & Initial Setup

```bash
# Clone the repository from GitHub into your dev folder
git clone https://github.com/boehnenelton/MFDB_CMS-Reborn.git /storage/emulated/0/dev/Projects/MFDB_CMS-Reborn

# Navigate to the project directory
cd /storage/emulated/0/dev/Projects/MFDB_CMS-Reborn

# Ensure the authoritative BEJSON/MFDB libraries are accessible.
# The 2026 standard path is /dev/lib/py.
export PYTHONPATH="/storage/emulated/0/dev/lib/py:$PYTHONPATH"

# Run the factory reset script to initialize the database workspaces.
# This is a critical first step. It mounts the master archives
# and creates a clean, functional workspace in /Data/workspace/.
python3 Lib/tools/factory_reset_and_setup.py
```

### 2.3. Running the Core Components

#### 2.3.1. Launching the Content Editor

The editor provides a web-based GUI to manage all content.

```bash
# From the project root directory
python3 MFDB_Editor.py
```

*   Open your mobile browser and navigate to **`http://localhost:5000`**.
*   You will be presented with an interface to select an entity (e.g., "page", "article") and perform CRUD operations.
*   All changes are saved directly to the mounted workspace. A "Commit" button in the UI repacks the database.

#### 2.3.2. Building the Static Site

To generate the HTML website from the current database state:

```bash
# From the project root directory
python3 MFDB_CMS.py
```

*   The script will mount the archives, read all entities, and generate the site into `/Processing/www`.
*   You can then serve this directory with a simple Python web server for preview:
    `cd Processing/www && python3 -m http.server 8000`

#### 2.3.3. Using the Site Manager

For administrative tasks:

```bash
# From the project root directory
python3 MFDB_Site_Manager.py --help

# Example: Trigger a full site rebuild
python3 MFDB_Site_Manager.py --rebuild

# Example: Check for orphan content
python3 MFDB_Site_Manager.py --check-orphans
```

---

## 3. 🛠 Core Components Deep Dive

This section details the key files and directories that constitute the CMS.

### 3.1. Data Directory (`/Data`)

This is the heart of the CMS, containing all persistent data.

| Sub-Directory / File | Description | Standard |
| :--- | :--- | :--- |
| **`global_master.mfdb.zip`** | Level 3 Archive. Contains sitewide configs, navigation, authors, etc. | MFDB v1.3 |
| **`content_master.mfdb.zip`**| Level 3 Archive. Contains pages, articles, videos, and their taxonomies. | MFDB v1.3 |
| **`/db_global/`** | The raw, un-archived source for the global master database. | BEJSON 104 |
| **`/db_content/`** | The raw, un-archived source for the content master database. | BEJSON 104 |
| **`/workspace/`** | The transactional directory where archives are mounted for editing. **This directory is volatile.** | Mixed |

#### **Global Data Model (`db_global`)**
*   `siteconfig.bejson`: Site title, URL, description.
*   `navlink.bejson`: Main navigation menu items (label, URL, order).
*   `authorprofile.bejson`: Author names, bios, and links.
*   `mediaasset.bejson`: Central registry for images, videos, etc.
*   `sociallink.bejson`: Social media profile links.
*   `adunit.bejson`: Advertising placement configurations.

#### **Content Data Model (`db_content`)**
*   `page.bejson`: The core content object. Includes title, author_fk, featured_img, timestamps, and status.
*   `pagecontent.bejson`: The actual body content for a page, linked via `page_fk`. Supports Markdown and raw HTML.
*   `category.bejson`: Defines the content taxonomy (e.g., "AI", "Software", "Hardware").
*   `standaloneapp.bejson`: Metadata for embedding standalone HTML/JS applications.

### 3.2. Standard Library (`/Lib`)

A comprehensive, self-contained library of Python modules providing all necessary functionality. This follows the 2026 mandate of portable, encapsulated logic.

| Library File | Description |
| :--- | :--- |
| **`lib_mfdb_core.py`** | The authoritative implementation of the **Mount-Commit** pattern. Handles all archive operations. |
| **`lib_bejson_core.py`** | Foundational library for parsing, manipulating, and writing BEJSON matrices. |
| **`lib_mfdb_validator.py`**| The official Level 3 validator. Enforces manifest integrity, bidirectional pathing, and schema compliance. |
| **`lib_bejson_validator.py`**| The official Level 1/2 validator for standalone BEJSON files. |
| **`lib_cms_*.py`** | A suite of specialized modules for CMS logic: `_config`, `_content`, `_mfdb`, `_orchestrator`, `_taxonomy`. |
| **`lib_html2_*.py`** | A powerful HTML generation library. Takes BEJSON data and renders it into static pages using the `HTML_Skeletons`. |

### 3.3. Administrative Tools (`/Lib/tools`)

A collection of powerful command-line utilities for developers and administrators.

| Tool Script | Description |
| :--- | :--- |
| **`factory_reset_and_setup.py`** | **(CRITICAL)** Wipes the workspace and performs a fresh mount of the master archives. Essential for initial setup. |
| **`MFDB_Builder.py`** | A low-level tool to manually build or rebuild MFDB archives from raw `db_*` directories. |
| **`seed_test_data.py`** | Populates the database with well-structured dummy content for testing purposes. |
| **`cleanup_orphans.py`** | Scans the database for content that is no longer linked to a parent entity and flags it for deletion. |
| **`import_unified_editor.py`** | Script to import content from the legacy BEJSON Unified Editor format. |

### 3.4. HTML Skeletons (`/HTML_Skeletons`)

These are the master HTML templates used by the `lib_html2_*` libraries to generate the final website. They contain special placeholder tags (e.g., `{{BODY_CONTENT}}`, `{{SIDE_MENU}}`) that the generation engine replaces with dynamic content from the database.

*   `Global_Skeleton.html`: Defines the main `<html>`, `<head>`, and `<body>` structure, including global CSS and JS links.
*   `Home_Skeleton.html`: Template for the homepage, typically containing multiple content feeds.
*   `Article_Skeleton.html`: Template for a standard text-based article page.
*   `Video_Skeleton.html`: Template for a page featuring an embedded video.
*   `SourceCode_Skeleton.html`: Template optimized for displaying and explaining source code.

---

## 4. 🔒 Security & Policy Mandates

This project operates under the strict 2026 BEJSON/MFDB security and policy standards.

*   **Handling Certification:** All modifications to the core libraries or data models require a minimum of **Level 3 (MFDB) Handling Certification**. Unqualified modifications are strictly prohibited and will be reverted.
*   **Data Integrity:** The Mount-Commit pattern is mandatory for all database interactions. Direct modification of the `.mfdb.zip` archives is forbidden.
*   **API Key Isolation:** This project does not directly handle API keys. However, any integrated components (like the `lib_bejson_genai.py` library) must use the standard `~/.env/` key registries.
*   **No Hallucination:** All documentation and system status reporting must be based on the actual, validated state of the codebase and databases.

---

## 5. 📜 License

**Proprietary** – All rights reserved. Developed by Elton Boehnen for the BEJSON ecosystem. Unauthorized redistribution or modification is prohibited without explicit permission.
