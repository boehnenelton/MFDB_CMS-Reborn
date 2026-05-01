"""
Library:     lib_bejson_html2_skeletons.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.2 (OFFICIAL)
Date:        2026-04-24
Description: Authoritative HTML/CSS skeleton templates for Core-Command.
             Implements the Unified Dashboard Architecture (v4.1.0).
             Features: Tree-view Sidebar, Elton Boehnen Credits Footer.
"""

import html as html_mod
import json

# ═══════════════════════════════════════════════════════
# 1. AUTHORITATIVE CSS VARIABLES (Policy v4.0)
# ═══════════════════════════════════════════════════════

COLOR = {
    "primary":    "#DE2626",
    "bg_dark":    "#FFFFFF",
    "bg_surface": "#F4F4F6",
    "text_main":  "#111111",
    "text_muted": "#555555",
    "border":     "#E1E1E1",
    "font_base":  "'Inter', 'Roboto', sans-serif",
    "font_mono":  "'Source Code Pro', monospace",
    "transition": "0.15s",
}

# ═══════════════════════════════════════════════════════
# 2. CORE STYLESHEETS
# ═══════════════════════════════════════════════════════

CSS_CORE = """
:root {{
    --primary-red: {primary};
    --bg-dark: {bg_dark};
    --bg-surface: {bg_surface};
    --text-main: {text_main};
    --text-muted: {text_muted};
    --font-base: {font_base};
    --font-mono: {font_mono};
    --transition-speed: {transition};
}}

/* Reset & Global */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ height: 100%; scroll-behavior: smooth; }}
body {{
    margin: 0;
    padding: 40px 0 50px 0; /* Updated for taller footer */
    background-color: var(--bg-dark);
    color: var(--text-main);
    font-family: var(--font-base);
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
}}

/* Typography */
h1, h2, h3, h4 {{ font-family: var(--font-mono); font-weight: 700; color: var(--text-main); }}
a {{ color: var(--text-main); text-decoration: none; transition: all var(--transition-speed) ease; }}
a:hover {{ color: var(--primary-red); }}

/* SECTION 1.1: TOP BAR */
.top-bar {{
    position: fixed; top: 0; left: 0; width: 100%; height: 40px;
    background-color: var(--bg-surface); border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px; z-index: 1000;
}}
.top-bar__brand {{ font-family: var(--font-mono); font-weight: 700; font-size: 14px; letter-spacing: 1px; }}
.top-bar__brand--accent {{ color: var(--primary-red); }}
.top-bar__toggle {{
    background: transparent; border: 1px solid var(--text-muted);
    color: var(--text-main); font-family: var(--font-mono); font-size: 12px;
    cursor: pointer; padding: 4px 8px; text-transform: uppercase;
    transition: all var(--transition-speed) ease;
}}
.top-bar__toggle:hover {{ border-color: var(--primary-red); color: var(--primary-red); }}

/* SECTION 1.2: SIDEBAR */
.sidebar {{
    position: fixed; top: 40px; left: -240px; width: 240px;
    height: calc(100vh - 40px); background-color: var(--bg-surface);
    border-right: 1px solid var(--border); transition: left var(--transition-speed) ease;
    z-index: 900; overflow-y: auto;
}}
.sidebar--open {{ left: 0; }}
.sidebar__nav {{ list-style: none; padding: 10px 0; }}
.sidebar__category {{
    padding: 8px 16px; font-family: var(--font-mono); font-size: 11px;
    color: var(--primary-red); text-transform: uppercase; font-weight: bold;
    cursor: pointer; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--border);
}}
.sidebar__category:hover {{ background: rgba(222, 38, 38, 0.05); }}
.sidebar__category-items {{ display: none; list-style: none; background: rgba(0,0,0,0.02); }}
.sidebar__category-items--open {{ display: block; }}
.sidebar__link {{
    display: block; padding: 12px 24px; color: var(--text-muted);
    font-family: var(--font-mono); font-size: 12px; border-bottom: 1px solid var(--border);
    transition: all var(--transition-speed) ease;
}}
.sidebar__link:hover {{ background-color: var(--primary-red); color: #fff; font-weight: bold; padding-left: 30px; }}
.sidebar__link--active {{ color: var(--primary-red); border-left: 3px solid var(--primary-red); background: rgba(222, 38, 38, 0.05); }}

/* Sidebar Overlay for Mobile */
.sidebar-overlay {{
    display: none; position: fixed; top: 40px; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.6); z-index: 850;
}}
.sidebar-overlay--open {{ display: block; }}

/* MAIN CONTENT */
.main-content {{ padding: 24px; max-width: 1200px; margin: 0 auto; }}

/* SECTION 2.1: GLASS STATS */
.glass-stats {{
    background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px); border: 1px solid var(--border);
    padding: 16px; margin-bottom: 24px; display: flex; gap: 24px;
    border-left: 4px solid var(--primary-red);
}}
.glass-stats__item {{ display: flex; flex-direction: column; }}
.glass-stats__label {{ font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); text-transform: uppercase; }}
.glass-stats__value {{ font-size: 24px; font-weight: bold; color: var(--primary-red); }}

/* SECTION 2.2: CARDS */
.card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-bottom: 24px; }}
.card {{
    background-color: var(--bg-surface); border: 1px solid var(--border);
    padding: 20px; transition: all var(--transition-speed) ease;
}}
.card:hover {{ transform: translateY(-4px); box-shadow: 4px 4px 0px rgba(222, 38, 38, 0.8); border-color: var(--primary-red); }}
.card__title {{ margin-top: 0; font-size: 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 16px; }}

/* SECTION 2.3: TABLES */
.table-container {{ border: 1px solid var(--border); background-color: var(--bg-surface); margin-bottom: 24px; overflow-x: auto; }}
.data-table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }}
.data-table th, .data-table td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); }}
.data-table th {{
    position: sticky; top: 0; background-color: #f9f9f9; font-family: var(--font-mono);
    font-weight: normal; color: var(--text-muted); z-index: 10; cursor: pointer;
}}
.data-table th:hover {{ color: var(--text-main); }}
.data-table tbody tr:hover {{ background-color: #f9f9f9; }}

/* DOCKED STATUS FOOTER */
.status-footer {{
    position: fixed; bottom: 0; left: 0; width: 100%; height: 50px;
    background-color: var(--bg-surface); border-top: 2px solid var(--primary-red);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px; z-index: 1000;
    font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);
}}
.status-footer__left {{ display: flex; gap: 24px; }}
.status-footer__right {{ font-weight: bold; color: var(--text-main); }}
.status-footer__author {{ color: var(--primary-red); text-decoration: underline; }}
.status-footer__indicator {{
    width: 8px; height: 8px; background-color: var(--primary-red);
    border-radius: 50%; display: inline-block; animation: pulse 2s infinite;
}}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}

/* SECTION 3: RESPONSIVE BREAKPOINTS */
@media (min-width: 768px) {{
    .sidebar {{ left: 0; }}
    .main-content {{ margin-left: 240px; }}
    .top-bar__toggle {{ display: none; }}
}}


/* SECTION 1.3: BREADCRUMBS */
.breadcrumbs {{
    margin-bottom: 16px; font-family: var(--font-mono); font-size: 11px;
    color: var(--text-muted); text-transform: uppercase; display: flex; gap: 8px;
    align-items: center;
}}
.breadcrumbs a {{ color: var(--text-muted); border-bottom: 1px solid transparent; }}
.breadcrumbs a:hover {{ color: var(--primary-red); border-bottom-color: var(--primary-red); }}
.breadcrumbs__separator {{ opacity: 0.5; }}
.breadcrumbs__current {{ color: var(--primary-red); font-weight: bold; }}

/* SECTION 2.4: BUTTONS & INTERACTIVES */
.form__button {{
    background-color: var(--primary-red); color: #fff; border: none;
    padding: 10px 20px; font-family: var(--font-mono); font-size: 12px;
    font-weight: bold; cursor: pointer; text-transform: uppercase;
    transition: all var(--transition-speed) ease; display: inline-block;
    text-align: center;
}}
.form__button:hover {{ background-color: #b01e1e; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
.form__button--outline {{
    background-color: transparent; color: var(--primary-red); border: 2px solid var(--primary-red);
    padding: 8px 18px; font-family: var(--font-mono); font-size: 12px;
    font-weight: bold; cursor: pointer; text-transform: uppercase;
    transition: all var(--transition-speed) ease; display: inline-block;
    text-align: center;
}}
.form__button--outline:hover {{ background-color: var(--primary-red); color: #fff; }}

.badge {{
    display: inline-block; padding: 4px 8px; border-radius: 4px;
    font-size: 10px; font-family: var(--font-mono); font-weight: bold;
    background: #E0E0E0; color: #111; text-transform: uppercase;
}}

.page-header {{ margin-bottom: 30px; border-bottom: 3px solid var(--primary-red); padding-bottom: 15px; }}
.page-header h1 {{ font-size: 32px; margin-bottom: 5px; }}
.page-header p {{ color: var(--text-muted); font-size: 14px; }}
"""

# ═══════════════════════════════════════════════════════
# 3. HTML STRUCTURE
# ═══════════════════════════════════════════════════════

HTML_SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>{{title}}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Source+Code+Pro:wght@400;700&display=swap" rel="stylesheet">
    <style>{{css}}</style>
</head>
<body>
    <header class="top-bar">
        <div class="top-bar__brand">THE <span class="top-bar__brand--accent">BEJSON</span> LIBRARIES</div>
        <button class="top-bar__toggle" aria-label="Toggle Menu">[ MENU ]</button>
    </header>

    <nav class="sidebar">
        <ul class="sidebar__nav">
            {{nav_items}}
        </ul>
    </nav>
    <div class="sidebar-overlay"></div>

    <main class="main-content">
        <nav class="breadcrumbs">{{breadcrumbs}}</nav>
        {{content}}
    </main>

    <footer class="status-footer">
        <div class="status-footer__left">
            <div class="status-footer__item"><span class="status-footer__indicator"></span> SYSTEM: ONLINE</div>
            
            <div class="status-footer__item">{{status_extra}}</div>
        </div>
        <div class="status-footer__right">
            CREDITS: <a href="https://github.com/eltonboehnen" class="status-footer__author">ELTON BOEHNEN</a> | 2026
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const toggle = document.querySelector('.top-bar__toggle');
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            if (toggle && sidebar) {
                toggle.addEventListener('click', () => {
                    const open = sidebar.classList.toggle('sidebar--open');
                    overlay.classList.toggle('sidebar-overlay--open');
                    toggle.textContent = open ? '[ CLOSE ]' : '[ MENU ]';
                });
                overlay.addEventListener('click', () => {
                    sidebar.classList.remove('sidebar--open');
                    overlay.classList.remove('sidebar-overlay--open');
                    toggle.textContent = '[ MENU ]';
                });
            }

            // Tree-view Sidebar Logic
            document.querySelectorAll('.sidebar__category').forEach(cat => {
                cat.addEventListener('click', () => {
                    const items = cat.nextElementSibling;
                    const isOpen = items.classList.toggle('sidebar__category-items--open');
                    cat.querySelector('.cat-arrow').textContent = isOpen ? '▼' : '▶';
                });
            });

            // Auto-expand current category
            const activeLink = document.querySelector('.sidebar__link--active');
            if (activeLink) {
                const parentItems = activeLink.closest('.sidebar__category-items');
                if (parentItems) {
                    parentItems.classList.add('sidebar__category-items--open');
                    const cat = parentItems.previousElementSibling;
                    if (cat) cat.querySelector('.cat-arrow').textContent = '▼';
                }
            }
        });
    </script>
</body>
</html>"""
