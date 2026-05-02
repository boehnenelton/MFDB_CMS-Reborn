# MFDB CMS Reborn

**Status:** Production | **Standard:** MFDB v1.3 (Federation) | **Qualification:** Level 3

---

## 1. 🏗 Architecture Overview

**MFDB CMS Reborn** is the definitive v1.3 Content Management System for the Boehnen Elton JSON (BEJSON) ecosystem. It represents a paradigm shift from traditional monolithic databases to a high-integrity, archive-based persistence model. This "database-as-files" approach provides unparalleled portability, version control, and transactional safety for complex content structures. The system's architecture is founded on a strict separation of concerns, comprising three interdependent pillars: the MFDB Core, the Mount-Commit Pattern, and the Python Orchestration Layer.

### 1.1. The MFDB (Multi-File Database) Core

The foundational principle of the CMS is that all data—content, configuration, and assets—is stored and transported within two primary MFDB archives. These are standardized `.mfdb.zip` files located in the `/Data` directory, each serving a distinct architectural purpose.

*   **`global_master.mfdb.zip`**: This archive is the single source of truth for all sitewide configurations and shared data entities. It is designed to be a central, globally-accessible database for elements that are not tied to a single piece of content. Its responsibilities include:
    *   **Site Configuration:** Core settings like site title, base URL, and metadata.
    *   **Navigation & Links:** The structure of the main site navigation, social media links, and footer content.
    *   **Author Profiles:** A central registry of all content authors, their bios, and associated data.
    *   **Media Assets:** A manifest of all images, video files, and other binary assets used across the site.
    *   **Advertising Units:** Definitions for ad placements and related scripts.

*   **`content_master.mfdb.zip`**: This archive houses the primary intellectual property of the site—the content itself. It manages the lifecycle of every page, article, and media post. Its responsibilities include:
    *   **Core Content Pages:** The main "page" entities, including articles, blog posts, and documentation.
    *   **Content Body:** The actual `pagecontent` (in Markdown or HTML) linked to each page.
    *   **Video & Source Code Metadata:** Specialized entities for video pages and code tutorials.
    *   **Taxonomy:** The categorical framework, defining relationships between different pieces of content.
    *   **Standalone Applications:** Metadata for embedding interactive HTML/JS applications within the CMS structure.

Each archive is a Level 3 Qualified MFDB, containing a `104a.mfdb.bejson` manifest that registers every internal BEJSON file, its purpose, and its primary key.

### 1.2. The Mount-Commit Operational Pattern (Detailed Lifecycle)

All interactions with the MFDB archives are governed by the atomic and non-negotiable **Mount-Commit** pattern. This ensures that the primary data archives are never corrupted and that all changes are transactional.

1.  **Initiation & Lock:** An orchestrator script (`MFDB_Editor.py` or `MFDB_CMS.py`) is executed. The first action is the creation of a `.mfdb_lock` file in the project's root directory. This prevents any other high-level script from initiating a concurrent transaction.

2.  **Mounting (Extraction):** The `lib_mfdb_core.py` module is invoked. It reads the target `.mfdb.zip` archives (e.g., `global_master.mfdb.zip`) and extracts their entire contents into the temporary `/Data/workspace/` directory. This workspace now represents the live, editable state of the database.

3.  **Live Interaction (Edit):** The system is now in a "live" state. All modifications occur *only* on the BEJSON files within the `/Data/workspace/` directory.
    *   The Flask-based `MFDB_Editor.py` provides a GUI for users to perform CRUD operations on these files.
    *   Automated tooling scripts (`/Lib/tools/`) can also be run to programmatically alter data in the workspace.

4.  **Commit (Repacking):** When the user or a system process triggers a "Commit," the `lib_mfdb_core.py` module is again invoked. It performs the following sequence:
    *   It reads the contents of the `/Data/workspace/` directory.
    *   It creates a new, temporary `.mfdb.zip` archive.
    *   It adds all the files from the workspace into this new archive.
    *   Upon successful creation, it atomically replaces the original master archive (e.g., `global_master.mfdb.zip`) with the newly created temporary archive.

5.  **Unmount (Cleanup):** The transaction is complete. The system performs a cleanup by:
    *   Recursively deleting the `/Data/workspace/` directory and all its contents.
    *   Removing the `.mfdb_lock` file.

The system is now back in its "at rest" state, with the master archives containing the newly committed data.

### 1.3. Python Orchestration Layer

High-level Python scripts serve as the designated entry points for all system operations, providing a clear command interface.

*   **`MFDB_CMS.py`**: The primary static site generator. It orchestrates the end-to-end build process, transforming the raw BEJSON data into a complete, browser-ready website.
*   **`MFDB_Editor.py`**: The interactive content management GUI. It provides a user-friendly web interface for non-technical users to manage all aspects of the site's content.
*   **`MFDB_Site_Manager.py`**: A powerful CLI tool for administrators, offering commands for rebuilding the site, checking data integrity, and other high-level management tasks.
*   **`mfdb_launcher.py`**: A master script that provides a simple menu for launching the editor, manager, or builder, ensuring the correct environment is always used.

---

## 2. 🚀 Setup & Deployment (Mobile/Termux First)

The system is engineered for a seamless experience within a Termux environment on Android, enabling a complete development-to-deployment workflow on a mobile device.

### 2.1. Prerequisites

*   **Termux Environment:** A fully updated Termux installation (`pkg upgrade`).
*   **Python 3.10+:** `pkg install python`
*   **Git:** `pkg install git`
*   **Zip/Unzip Utilities:** `pkg install zip unzip`

### 2.2. Installation & Initial Setup

```bash
# Clone the authoritative repository from GitHub into your designated projects folder.
# This ensures you have the latest production-ready version.
git clone https://github.com/boehnenelton/MFDB_CMS-Reborn.git /storage/emulated/0/dev/Projects/MFDB_CMS-Reborn

# Navigate into the newly created project directory.
# All subsequent commands should be run from this root.
cd /storage/emulated/0/dev/Projects/MFDB_CMS-Reborn

# Set the PYTHONPATH environment variable.
# This is a critical step that tells Python where to find the authoritative 2026 standard libraries for BEJSON and MFDB.
export PYTHONPATH="/storage/emulated/0/dev/lib/py:$PYTHONPATH"

# Execute the factory reset and setup script.
# This initializes the database, mounts the master archives into a clean workspace,
# and prepares the CMS for its first use. This command is idempotent and safe to run.
python3 Lib/tools/factory_reset_and_setup.py
```

### 2.3. Troubleshooting Common Setup Issues

*   **`ModuleNotFoundError`**: If you see an error like `No module named 'lib_bejson_core'`, your `PYTHONPATH` is not set correctly. Ensure you have run the `export` command in the same terminal session.
*   **Permission Denied**: If scripts fail to execute, ensure they have the correct permissions. Run `chmod +x *.py` and `chmod +x Lib/tools/*.py`.
*   **Failed Mount**: If a "failed to mount" error occurs, it may be due to a lingering `.mfdb_lock` file from a previously failed transaction. Manually delete this file from the project root and re-run the setup script.

---

## 3. 🛠 Core Components Deep Dive

This section provides an exhaustive breakdown of every key component within the system.

### 3.1. Primary Orchestrators

| Script | Role & Function |
| :--- | :--- |
| **`MFDB_CMS.py`** | The main static site generator. It reads data from the mounted MFDB workspace, processes it through the `lib_html2_*` libraries, and writes the final HTML files to `/Processing/www`. |
| **`MFDB_Editor.py`** | Launches the Flask-based web editor on `localhost:5000`. Provides a GUI for all CRUD operations and includes a "Commit" button to trigger the repacking of the MFDB archives. |
| **`MFDB_Site_Manager.py`** | The administrative command-line interface. Use `--rebuild` to trigger a site build, `--check-orphans` to find unlinked content, and other flags for system maintenance. |
| **`mfdb_launcher.py`** | A user-friendly menu-driven script to launch the other primary orchestrators without needing to remember their specific commands. |

### 3.2. Authoritative Libraries (`/Lib`)

This directory contains the complete, self-contained suite of Python libraries required for all CMS operations.

| Library | Description |
| :--- | :--- |
| **`lib_mfdb_core.py`** | Implements the core Mount-Commit logic. Contains functions for mounting archives, repacking them, and managing lock files. This is the heart of the database's transactional integrity. |
| **`lib_bejson_core.py`** | The foundational Level 1 library for all BEJSON operations. Provides high-performance functions for loading, parsing, and performing matrix manipulations on BEJSON data. |
| **`lib_mfdb_validator.py`** | The official Level 3 validator. It enforces all MFDB rules, including manifest integrity, entity back-linking (bidirectional checks), and schema compliance. |
| **`lib_bejson_validator.py`** | The official Level 1/2 validator for standalone BEJSON files. Ensures all files adhere to their respective 104, 104a, or 104db standards. |
| **`lib_cms_config.py`** | A high-level module for managing and retrieving settings from the `global_master` database, specifically from the `siteconfig.bejson` entity. |
| **`lib_cms_content.py`** | Provides functions for fetching, filtering, and processing content from the `content_master` database, handling relationships between pages, authors, and categories. |
| **`lib_cms_mfdb.py`** | Acts as an abstraction layer, simplifying interactions with `lib_mfdb_core.py` for CMS-specific tasks like fetching the content for a specific page. |
| **`lib_cms_orchestrator.py`**| The logic brain for the `MFDB_CMS.py` site generator. It sequences the entire build process from data loading to HTML rendering. |
| **`lib_cms_taxonomy.py`**| Manages the categorical relationships between content, allowing for the generation of category-specific feed pages. |
| **`lib_html2_body.py`** | A key part of the rendering engine, responsible for constructing the main `<body>` content of each HTML page. |
| **`lib_html2_feed_templates.py`**| Contains logic for rendering lists of content, such as the list of articles on the homepage or a category page. |
| **`lib_html2_page_templates.py`**| Specialized rendering logic for different page types, calling the correct `HTML_Skeleton` based on the content's entity type. |
| **`lib_html2_sidemenu.py`**| Generates the site's side navigation menu based on the data provided by `navlink.bejson`. |
| **`lib_html2_widgets.py`**| Renders smaller, reusable HTML components like author bylines, social media links, or ad units. |
| **`lib_bejson_genai.py`**| An integrated library for communicating with LLM APIs (e.g., Gemini) for potential AI-driven content assistance, using the standard key registries. |

### 3.3. Administrative Tools (`/Lib/tools`)

These scripts provide essential functionality for managing, testing, and maintaining the CMS.

| Tool Script | Example Usage & Description |
| :--- | :--- |
| **`factory_reset_and_setup.py`** | `python3 Lib/tools/factory_reset_and_setup.py`<br>Performs a clean initialization of the system. It removes any existing workspace, re-mounts the master archives, and logs the process. This is the first command you should run after cloning. |
| **`MFDB_Builder.py`** | `python3 Lib/tools/MFDB_Builder.py --build global`<br>A low-level utility for power users. It can build a new `.mfdb.zip` archive directly from a raw source directory (e.g., `db_global`), bypassing the Mount-Commit pattern for initial database creation. |
| **`seed_test_data.py`** | `python3 Lib/tools/seed_test_data.py --count 10`<br>Populates the mounted workspace with a specified number of procedurally generated articles, authors, and categories. Essential for testing the rendering engine without manual data entry. |
| **`cleanup_orphans.py`** | `python3 Lib/tools/cleanup_orphans.py --dry-run`<br>Scans the `pagecontent` and other entities for records that are no longer linked to a parent `page`. The `--dry-run` flag lists orphans without deleting them; remove the flag to perform the cleanup. |
| **`import_unified_editor.py`**| `python3 Lib/tools/import_unified_editor.py --source /path/to/old/data.bejson`<br>A migration tool for importing content from older, non-MFDB BEJSON formats into the modern MFDB structure. |

### 3.4. HTML Skeletons (`/HTML_Skeletons`)

These files are the foundational HTML structures for the entire generated site.

| Skeleton File | Purpose |
| :--- | :--- |
| **`Global_Skeleton.html`** | The master template. Contains the `<html>`, `<head>`, and `<body>` tags, global CSS/JS, and placeholders for the header, footer, and main content block. |
| **`Home_Skeleton.html`** | The template for the site's homepage. Designed to display multiple content feeds generated by `lib_html2_feed_templates.py`. |
| **`Article_Skeleton.html`**| The standard template for a text-based article. Includes placeholders for title, author bio, body content, and metadata. |
| **`Video_Skeleton.html`** | A template specifically for video posts, featuring a large embedded video player area and a section for the video transcript or description. |
| **`SourceCode_Skeleton.html`** | A template designed for technical tutorials, with syntax highlighting and a clear layout for code blocks and their explanations. |

---

## 4. Data Model Deep Dive

The CMS utilizes two distinct but interconnected data models, stored in `db_global` and `db_content`.

### 4.1. Global Data Model (`db_global`)

This model defines entities that are shared across the entire site.

#### **`siteconfig.bejson`** (104)
| Field | Type | Description |
| :--- | :--- | :--- |
| `site_title` | string | The main title of the website, used in `<title>` tags and headers. |
| `base_url` | string | The canonical base URL of the site (e.g., `https://example.com`). |
| `site_description`| string | The default meta description for search engines. |
| `theme_color` | string | A hex color code for the browser theme. |

#### **`navlink.bejson`** (104a)
| Field | Type | Description |
| :--- | :--- | :--- |
| `nav_id` | integer | The primary key for the navigation link. |
| `label` | string | The visible text of the link (e.g., "Home", "About Us"). |
| `url` | string | The destination URL for the link. |
| `display_order` | integer | The order in which the link appears in the navigation menu. |
| `is_active` | boolean | Whether the link is currently enabled. |

#### **`authorprofile.bejson`** (104a)
| Field | Type | Description |
| :--- | :--- | :--- |
| `author_id` | integer | The primary key for the author. |
| `full_name` | string | The author's full name. |
| `bio` | string | A short biography for the author page. |
| `avatar_url` | string | A URL to the author's profile picture. |

### 4.2. Content Data Model (`db_content`)

This model defines the core content entities.

#### **`page.bejson`** (104a)
| Field | Type | Description |
| :--- | :--- | :--- |
| `page_id` | integer | The primary key for the page. |
| `title` | string | The main title of the article or page. |
| `slug` | string | The URL-friendly version of the title. |
| `author_fk` | integer | A foreign key linking to `authorprofile.author_id`. |
| `category_fk` | integer | A foreign key linking to `category.category_id`. |
| `status` | string | The publication status ("draft", "published", "archived"). |
| `featured_img` | string | Path to the main image for the article. |
| `creation_ts`| integer | A Unix timestamp of when the page was created. |
| `modified_ts`| integer | A Unix timestamp of the last modification. |

#### **`pagecontent.bejson`** (104)
| Field | Type | Description |
| :--- | :--- | :--- |
| `page_fk` | integer | A foreign key linking to `page.page_id`. This is a one-to-one relationship. |
| `body_md` | string | The full body of the content in Markdown format. |
| `body_html` | string | (Optional) Pre-rendered HTML content if Markdown is not used. |

#### **`category.bejson`** (104a)
| Field | Type | Description |
| :--- | :--- | :--- |
| `category_id` | integer | The primary key for the category. |
| `name` | string | The name of the category (e.g., "Software Engineering"). |
| `slug` | string | The URL-friendly version of the name. |

---

## 5. Validation and Integrity

The system's reliability is guaranteed by a multi-layered validation protocol, enforced by the `lib_*_validator.py` libraries.

### 5.1. BEJSON Validation (Level 1 & 2)

`lib_bejson_validator.py` checks all standalone `.bejson` files.

*   **`E_RECORD_LENGTH_MISMATCH`**: This critical error occurs if a row in the `Values` array does not have the same number of elements as defined in the `Fields` array. It indicates a violation of **Positional Integrity**.
*   **`E_MISSING_MANDATORY_KEY`**: A file is invalid if it is missing a required header key like `Format` or `Format_Creator`.
*   **`E_INVALID_VERSION`**: The `Format_Version` must be one of the recognized standards ("104", "104a", "104db").
*   **`E_TYPE_MISMATCH`**: Occurs if a value's data type does not match the type defined in its corresponding `Fields` entry (e.g., a string where an integer is expected).
*   **`E_INVALID_FORMAT`**: The `Format` must always be "BEJSON".

### 5.2. MFDB Validation (Level 3)

`lib_mfdb_validator.py` performs higher-level checks on the entire database structure.

*   **`E_MFDB_NOT_MANIFEST`**: The root `104a.mfdb.bejson` file must have its `Records_Type` set to `["mfdb"]`.
*   **`E_MFDB_ENTITY_NOT_FOUND`**: An entity file listed in the manifest does not exist on disk at its resolved path.
*   **`E_MFDB_NO_PARENT_HIERARCHY`**: An entity file (e.g., `page.bejson`) is missing the required `Parent_Hierarchy` key that links it back to its manifest.
*   **`E_MFDB_BIDIRECTIONAL_FAIL`**: A catastrophic integrity failure where the path to an entity in the manifest does not match the back-link from the entity to the manifest. This indicates a corrupted database structure.
*   **`E_MFDB_INVALID_ARCHIVE`**: The `.mfdb.zip` file itself is corrupted or does not contain a manifest at its root.

---

## 6. 🔒 Security & Policy Mandates

This project operates under the strict 2026 BEJSON/MFDB security and policy standards.

*   **Handling Certification:** All modifications to the core libraries or data models require a minimum of **Level 3 (MFDB) Handling Certification**. Unqualified modifications are strictly prohibited and will be reverted.
*   **Data Integrity:** The Mount-Commit pattern is mandatory for all database interactions. Direct modification of the `.mfdb.zip` archives is forbidden.
*   **API Key Isolation:** This project does not directly handle API keys. However, any integrated components (like the `lib_bejson_genai.py` library) must use the standard `~/.env/` key registries.
*   **No Hallucination:** All documentation and system status reporting must be based on the actual, validated state of the codebase and databases.

---

## 7. 📜 License

**Proprietary** – All rights reserved. Developed by Elton Boehnen for the BEJSON ecosystem. Unauthorized redistribution or modification is prohibited without explicit permission.
