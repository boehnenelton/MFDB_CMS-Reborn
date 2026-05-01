"""
Library:     lib_html2_page_templates.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL
Author:      Elton Boehnen
Version:     1.4 (OFFICIAL)
Date:        2026-04-29
Description: Full HTML Dashboard templates for BEJSON data.
             Unified Dashboard Architecture v4.2.
             Added: Deep Categorization support & download linking.
"""
import html as html_mod
import os
import json
import re
from datetime import datetime

# Import skeletons
from lib_bejson_html2_skeletons import (
    COLOR, THEMES, CSS_CORE, HTML_SKELETON
)

# ═══════════════════════════════════════════════════════
# 1. CORE PAGE GENERATION
# ═══════════════════════════════════════════════════════

def html_page(title, content, nav_links=None, status_extra="", active_url="", breadcrumbs_html="", sidebar_widgets="", bottom_widgets="", theme=None): 
    """
    Generate a full Core-Command Dashboard page.
    :param theme: Theme name string (from THEMES) or a custom color dict.
    """
    
    # 1. Theme Resolution
    selected_theme = COLOR
    if isinstance(theme, str) and theme in THEMES:
        selected_theme = THEMES[theme]
    elif isinstance(theme, dict):
        selected_theme = theme
        
    # 2. CSS Injection
    css = CSS_CORE.format(**selected_theme)
    
    # 2. Sidebar Tree-view Generation
    nav_html = ""
    if nav_links:
        for cat in nav_links:
            cat_name = cat.get("category", "General")
            nav_html += f'<li class="sidebar__category">{html_mod.escape(cat_name)} <span class="cat-arrow">▶</span></li>\n'
            nav_html += '<ul class="sidebar__category-items">\n'
            for item in cat.get("items", []):
                label = html_mod.escape(item.get("label", "Link"))
                url = item.get("url", "#")
                # Handle relative pathing for active state check
                active_class = " sidebar__link--active" if url == active_url or url.endswith("/" + active_url) else ""
                nav_html += f'  <li><a href="{url}" class="sidebar__link{active_class}">> {label}</a></li>\n'
            nav_html += '</ul>\n'
    else:
        nav_html = '<li class="sidebar__category">Navigation <span class="cat-arrow">▶</span></li>'
        nav_html += '<ul class="sidebar__category-items"><li><a href="#" class="sidebar__link">> No Links</a></li></ul>'

    # 3. Final Assembly
    return HTML_SKELETON.replace("{{title}}", html_mod.escape(title)) \
                       .replace("{{css}}", css) \
                       .replace("{{nav_items}}", nav_html) \
                       .replace("{{content}}", content).replace("{{breadcrumbs}}", breadcrumbs_html) \
                       .replace("{{status_extra}}", html_mod.escape(status_extra)) \
                       .replace("{{sidebar_widgets}}", sidebar_widgets) \
                       .replace("{{bottom_widgets}}", bottom_widgets)

def html_dashboard(title, bejson_doc, nav_links=None):
    """
    Convenience function: Builds a dashboard around a BEJSON Table.
    """
    from lib_html2_tables import html_table
    table_content = html_table(bejson_doc)
    
    # Add a header for the content area
    content = f'<h1 style="margin-bottom:24px;">{html_mod.escape(title)}</h1>'
    content += table_content
    
    return html_page(title, content, nav_links=nav_links, status_extra=f"DATA: {bejson_doc.get('Format_Version', 'UNK')}")

def html_save(content, path):
    """Unified save function for generated HTML."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ═══════════════════════════════════════════════════════
# 2. STATIC WIKI ENGINE
# ═══════════════════════════════════════════════════════

class BEJSONWiki:
    def __init__(self, title="System Wiki", output_dir=None, root_dir=None):
        self.title = title
        self.output_dir = output_dir # Where pages go (e.g. lib/DOCS_WIKI)
        self.root_dir = root_dir     # Where index goes (e.g. lib/)
        self.pages = [] # List of {name, url, category, tags, source_rel_path}

    def _extract_tags(self, first_line):
        if not first_line: return []
        return re.findall(r'#(\w+)', first_line)

    def _simple_md_to_html(self, text):
        lines = text.split('\n')
        html_lines = []
        in_code = False
        for line in lines:
            if line.strip().startswith('```'):
                if not in_code:
                    html_lines.append('<pre class="code-block"><code>')
                    in_code = True
                else:
                    html_lines.append('</code></pre>')
                    in_code = False
                continue
            if in_code:
                html_lines.append(html_mod.escape(line))
                continue
            if line.startswith('### '): html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('## '): html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '): html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('- '): html_lines.append(f'<li>{line[2:]}</li>')
            else:
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                html_lines.append(f'<p>{line}</p>')
        return '\n'.join(html_lines)

    def render_all(self):
        # Build Navigation Tree
        nav_tree = {}
        for p in self.pages:
            cat = p.get('category', 'General')
            if cat not in nav_tree: nav_tree[cat] = []
            
            # Paths relative to the PAGE being rendered (in subfolder)
            # Home is 2 levels up if we use root index, 1 level if we use DOCS_WIKI/index.html
            # Let's target DOCS_WIKI/index.html as the primary index
            nav_tree[cat].append({
                "label": p['name'], 
                "url": f"../{cat}/{p['url']}" if p['url'] != "index.html" else "../index.html"
            })
            
        nav_links = []
        nav_links.append({"category": "Home", "items": [{"label": "Index", "url": "../index.html"}]})
        for cat, items in nav_tree.items():
            nav_links.append({"category": cat, "items": items})
            
        for p in self.pages:
            cat = p.get('category', 'General')
            tag_html = "".join([f'<span class="badge" style="margin-right:5px;">{t}</span>' for t in p['tags']])
            
            # Action Bar for Download/Source
            action_bar = f"""
            <div style="margin: 20px 0; display: flex; gap: 10px;">
                <a href="../../{p['source_rel_path']}" class="form__button" download>DOWNLOAD SOURCE</a>
                <a href="../../{p['source_rel_path']}" class="form__button--outline" target="_blank">VIEW RAW</a>
            </div>
            """
            
            full_content = f'<div style="margin-bottom:20px;">{tag_html}</div>{action_bar}{p["content"]}'
            
            # Generate Breadcrumbs
            bc = f'<a href="../index.html">HUB</a> <span class="breadcrumbs__separator">/</span> '
            bc += f'<a href="index.html">{cat}</a> <span class="breadcrumbs__separator">/</span> '
            bc += f'<span class="breadcrumbs__current">{p["name"]}</span>'
            
            final_html = html_page(
                title=f"{self.title} | {p['name']}",
                content=full_content,
                nav_links=nav_links,
                status_extra=f"WIKI | {cat}",
                active_url=f"../{cat}/{p['url']}",
                breadcrumbs_html=bc
            )
            
            page_path = os.path.join(self.output_dir, cat, p['url'])
            html_save(final_html, page_path)

        self._build_index(nav_tree)

    def _build_index(self, nav_tree):
        # 1. Build PLATFORM (Category) Indices
        for cat, items in nav_tree.items():
            cat_nav = []
            cat_nav.append({"category": "Home", "items": [{"label": "Index", "url": "../index.html"}]})
            for c2, i2 in nav_tree.items():
                cat_nav.append({"category": c2, "items": i2})

            cat_content = f'<div class="page-header"><h1>{cat} Libraries</h1><p>Platform Specific Documentation</p></div>'
            cat_content += '<div class="card-grid"><div class="card" style="grid-column: 1 / -1;">'
            cat_content += '<ul style="list-style:none; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">'
            for item in items:
                link = os.path.basename(item['url'])
                cat_content += f'<li><a href="{link}" class="sidebar__link" style="border:1px solid var(--border)">> {item["label"]}</a></li>'
            cat_content += '</ul></div></div>'

            bc = f'<a href="../index.html">HUB</a> <span class="breadcrumbs__separator">/</span> '
            bc += f'<span class="breadcrumbs__current">{cat}</span>'
            
            final_cat_index = html_page(
                title=f"{self.title} | {cat}",
                content=cat_content,
                nav_links=cat_nav,
                status_extra=f"CATEGORY: {cat}",
                active_url="index.html",
                breadcrumbs_html=bc
            )
            html_save(final_cat_index, os.path.join(self.output_dir, cat, "index.html"))

        # 2. Build MASTER Index (in DOCS_WIKI/index.html)
        index_nav = []
        index_nav.append({"category": "Home", "items": [{"label": "Index", "url": "index.html"}]})
        for cat, items in nav_tree.items():
            cat_items = []
            for item in items:
                cat_items.append({"label": item['label'], "url": f"{cat}/{os.path.basename(item['url'])}"})
            index_nav.append({"category": cat, "items": cat_items})

        content = f'<div class="page-header"><h1>{self.title}</h1><p>System Knowledge Hub & Library Archive</p></div>'
        content += '''
        <div class="glass-stats" style="margin-bottom:30px;">
            <div class="glass-stats__item">
                <span class="glass-stats__label">PACKAGE</span>
                <span class="glass-stats__value">BEJSON_FULL_v1.1.zip</span>
            </div>
            <div style="margin-left:auto; display:flex; align-items:center;">
                <a href="../retain.zip" class="form__button" download>DOWNLOAD ALL LIBRARIES (.ZIP)</a>
            </div>
        </div>
        '''
        
        
        # 3. Add Site Map / Text Link Map
        content += '<div class="card" style="margin-bottom:30px; border-left: 4px solid var(--primary-red);">'
        content += '<h2 style="font-size:14px; text-transform:uppercase; margin-bottom:15px; color:var(--text-muted);">[ SYSTEM MAP ]</h2>'
        content += '<div style="display: flex; flex-wrap: wrap; gap: 20px; font-family: var(--font-mono); font-size: 12px;">'
        
        for cat, items in nav_tree.items():
            content += f'<div style="min-width: 150px;">'
            content += f'<div style="color:var(--primary-red); font-weight:bold; margin-bottom:8px;">{cat}/</div>'
            content += f'<ul style="list-style:none; padding-left:10px; border-left:1px solid var(--border);">'
            content += f'<li><a href="{cat}/index.html" style="color:var(--text-main);">index.html</a></li>'
            for item in items[:3]:
                content += f'<li><a href="{cat}/{os.path.basename(item["url"])}" style="color:var(--text-muted);">{os.path.basename(item["url"])}</a></li>'
            if len(items) > 3:
                content += f'<li><a href="{cat}/index.html" style="color:var(--primary-red); opacity:0.7;">... +{len(items)-3} files</a></li>'
            content += '</ul></div>'
            
        content += '</div></div>'
        
        content += '<div class="card-grid">'

        for cat, items in nav_tree.items():
            content += f'''
            <div class="card">
                <h2 style="color:var(--primary-red); border-bottom:1px solid var(--border); padding-bottom:8px; margin-bottom:15px;">{cat}</h2>
                <ul style="list-style:none;">'''
            # Link to Category Index instead of direct files
            content += f'<li style="margin-bottom:12px; border-bottom:1px solid var(--border); padding-bottom:8px;"><a href="{cat}/index.html" style="font-weight:bold; color:var(--primary-red);">[ VIEW {cat} INDEX ]</a></li>'
            for item in items[:5]: # Show top 5
                link = f"{cat}/{os.path.basename(item['url'])}"
                content += f'<li style="margin-bottom:8px;"><a href="{link}">> {item["label"]}</a></li>'
            if len(items) > 5:
                content += f'<li><a href="{cat}/index.html" style="color:var(--text-muted); font-size:11px;">...and {len(items)-5} more</a></li>'
            content += '</ul></div>'
        content += '</div>'

        bc = '<span class="breadcrumbs__current">HUB</span>'
        final_index = html_page(
            title=self.title,
            content=content,
            nav_links=index_nav,
            status_extra="MASTER INDEX",
            active_url="index.html",
            breadcrumbs_html=bc
        )
        html_save(final_index, os.path.join(self.output_dir, "index.html"))
        
        # Also symlink or copy index to root for convenience if desired, 
        # but the request was "index in its own folders"
        # We will keep it in DOCS_WIKI/index.html as the primary.

