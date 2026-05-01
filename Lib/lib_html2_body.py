"""
Library:     lib_html2_body.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL
Author:      Elton Boehnen
Version:     1.4 (OFFICIAL)
Date:        2026-04-29
Description: Content components for Unified Dashboard v4.0.
             Implements Glass Stats, BEM Cards, and Status Badges.
"""
import html as html_mod

def html_stats_bar(stats_list):
    """
    Generate a glass stats bar.
    :param stats_list: List of {"label": "...", "value": "..."}
    """
    if not stats_list: return ""
    items = ""
    for s in stats_list:
        label = html_mod.escape(str(s.get("label", "")))
        value = html_mod.escape(str(s.get("value", "")))
        items += f"""
        <div class="glass-stats__item">
            <span class="glass-stats__label">{label}</span>
            <span class="glass-stats__value">{value}</span>
        </div>"""
    return f'<div class="glass-stats">{items}</div>'

def html_subtabs(tabs):
    """
    Generate horizontal sub-navigation tabs for the dashboard body.
    :param tabs: List of dicts with {"label": "...", "id": "...", "active": bool}
    """
    if not tabs: return ""
    items = ""
    for t in tabs:
        active_class = " subtabs__btn--active" if t.get("active") else ""
        label = html_mod.escape(str(t.get("label", "")))
        tab_id = html_mod.escape(str(t.get("id", "")))
        items += f'<button class="subtabs__btn{active_class}" onclick="switchSubTab(\'{tab_id}\')">{label}</button>\n'
    return f'<div class="subtabs">{items}</div>'

def html_tab_content(tab_id, content, active=False):
    """Wraps content in a tab pane."""
    style = "display: block;" if active else "display: none;"
    return f'<div id="{html_mod.escape(tab_id)}" class="tab-content" style="{style}">{content}</div>'

def html_card(title, body):
    """Generate a dashboard card."""
    return f"""
    <div class="card">
        <h2 class="card__title">{html_mod.escape(title)}</h2>
        <p>{body}</p>
    </div>"""

def html_card_grid(cards_html):
    """Wraps cards in a grid."""
    return f'<div class="card-grid">{cards_html}</div>'

def html_drawer(drawer_id, title, content):
    """Generate a slide-out drawer component."""
    return f"""
    <div id="{drawer_id}" class="drawer">
        <div class="drawer__header">
            <span class="drawer__title">{html_mod.escape(title)}</span>
            <button class="drawer__close" onclick="closeDrawer('{drawer_id}')">&times;</button>
        </div>
        <div class="drawer__content">{content}</div>
    </div>
    <div id="{drawer_id}_overlay" class="drawer-overlay" onclick="closeDrawer('{drawer_id}')"></div>
    <style>
    .drawer {{ position: fixed; top: 0; right: -400px; width: 400px; height: 100%; background: var(--bg-surface); z-index: 3000; transition: right 0.3s ease; border-left: 1px solid var(--border); box-shadow: -5px 0 15px rgba(0,0,0,0.1); }}
    .drawer--open {{ right: 0; }}
    .drawer__header {{ padding: 15px; background: #eee; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }}
    .drawer__title {{ font-family: var(--font-mono); font-weight: bold; font-size: 14px; text-transform: uppercase; color: var(--primary-red); }}
    .drawer__close {{ background: none; border: none; font-size: 24px; cursor: pointer; color: #888; }}
    .drawer__content {{ padding: 20px; height: calc(100% - 50px); overflow-y: auto; }}
    .drawer-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2999; }}
    .drawer-overlay--open {{ display: block; }}
    </style>
    <script>
    function openDrawer(id) {{ 
        document.getElementById(id).classList.add('drawer--open'); 
        document.getElementById(id + '_overlay').classList.add('drawer-overlay--open'); 
    }}
    function closeDrawer(id) {{ 
        document.getElementById(id).classList.remove('drawer--open'); 
        document.getElementById(id + '_overlay').classList.remove('drawer-overlay--open'); 
    }}
    </script>
    """

def html_property_list(props):
    """Generate a vertical key-value list."""
    items = ""
    for p in props:
        key = html_mod.escape(str(p.get("key", "")))
        val = html_mod.escape(str(p.get("value", "")))
        items += f"""
        <div class="prop-list__item">
            <span class="prop-list__key">{key}</span>
            <span class="prop-list__val">{val}</span>
        </div>"""
    return f"""
    <div class="prop-list">{items}</div>
    <style>
    .prop-list {{ border: 1px solid var(--border); background: #fff; }}
    .prop-list__item {{ display: flex; justify-content: space-between; padding: 8px 15px; border-bottom: 1px solid #f0f0f0; font-family: var(--font-mono); font-size: 13px; }}
    .prop-list__item:last-child {{ border-bottom: none; }}
    .prop-list__key {{ color: #777; }}
    .prop-list__val {{ color: #000; font-weight: bold; }}
    </style>
    """

def html_gauge(label, percent, variant=""):
    """Generate a health/progress gauge."""
    color = "var(--primary-red)"
    if variant == "success": color = "#00FF00"
    elif variant == "warning": color = "#FFA500"
    
    return f"""
    <div class="gauge-container">
        <div class="gauge__label">{html_mod.escape(label)} <span class="gauge__value">{percent}%</span></div>
        <div class="gauge__track">
            <div class="gauge__bar" style="width: {percent}%; background: {color};"></div>
        </div>
    </div>
    <style>
    .gauge-container {{ margin: 10px 0; }}
    .gauge__label {{ font-family: var(--font-mono); font-size: 11px; margin-bottom: 5px; color: #555; text-transform: uppercase; }}
    .gauge__value {{ float: right; color: var(--text-main); font-weight: bold; }}
    .gauge__track {{ height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }}
    .gauge__bar {{ height: 100%; transition: width 0.5s ease; }}
    </style>
    """

def html_badge(text, variant=""):
    """
    Generate a status badge.
    Variant can be 'success', 'fail', or empty for neutral.
    """
    style = ""
    if variant == "success": style = "color:#00FF00;"
    elif variant == "fail": style = "color:#FF0000;"
    return f'<span class="badge" style="font-family:var(--font-mono);font-weight:bold;{style}">[{html_mod.escape(text.upper())}]</span>'

def html_action_list(items):
    """
    Generate a list of items with action buttons.
    :param items: List of {"label": "...", "action_label": "...", "onclick": "..."}
    """
    html_items = ""
    for item in items:
        label = html_mod.escape(item.get("label", ""))
        action = html_mod.escape(item.get("action_label", "View"))
        onclick = item.get("onclick", "")
        html_items += f"""
        <div class="action-list__item">
            <span class="action-list__label">{label}</span>
            <button class="form__button form__button--outline" style="padding: 4px 12px; font-size: 10px;" onclick="{onclick}">{action}</button>
        </div>"""
    return f"""
    <div class="action-list">{html_items}</div>
    <style>
    .action-list {{ border: 1px solid var(--border); background: #fff; }}
    .action-list__item {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-bottom: 1px solid #f0f0f0; }}
    .action-list__item:last-child {{ border-bottom: none; }}
    .action-list__label {{ font-family: var(--font-base); font-size: 14px; color: #333; }}
    </style>
    """

def html_description_list(props):
    """
    Generate a technical description list (DL).
    :param props: List of {"term": "...", "description": "..."}
    """
    html_items = ""
    for p in props:
        term = html_mod.escape(p.get("term", ""))
        desc = html_mod.escape(p.get("description", ""))
        html_items += f"<dt class='desc-list__term'>{term}</dt><dd class='desc-list__desc'>{desc}</dd>"
    return f"""
    <dl class="desc-list">{html_items}</dl>
    <style>
    .desc-list {{ display: grid; grid-template-columns: max-content 1fr; gap: 10px 20px; }}
    .desc-list__term {{ font-family: var(--font-mono); font-weight: bold; color: var(--primary-red); text-transform: uppercase; font-size: 11px; }}
    .desc-list__desc {{ font-family: var(--font-base); font-size: 14px; color: #555; margin-left: 0; }}
    </style>
    """

def html_status_panel(title, content, status="ONLINE"):
    """Generate a themed status panel."""
    indicator_color = "#00FF00" if status == "ONLINE" else "#FF0000"
    return f"""
    <div class="status-panel">
        <div class="status-panel__header">
            <span>{html_mod.escape(title)}</span>
            <span class="status-panel__indicator" style="background: {indicator_color};"></span>
            <span class="status-panel__status">{status}</span>
        </div>
        <div class="status-panel__body">{content}</div>
    </div>
    <style>
    .status-panel {{ border: 1px solid var(--border); background: #fff; margin-bottom: 20px; }}
    .status-panel__header {{ 
        padding: 8px 15px; background: #f8f8f8; border-bottom: 1px solid var(--border);
        display: flex; align-items: center; gap: 10px; font-family: var(--font-mono); font-weight: bold; font-size: 12px;
    }}
    .status-panel__indicator {{ width: 8px; height: 8px; border-radius: 50%; }}
    .status-panel__status {{ margin-left: auto; color: {indicator_color}; }}
    .status-panel__body {{ padding: 15px; }}
    </style>
    """
