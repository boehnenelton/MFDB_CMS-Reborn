# BEJSON CMS - System Features (v15.5.0)

A high-performance, dark-themed static site engine built on the MFDB (Multi-File Database) standard.

## 🚀 Core Engine (v1.2 Standard)
*   **Archive Transport**: Site data is managed via standardized `.mfdb.zip` archives with mount-commit safety.
*   **Dual-MFDB Architecture**: Separates site-wide configuration (`db_global`) from page-specific content (`db_content`) for maximum scalability.
*   **Static Site Generator**: High-speed build process that transforms tabular MFDB data into a structured directory-based website.
*   **Automated Sitemap**: Generates a valid `sitemap.xml` on every build using the configured base URL.
*   **Asset Deployment**: Physical asset management system that copies media and standalone apps into the final `www/` build.

## 🛠️ Management Tools
*   **Admin Dashboard (Port 5005)**: Central hub for managing categories, custom navigation links, and authors.
*   **Dynamic Page Editor (Port 5006)**: An adaptive editor that changes its UI based on the page type:
    *   **Article**: Minimalist writing view.
    *   **Video**: Dedicated YouTube embed controls.
    *   **PDF Viewer**: Library-linked document selector.
    *   **Source Code**: Advanced multi-file manager with horizontally scrolling tabs.
*   **Site Manager (Port 5007)**: Global config management, one-click build trigger, and a multi-threaded live preview server (Port 8080).

## 🎨 Content & Design
*   **BEJSON CMS Reborn Theme**: High-contrast, accessibility-first design using Inter/Roboto/Source Code Pro fonts and Tailwind CSS.
*   **Hybrid Feeds**: Categories can render Pages and Standalone Apps together. Includes automated content previews (first 150 chars).
*   **Media Library**: Pro-tier asset management with SHA-256 duplicate detection and alphabetical grouping.
*   **Ad Rotator**: Dynamic ad injection into Header and Sidebar zones with randomized rotation on build.
*   **Author Profiles**: Rich author attribution at the bottom of articles.
*   **Related Content**: Automatic discovery and rendering of "More from this category" at the bottom of pages.

## 📈 SEO & Accessibility
*   **SEO Optimized**: Dynamic meta tags for keywords, descriptions, and OpenGraph/Twitter social sharing.
*   **ARIA Compliant**: Full suite of ARIA roles (`banner`, `navigation`, `main`, `contentinfo`) and accessibility labels for screen readers.
