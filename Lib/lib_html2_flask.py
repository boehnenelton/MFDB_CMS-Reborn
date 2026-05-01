"""
Library:     lib_html2_flask.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Integration layer between Flask and Core-Command HTML libraries.
"""

import os
from flask import request

# Import our UI components
from lib_bejson_html2_skeletons import CSS_CORE, COLOR
from lib_html2_body import html_stats_bar, html_card, html_card_grid, html_badge
from lib_html2_tables import html_table

def init_dashboard(app, nav_links=None):
    """
    Initializes a Flask app with Core-Command UI standards.
    - Registers Jinja2 globals for all HTML components.
    - Injects the master CSS_CORE into every template.
    - Sets up navigation.
    """
    
    # 1. Global Context Processor (Styles and Nav)
    @app.context_processor
    def inject_ui_context():
        return {
            "css_core": CSS_CORE.format(**COLOR),
            "nav_links": nav_links or []
        }

    # 2. Register UI Components as Jinja Globals
    # This allows calling {{ html_table(doc) | safe }} directly in Jinja templates.
    app.jinja_env.globals.update(
        html_stats_bar=html_stats_bar,
        html_card=html_card,
        html_card_grid=html_card_grid,
        html_badge=html_badge,
        html_table=html_table
    )

    # 3. Path Logic (Ensure templates/flask is discoverable)
    # Most Flask apps will set their template_folder, but we can hint at our base.
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    flask_tpl_path = os.path.join(base_dir, "templates", "flask")
    
    # We don't override the app's template_folder, but we suggest developers 
    # symlink or add this path to their ChoiceLoader if they want base_dashboard.html
    # For now, we assume the system-wide 'templates/' is handled at the project level.

    print(f"Core-Command UI registered for Flask app: {app.name}")

def html_form(bejson_schema, action_url, method="POST", submit_label="SAVE CHANGES"):
    """
    Generates a BEM-compliant form from a BEJSON schema.
    This is a specialized Flask component for data entry.
    """
    import html as html_mod
    
    fields_html = ""
    for field in bejson_schema.get("Fields", []):
        name = field["name"]
        ftype = field["type"]
        
        # Skip discriminators in forms unless needed
        if name == "Record_Type_Parent": continue
        
        label = name.replace("_", " ").upper()
        
        if ftype == "boolean":
            input_html = f'<input type="checkbox" name="{name}" class="c-form__checkbox">'
        elif ftype == "number" or ftype == "integer":
            input_html = f'<input type="number" name="{name}" class="c-form__input" style="width:100%; background:#fff; border:none; padding:8px; margin-top:4px;">'
        else:
            input_html = f'<input type="text" name="{name}" class="c-form__input" style="width:100%; background:#fff; border:none; padding:8px; margin-top:4px;">'
            
        fields_html += f"""
        <div class="c-form__group" style="margin-bottom:16px;">
            <label class="c-form__label" style="font-family:var(--font-mono); font-size:11px; color:var(--primary-red);">{label}</label>
            {input_html}
        </div>"""

    return f"""
    <form action="{action_url}" method="{method}" class="c-form">
        {fields_html}
        <button type="submit" class="top-bar__toggle" style="width:100%; margin-top:16px; height:40px; background:var(--primary-red); color:#fff; border:none;">
            {submit_label}
        </button>
    </form>"""
