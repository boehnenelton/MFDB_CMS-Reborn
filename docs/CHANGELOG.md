# Changelog - MFDB CMS Reborn

## [1.2.5] - 2026-04-27
### Added
- New "BEJSON" category for standards documentation.
- "Gemini CLI Orchestrator" multi-file showcase page.
- "Gemini Schema Standardization" page with 2026 core templates.
- "Tabulated Json" video showcase with YouTube embedding.
- "BEJSON & MFDB Crash Course" (v13.1) converted to HTML article.
- Automatic Author Profile integration for Elton Boehnen.
- `ensure_category` method in `lib_cms_mfdb.py` to prevent duplicates.
- `batch_fix_images.py` tool for default branding enforcement.

### Changed
- Sidebar now sorts categories alphabetically.
- Empty categories are now automatically hidden from the sidebar.
- Updated all internal libraries and tools to use standardized 2026 Gemini model IDs.
- `MFDB_Builder.py` now correctly passes page titles to the Global Skeleton.
- Set `MFDBCMS.png` as the global default fallback image.

### Fixed
- Resolved duplicate "Apps" category issues.
- Fixed 404 errors in static build by correcting model ID strings to 2026-preview variants.
