"""
Project: MFDB CMS Reborn
Project Version: v1.3
MFDB Version: v1.3
"""
import os
import sys
import uuid
import collections
import threading
import http.server
import socketserver
from datetime import datetime
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename

# Add Lib to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "Lib")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore
import lib_mfdb_extensions as MFDBExt

# --- Flask App Initialization ---
app = Flask(__name__)
app.secret_key = 'mfdb-reborn-secret'

@app.context_processor
def inject_globals():
    return {
        "network_role": cms.network_role,
        "is_dirty": cms.is_dirty
    }

# Portable SVG placeholder for missing images
_IMG_ONERROR = "this.src='data:image/svg+xml;charset=utf-8,%3Csvg xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22 width%3D%22200%22 height%3D%22200%22 viewBox%3D%220 0 200 200%22%3E%3Crect width%3D%22100%25%22 height%3D%22100%25%22 fill%3D%22%23171717%22%2F%3E%3Ctext x%3D%2250%25%22 y%3D%2250%25%22 dominant-baseline%3D%22middle%22 text-anchor%3D%22middle%22 font-family%3D%22monospace%22 font-size%3D%2214%22 fill%3D%22%23444%22%3EMISSING ASSET%3C%2Ftext%3E%3C%2Fsvg%3E'"

DATA_ROOT = os.path.join(BASE_DIR, "Data")
WWW_ROOT = os.path.join(BASE_DIR, "Processing", "www")
# Multi-Site Multi-Tenant Patch
SITES_REGISTRY = os.path.join(BASE_DIR, "sites_registry.bejson")
def get_active_site():
    try:
        reg = BEJSONCore.bejson_core_load_file(SITES_REGISTRY)
        idx_path = BEJSONCore.bejson_core_get_field_index(reg, "data_path")
        idx_active = BEJSONCore.bejson_core_get_field_index(reg, "is_active")
        for row in reg["Values"]:
            if row[idx_active]: return os.path.join(BASE_DIR, row[idx_path])
    except: pass
    return DATA_ROOT

ACTIVE_SITE_DATA = get_active_site()
cms = MFDB_CMS_Manager(ACTIVE_SITE_DATA)

# Global for preview server
_preview_srv = {
    "thread": None,
    "httpd": None,
    "port": 8080,
    "running": False
}

# Initialize and Mount on start
with app.app_context():
    try:
        cms.mount_system(force=True)
    except MFDBCore.MFDBValidationError as e:
        # Smart Repair Gate (v1.21)
        print(f"[REPAIR] Validation error detected on mount: {e}")
        # Attempt repair on both manifests if they exist
        repaired = False
        if os.path.exists(cms.global_manifest):
            repaired |= MFDBCore.mfdb_core_smart_repair(cms.global_manifest, e)
        if os.path.exists(cms.content_manifest):
            repaired |= MFDBCore.mfdb_core_smart_repair(cms.content_manifest, e)
        
        if repaired:
            print("[REPAIR] Smart Repair successful. Retrying mount...")
            cms.mount_system(force=True)
        else:
            print("[REPAIR] Smart Repair failed to resolve issue.")
            raise e

# =============================================================================
# DB ORCHESTRATION ROUTES (v1.2)
# =============================================================================

@app.route('/db/status')
def db_status():
    return jsonify({
        "dirty": cms.is_dirty,
        "global_archive": os.path.basename(cms.global_archive),
        "content_archive": os.path.basename(cms.content_archive),
        "workspace": cms.workspace_root
    })

@app.route('/db/repack', methods=['POST'])
def db_repack():
    try:
        cms.repack_system()
        flash("Database repacked and committed to transport archives.")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/db/export/<db_type>')
def db_export(db_type):
    if db_type == 'global':
        return send_file(cms.global_archive, as_attachment=True)
    elif db_type == 'content':
        return send_file(cms.content_archive, as_attachment=True)
    return "Invalid DB type", 400

@app.route('/db/health')
def db_health():
    orphans = MFDBExt.mfdb_ext_verify_referential_integrity(cms.content_manifest)
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Database Health Audit</h1>
        <a href="/" class="text-xs font-bold text-gray-500 hover:text-white uppercase">Back to Dashboard</a>
    {% endblock %}
    {% block content %}
    <div class="max-w-4xl mx-auto space-y-6">
        <div class="bg-[#171717] p-8 rounded-xl border border-gray-800">
            <h2 class="text-lg font-bold text-red-500 mb-6 uppercase tracking-widest">Integrity Report (Foreign Keys)</h2>
            {% if not orphans %}
            <div class="flex items-center gap-4 text-green-500 bg-green-900/10 p-6 rounded-lg border border-green-900/30">
                <i data-lucide="shield-check" class="w-8 h-8"></i>
                <div>
                    <p class="font-bold">Database Healthy</p>
                    <p class="text-xs opacity-70">No orphaned records or broken references detected in the content database.</p>
                </div>
            </div>
            {% else %}
            <div class="space-y-4">
                {% for entity, fields in orphans.items() %}
                <div class="border border-red-900/30 bg-red-950/5 rounded-lg overflow-hidden">
                    <div class="bg-red-950/20 px-4 py-2 font-bold text-xs uppercase text-red-400 border-b border-red-900/30">Entity: {{ entity }}</div>
                    <div class="p-4 space-y-3">
                        {% for field, values in fields.items() %}
                        <div>
                            <p class="text-[10px] font-bold text-gray-500 uppercase mb-1">{{ field }} (Orphaned Values)</p>
                            <div class="flex flex-wrap gap-2">
                                {% for val in values %}
                                <span class="bg-black px-2 py-1 rounded font-mono text-[10px] border border-gray-800 text-red-500">{{ val }}</span>
                                {% endfor %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        
        <div class="bg-[#171717] p-8 rounded-xl border border-gray-800">
             <h2 class="text-lg font-bold text-gray-500 mb-4 uppercase tracking-widest">Diagnostic Tools</h2>
             <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button class="bg-gray-800 p-4 rounded-lg text-left hover:bg-gray-700 transition-all group">
                    <p class="font-bold text-sm mb-1 group-hover:text-red-500">Recalculate Indices</p>
                    <p class="text-[10px] text-gray-500">Force a full re-index of all primary key fields.</p>
                </button>
                <button class="bg-gray-800 p-4 rounded-lg text-left hover:bg-gray-700 transition-all group">
                    <p class="font-bold text-sm mb-1 group-hover:text-red-500">Prune Temp Data</p>
                    <p class="text-[10px] text-gray-500">Clean up orphaned session locks and temp files.</p>
                </button>
             </div>
        </div>
    </div>
    {% endblock %}'''
    return render_template_string(html, orphans=orphans)

@app.route('/network', methods=['GET', 'POST'])
def network():
    # Attempt to load connected nodes from global database
    # Requirement: Federation Module uses 'connected_slaves.bejson'
    try:
        nodes = MFDBCore.mfdb_core_load_entity(cms.global_manifest, "ConnectedSlave")
    except:
        nodes = []

    if request.method == 'POST':
        label = request.form.get('label')
        url = request.form.get('url')
        # Simple registration for now
        try:
            MFDBCore.mfdb_core_add_entity_record(cms.global_manifest, "ConnectedSlave", [label, url, "Slave", "Active", []])
            flash(f"Node '{label}' added to the federation.")
        except Exception as e:
            flash(f"Failed to add node: {e}", "error")
        return redirect(url_for('network'))

    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Network Federation</h1>
        <button onclick="document.getElementById('add-node-modal').classList.remove('hidden')" class="bg-red-600 px-4 py-2 rounded font-bold text-sm">+ Register Node</button>
    {% endblock %}
    {% block content %}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 space-y-6">
            {% if not nodes %}
            <div class="bg-[#171717] p-12 rounded-xl border border-gray-800 text-center">
                <i data-lucide="network" class="w-12 h-12 text-gray-600 mx-auto mb-4"></i>
                <p class="text-gray-500 font-medium">No slave nodes connected to this master.</p>
                <p class="text-xs text-gray-600 mt-2 italic">Register a node to start distributed content synchronization.</p>
            </div>
            {% endif %}
            
            {% for n in nodes %}
            <div class="bg-[#171717] p-6 rounded-xl border border-gray-800 flex justify-between items-center group hover:border-red-500/30 transition-all">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded bg-black flex items-center justify-center text-red-500"><i data-lucide="server"></i></div>
                    <div>
                        <h3 class="font-bold">{{ n.label }}</h3>
                        <p class="text-xs text-gray-500 font-mono">{{ n.url }}</p>
                    </div>
                </div>
                <div class="flex items-center gap-6">
                    <div class="text-right">
                        <span class="text-[10px] font-bold text-green-500 uppercase tracking-widest block">{{ n.status }}</span>
                        <span class="text-[10px] text-gray-600 uppercase font-bold">{{ n.role }}</span>
                    </div>
                    <button class="text-gray-500 hover:text-red-500 transition-colors"><i data-lucide="more-vertical"></i></button>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="space-y-6">
            <div class="bg-[#171717] p-6 rounded-xl border border-gray-800">
                <h2 class="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] mb-4">Node Configuration</h2>
                <div class="space-y-4">
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-400">Master Identity:</span>
                        <span class="font-bold text-red-500 uppercase">Master-01</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-400">Sync Interval:</span>
                        <span class="font-bold">60 MIN</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-400">Network Protocol:</span>
                        <span class="font-bold">BEJSON/REST</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="add-node-modal" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
        <form method="POST" class="bg-[#171717] p-8 rounded-xl border border-gray-800 w-full max-w-md flex flex-col gap-4">
            <h2 class="text-xl font-bold mb-2">Register Slave Node</h2>
            <input name="label" placeholder="Node Name (e.g. Edge-Node-NY)" class="bg-black p-3 rounded border border-gray-800" required>
            <input name="url" placeholder="Public Endpoint URL" class="bg-black p-3 rounded border border-gray-800" required>
            <div class="flex gap-4 mt-4">
                <button type="submit" class="flex-1 bg-red-600 py-3 rounded font-bold">Register</button>
                <button type="button" onclick="document.getElementById('add-node-modal').classList.add('hidden')" class="flex-1 bg-gray-800 py-3 rounded font-bold">Cancel</button>
            </div>
        </form>
    </div>
    {% endblock %}'''
    return render_template_string(html, nodes=nodes)

# =============================================================================
# PREVIEW SERVER ROUTES
# =============================================================================

@app.route('/srv/status')
def srv_status():
    return jsonify({
        "running": _preview_srv["running"],
        "port": _preview_srv["port"],
        "url": f"http://{request.host.split(':')[0]}:{_preview_srv['port']}"
    })

@app.route('/srv/start')
def srv_start():
    port = request.args.get('port', 8080, type=int)
    if port < 8000: port = 8080 # Safety fallback
    
    if not _preview_srv["running"]:
        try:
            _preview_srv["port"] = port
            def run_srv():
                handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=WWW_ROOT, **kwargs)
                socketserver.TCPServer.allow_reuse_address = True
                _preview_srv["httpd"] = socketserver.TCPServer(("", _preview_srv["port"]), handler)
                _preview_srv["running"] = True
                _preview_srv["httpd"].serve_forever()
            
            _preview_srv["thread"] = threading.Thread(target=run_srv, daemon=True)
            _preview_srv["thread"].start()
            return jsonify({"success": True, "message": f"Preview server started on port {port}"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    return jsonify({"success": True, "message": "Server already running"})

@app.route('/srv/stop')
def srv_stop():
    if _preview_srv["running"] and _preview_srv["httpd"]:
        _preview_srv["httpd"].shutdown()
        _preview_srv["httpd"].server_close()
        _preview_srv["running"] = False
        return jsonify({"success": True, "message": "Preview server stopped"})
    return jsonify({"success": True, "message": "Server not running"})

# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def dashboard():
    global_stats = MFDBCore.mfdb_core_get_stats(cms.global_manifest)
    content_stats = MFDBCore.mfdb_core_get_stats(cms.content_manifest)

    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <div class="flex items-center gap-4">
            <h1 class="text-xl font-bold">System Dashboard</h1>
            {% if network_role == "Master" %}
            <span class="bg-red-900/30 text-red-500 border border-red-600 px-3 py-1 rounded-full text-[10px] font-bold">MASTER NODE</span>
            {% elif network_role == "Slave" %}
            <span class="bg-blue-900/30 text-blue-500 border border-blue-600 px-3 py-1 rounded-full text-[10px] font-bold">SLAVE NODE</span>
            {% endif %}
            {% if is_dirty %}

            <span class="bg-amber-900/30 text-amber-500 border border-amber-600 px-3 py-1 rounded-full text-[10px] font-bold animate-pulse">UNSAVED CHANGES</span>
            {% endif %}
        </div>
        <div class="flex gap-2">
            <button onclick="repackDB()" class="bg-red-600 px-4 py-2 rounded font-bold text-sm {% if not is_dirty %}opacity-50 cursor-not-allowed{% endif %}" {% if not is_dirty %}disabled{% endif %}>COMMIT & REPACK</button>
            <a href="/build" class="bg-gray-800 px-4 py-2 rounded font-bold text-sm {% if is_dirty %}opacity-50 cursor-not-allowed pointer-events-none{% endif %}" {% if is_dirty %}title="Repack required before build"{% endif %}>BUILD SITE</a>
        </div>
    {% endblock %}
    {% block content %}
    {% if is_dirty %}
    <div class="bg-amber-950/20 border border-amber-800/50 p-4 rounded-xl mb-8 flex items-center justify-between">
        <div class="flex items-center gap-3 text-amber-500">
            <i data-lucide="alert-triangle"></i>
            <span class="text-sm font-medium">The database has uncommitted changes. You must <b>Repack</b> into the transport archive before you can build the site.</span>
        </div>
        <button onclick="repackDB()" class="text-xs bg-amber-600 text-white px-4 py-2 rounded font-bold hover:bg-amber-500 transition-colors">Repack Now</button>
    </div>
    {% endif %}

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-[#171717] p-6 rounded-xl border border-gray-800">
            <div class="flex justify-between items-start mb-4">
                <h2 class="text-xl font-bold text-red-500">Global Archive</h2>
                <a href="/db/export/global" class="text-[10px] text-gray-500 hover:text-white uppercase font-bold flex items-center gap-1"><i data-lucide="download" class="w-3 h-3"></i> Download .zip</a>
            </div>
            <div class="space-y-2 text-sm text-gray-400">
                <p>Entities: <span class="text-white">{{ g_stats.entity_count }}</span></p>
                <p>Schema: <span class="text-white">{{ g_stats.schema_version }}</span></p>
                <p class="text-[10px] font-mono break-all opacity-50">{{ g_stats.db_name }}</p>
            </div>
        </div>
        <div class="bg-[#171717] p-6 rounded-xl border border-gray-800">
            <div class="flex justify-between items-start mb-4">
                <h2 class="text-xl font-bold text-red-500">Content Archive</h2>
                <a href="/db/export/content" class="text-[10px] text-gray-500 hover:text-white uppercase font-bold flex items-center gap-1"><i data-lucide="download" class="w-3 h-3"></i> Download .zip</a>
            </div>
            <div class="space-y-2 text-sm text-gray-400">
                <p>Entities: <span class="text-white">{{ c_stats.entity_count }}</span></p>
                <p>Schema: <span class="text-white">{{ c_stats.schema_version }}</span></p>
                <p class="text-[10px] font-mono break-all opacity-50">{{ c_stats.db_name }}</p>
            </div>
        </div>
    </div>

    <script>
    async function repackDB() {
        if(!confirm("Are you sure you want to repack the database? This will update the master transport archives.")) return;
        const res = await fetch('/db/repack', {method:'POST'});
        const data = await res.json();
        if(data.success) {
            window.location.reload();
        } else {
            alert("Repack failed: " + data.message);
        }
    }
    </script>
    {% endblock %}'''
    return render_template_string(html, g_stats=global_stats, c_stats=content_stats)

@app.route('/media')
def media_library():
    all_assets = cms.get_assets()
    grouped = collections.defaultdict(list)
    for a in all_assets:
        fname = a.get('filename', '')
        if not fname: continue
        char = fname[0].upper() if fname[0].isalpha() else '#'
        grouped[char].append(a)
    
    sorted_groups = sorted(grouped.items())
    
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Media Library</h1>
        <form action="/media/upload" method="POST" enctype="multipart/form-data" class="flex gap-2">
            <input type="file" name="files" multiple class="bg-black/50 p-2 rounded text-xs border border-gray-800" accept="image/*,video/*,audio/*,.pdf,.zip">
            <button type="submit" class="bg-red-600 px-4 py-2 rounded font-bold text-sm">Upload</button>
        </form>
    {% endblock %}
    {% block content %}
    <div class="space-y-4">
        {% if not groups %}
        <div class="bg-[#171717] p-12 rounded-xl border border-gray-800 text-center text-gray-500">
            No assets found in the library.
        </div>
        {% endif %}
        {% for char, group in groups %}
        <div class="bg-[#171717] rounded-xl border border-gray-800 overflow-hidden">
            <div class="bg-black/30 p-4 font-bold border-b border-gray-800 flex justify-between">
                <span>{{ char }}</span>
                <span class="text-gray-500 text-xs">{{ group|length }} Files</span>
            </div>
            <div class="p-4 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {% for a in group %}
                <div class="bg-black/50 p-2 rounded-lg border border-gray-800 group relative">
                    {% if a.mime_type.startswith('image/') %}
                    <img src="/media/serve/{{ a.filename }}" class="w-full aspect-square object-cover rounded mb-2" onerror="{{ img_onerror }}">
                    {% else %}
                    <div class="w-full aspect-square flex flex-col items-center justify-center bg-gray-900 rounded mb-2 text-[10px] text-gray-500 text-center p-2">
                        <i data-lucide="file" class="mb-2"></i>
                        <span class="truncate w-full">{{ a.mime_type }}</span>
                    </div>
                    {% endif %}
                    <div class="text-[10px] font-mono truncate text-gray-400" title="{{ a.filename }}">{{ a.filename }}</div>
                    <div class="absolute inset-0 bg-black/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                         <a href="/media/delete/{{ a.filename }}" class="text-red-500 p-2" onclick="return confirm('Delete this asset? This cannot be undone.')"><i data-lucide="trash"></i></a>
                         <a href="/media/serve/{{ a.filename }}" target="_blank" class="text-blue-500 p-2"><i data-lucide="external-link"></i></a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endblock %}'''
    return render_template_string(html, groups=sorted_groups, img_onerror=_IMG_ONERROR)

@app.route('/media/upload', methods=['POST'])
def media_upload():
    files = request.files.getlist('files')
    uploaded = 0
    skipped = 0
    for f in files:
        if f:
            data = f.read()
            f_hash = cms.get_file_hash(data)
            existing = cms.get_asset_by_hash(f_hash)
            if existing:
                skipped += 1
                continue
            
            filename = secure_filename(f.filename)
            if os.path.exists(os.path.join(cms.assets_dir, filename)):
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{uuid.uuid4().hex[:4]}{ext}"
            
            fpath = os.path.join(cms.assets_dir, filename)
            with open(fpath, "wb") as wf:
                wf.write(data)
            
            cms.add_asset(filename, f.filename, f_hash, len(data), f.content_type)
            uploaded += 1
            
    flash(f"Uploaded {uploaded}, Skipped {skipped}")
    return redirect(url_for('media_library'))

@app.route('/media/serve/<path:filename>')
def serve_media(filename):
    fpath = os.path.join(cms.assets_dir, filename)
    if not os.path.exists(fpath):
        return "File not found", 404
    return send_from_directory(cms.assets_dir, filename)

@app.route('/media/delete/<filename>')
def media_delete(filename):
    if cms.delete_asset(filename):
        flash("Asset deleted")
    return redirect(url_for('media_library'))

@app.route('/apps', methods=['GET', 'POST'])
def apps():
    import zipfile
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        cat = request.form.get('category')
        feat_img = request.form.get('featured_img')
        entry = request.form.get('entry_file', 'index.html')
        
        # 1. Create entry in DB first to get canonical UUID
        app_uuid = cms.create_app(name, desc, cat, feat_img, entry)
        
        app_file = request.files.get('app_file')
        app_dir = os.path.join(cms.apps_dir, app_uuid)
        os.makedirs(app_dir, exist_ok=True)

        if app_file:
            fname = secure_filename(app_file.filename)
            fpath = os.path.join(app_dir, fname)
            app_file.save(fpath)
            
            if fname.endswith('.zip'):
                with zipfile.ZipFile(fpath, 'r') as z:
                    z.extractall(app_dir)
                os.remove(fpath)
            else:
                # Update entry file to the single uploaded file
                cms.update_app(app_uuid, name, desc, cat, feat_img, fname)
                
        flash("App imported successfully")
        return redirect(url_for('apps'))

    apps_list = cms.get_apps()
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    assets = cms.get_assets()
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Standalone Apps</h1>
        <button onclick="document.getElementById('import-modal').classList.remove('hidden')" class="bg-red-600 px-4 py-2 rounded font-bold text-sm">+ Import App</button>
    {% endblock %}
    {% block content %}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for a in apps %}
        <div class="bg-[#171717] p-6 rounded-xl border border-gray-800 group hover:border-red-500/50 transition-all">
            <h3 class="font-bold text-xl mb-2">{{ a.name }}</h3>
            <p class="text-xs text-gray-500 mb-4 h-12 line-clamp-3">{{ a.description }}</p>
            <div class="flex justify-between items-center mt-auto">
                <span class="text-[10px] tag-font bg-black px-2 py-1 rounded">{{ a.category_fk }}</span>
                <a href="/apps/delete/{{ a.app_uuid }}" class="text-red-500 hover:underline text-xs" onclick="return confirm('Delete?')">Delete</a>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="import-modal" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
        <form method="POST" enctype="multipart/form-data" class="bg-[#171717] p-8 rounded-xl border border-gray-800 w-full max-w-md flex flex-col gap-4">
            <h2 class="text-xl font-bold mb-2">Import HTML App</h2>
            <input name="name" placeholder="App Name" class="bg-black p-3 rounded border border-gray-800" required>
            <textarea name="description" placeholder="Description" class="bg-black p-3 rounded border border-gray-800"></textarea>
            <select name="category" class="bg-black p-3 rounded border border-gray-800">
                {% for c in cats %}<option value="{{ c.slug }}">{{ c.name }}</option>{% endfor %}
            </select>
            <select name="featured_img" class="bg-black p-3 rounded border border-gray-800">
                <option value="">-- Featured Image --</option>
                {% for a in assets %}<option value="{{ a.filename }}">{{ a.filename }}</option>{% endfor %}
            </select>
            <input name="entry_file" placeholder="Entry File (default: index.html)" class="bg-black p-3 rounded border border-gray-800">
            <input type="file" name="app_file" class="bg-black p-3 rounded border border-gray-800" required>
            <div class="flex gap-4 mt-4">
                <button type="submit" class="flex-1 bg-red-600 py-3 rounded font-bold">Import</button>
                <button type="button" onclick="document.getElementById('import-modal').classList.add('hidden')" class="flex-1 bg-gray-800 py-3 rounded font-bold">Cancel</button>
            </div>
        </form>
    </div>
    {% endblock %}'''
    return render_template_string(html, apps=apps_list, cats=cats, assets=assets)

@app.route('/apps/delete/<uuid>')
def app_delete(uuid):
    cms.delete_app(uuid)
    flash("App deleted")
    return redirect(url_for('apps'))

@app.route('/navigation', methods=['GET', 'POST'])
def navigation():
    if request.method == 'POST':
        label = request.form.get('label')
        url = request.form.get('url')
        cms.add_nav_link(label, url)
        flash('Navigation link added')
        return redirect(url_for('navigation'))
    
    links = cms.get_nav_links()
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Site Navigation</h1>
    {% endblock %}
    {% block content %}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 bg-[#171717] rounded-xl border border-gray-800 overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead class="bg-black/30">
                        <tr><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Label</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">URL</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500 text-right">Action</th></tr>
                    </thead>
                    <tbody>
                        {% for l in links %}
                        <tr class="border-t border-gray-800 hover:bg-white/5 transition-colors">
                            <td class="p-4 font-bold">{{ l.label }}</td>
                            <td class="p-4 text-gray-400 font-mono text-sm">{{ l.url }}</td>
                            <td class="p-4 text-right"><a href="/navigation/delete/{{ l.label }}" class="text-red-500 hover:underline text-sm font-bold">Delete</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        <div class="bg-[#171717] p-8 rounded-xl border border-gray-800 h-fit">
            <h2 class="text-xl font-bold mb-6">Add Custom Link</h2>
            <form method="POST" class="flex flex-col gap-4">
                <input name="label" placeholder="Link Label (e.g. GitHub)" class="bg-black p-3 rounded border border-gray-800" required>
                <input name="url" placeholder="URL (e.g. https://...)" class="bg-black p-3 rounded border border-gray-800" required>
                <button type="submit" class="bg-red-600 py-3 rounded font-bold">Add to Menu</button>
            </form>
        </div>
    </div>
    {% endblock %}'''
    return render_template_string(html, links=links)

@app.route('/navigation/delete/<label>')
def navigation_delete(label):
    cms.delete_nav_link(label)
    return redirect(url_for('navigation'))

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        name = request.form.get('name')
        slug = request.form.get('slug')
        desc = request.form.get('description')
        feed = request.form.get('feed_type')
        
        if action == 'edit':
            cms.update_category(slug, name, desc, feed)
            flash('Category updated')
        else:
            cms.add_category(name, slug, desc, feed)
            flash('Category added successfully')
        return redirect(url_for('categories'))
    
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Categories</h1>
        <button onclick="openAddModal()" class="bg-red-600 px-4 py-2 rounded font-bold text-sm">+ New Category</button>
    {% endblock %}
    {% block content %}
    <div class="bg-[#171717] rounded-xl overflow-hidden border border-gray-800">
        <div class="overflow-x-auto">
            <table class="w-full text-left">
                <thead class="bg-black/30">
                    <tr><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Name</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Slug</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Feed Type</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500 text-right">Actions</th></tr>
                </thead>
                <tbody>
                    {% for c in cats %}
                    <tr class="border-t border-gray-800 hover:bg-white/5 transition-colors">
                        <td class="p-4 font-bold">{{ c.name }}</td>
                        <td class="p-4 text-gray-400">{{ c.slug }}</td>
                        <td class="p-4"><span class="bg-gray-800 px-2 py-1 rounded text-[10px] uppercase font-bold">{{ c.feed_type }}</span></td>
                        <td class="p-4 text-right flex justify-end gap-3">
                            <button onclick='openEditModal({{ c | tojson }})' class="text-blue-400 hover:underline text-sm font-bold">Edit</button>
                            <a href="/categories/delete/{{ c.slug }}" class="text-red-500 hover:underline text-sm font-bold" onclick="return confirm('Delete category? Links might break.')">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Category Modal (Add/Edit) -->
    <div id="cat-modal" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
        <form method="POST" class="bg-[#171717] p-8 rounded-xl border border-gray-800 w-full max-w-md flex flex-col gap-4">
            <h2 id="modal-title" class="text-xl font-bold mb-6">Create New Category</h2>
            <input type="hidden" name="action" id="modal-action" value="add">
            
            <div class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase px-1">Display Name</label>
                <input name="name" id="field-name" placeholder="Name" class="bg-black p-3 rounded border border-gray-800" required>
            </div>

            <div class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase px-1">Slug (Identifier)</label>
                <input name="slug" id="field-slug" placeholder="Slug (lowercase)" class="bg-black p-3 rounded border border-gray-800" required>
            </div>

            <div class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase px-1">Description</label>
                <textarea name="description" id="field-desc" placeholder="Description" class="bg-black p-3 rounded border border-gray-800 h-24"></textarea>
            </div>

            <div class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase px-1">Feed Template</label>
                <select name="feed_type" id="field-feed" class="bg-black p-3 rounded border border-gray-800">
                    <option value="blog">Standard Blog Feed</option>
                    <option value="link-grid">Simple Link Grid</option>
                    <option value="gallery">Visual Gallery</option>
                    <option value="card-grid">Modern Card Grid</option>
                </select>
            </div>

            <div class="flex gap-4 mt-4">
                <button type="submit" class="flex-1 bg-red-600 py-3 rounded font-bold">Save Category</button>
                <button type="button" onclick="closeModal()" class="flex-1 bg-gray-800 py-3 rounded font-bold">Cancel</button>
            </div>
        </form>
    </div>

    <script>
        function openAddModal() {
            document.getElementById('modal-title').innerText = "Create New Category";
            document.getElementById('modal-action').value = "add";
            document.getElementById('field-name').value = "";
            document.getElementById('field-slug').value = "";
            document.getElementById('field-slug').readOnly = false;
            document.getElementById('field-desc').value = "";
            document.getElementById('field-feed').value = "blog";
            document.getElementById('cat-modal').classList.remove('hidden');
        }

        function openEditModal(cat) {
            document.getElementById('modal-title').innerText = "Edit Category: " + cat.name;
            document.getElementById('modal-action').value = "edit";
            document.getElementById('field-name').value = cat.name;
            document.getElementById('field-slug').value = cat.slug;
            document.getElementById('field-slug').readOnly = true;
            document.getElementById('field-desc').value = cat.description;
            document.getElementById('field-feed').value = cat.feed_type;
            document.getElementById('cat-modal').classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('cat-modal').classList.add('hidden');
        }
    </script>
    {% endblock %}'''
    return render_template_string(html, cats=cats)

@app.route('/categories/delete/<slug>')
def delete_category(slug):
    cms.delete_category(slug)
    flash(f"Category {slug} deleted")
    return redirect(url_for('categories'))

@app.route('/pages')
def pages():
    pages_list = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Page")
    editor_url = f"http://{request.host.split(':')[0]}:5006"
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Pages</h1>
        <a href="{{ editor_url }}/new" class="bg-red-600 px-4 py-2 rounded font-bold text-sm">+ Create Page</a>
    {% endblock %}
    {% block content %}
    <div class="bg-[#171717] rounded-xl overflow-hidden border border-gray-800">
        <div class="overflow-x-auto">
            <table class="w-full text-left">
                <thead class="bg-black/30">
                    <tr><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Title</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Category</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Type</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Created</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500 text-right">Actions</th></tr>
                </thead>
                <tbody>
                    {% for p in pages %}
                    <tr class="border-t border-gray-800 hover:bg-white/5 transition-colors">
                        <td class="p-4 font-bold">{{ p.title }}</td>
                        <td class="p-4 text-gray-400 text-sm">{{ p.category_fk }}</td>
                        <td class="p-4"><span class="bg-gray-800 px-2 py-1 rounded text-[10px] uppercase font-bold">{{ p.page_type }}</span></td>
                        <td class="p-4 text-gray-500 text-xs">{{ p.created_at }}</td>
                        <td class="p-4 text-right">
                            <a href="{{ editor_url }}/edit/{{ p.page_uuid }}" class="text-blue-400 hover:underline text-sm font-bold">Edit</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
'''
    return render_template_string(html, pages=pages_list, editor_url=editor_url)

@app.route('/authors', methods=['GET', 'POST'])
def authors():
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        name = request.form.get('name')
        bio = request.form.get('bio')
        img = request.form.get('image_url')
        auuid = request.form.get('author_uuid')

        if action == 'edit':
            cms.update_author(auuid, name, bio, img)
            flash('Author updated')
        else:
            cms.add_author(name, bio, img)
            flash('Author added')
        return redirect(url_for('authors'))
    
    authors_list = cms.get_authors()
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Authors</h1>
        <button onclick="openAuthorModal()" class="bg-red-600 px-4 py-2 rounded font-bold text-sm">+ New Author</button>
    {% endblock %}
    {% block content %}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        {% for a in authors %}
        <div class="bg-[#171717] p-6 rounded-xl border border-gray-800 flex items-center gap-4 hover:border-red-500/30 transition-all group">
            <div class="w-16 h-16 rounded-full bg-black/40 overflow-hidden border-2 border-gray-800 flex-shrink-0">
                {% if a.image_url %}
                <img src="/media/serve/{{ a.image_url }}" class="w-full h-full object-contain" onerror="{{ img_onerror }}">
                {% else %}
                <div class="w-full h-full flex items-center justify-center text-gray-500">
                    <i data-lucide="user"></i>
                </div>
                {% endif %}
            </div>
            <div class="flex-grow">
                <h3 class="font-bold">{{ a.name }}</h3>
                <p class="text-xs text-gray-500 line-clamp-1">{{ a.bio }}</p>
                <div class="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onclick='openEditAuthorModal({{ a | tojson }})' class="text-[10px] font-bold text-blue-400 uppercase">Edit</button>
                    <a href="/authors/delete/{{ a.author_uuid }}" class="text-[10px] font-bold text-red-500 uppercase" onclick="return confirm('Delete author?')">Delete</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- Author Modal -->
    <div id="author-modal" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
        <form method="POST" class="bg-[#171717] p-8 rounded-xl border border-gray-800 w-full max-w-md flex flex-col gap-4">
            <h2 id="author-modal-title" class="text-xl font-bold mb-4">Add Author</h2>
            <input type="hidden" name="action" id="author-action" value="add">
            <input type="hidden" name="author_uuid" id="author-uuid">
            
            <input name="name" id="author-name" placeholder="Name" class="bg-black p-3 rounded border border-gray-800" required>
            <textarea name="bio" id="author-bio" placeholder="Bio" class="bg-black p-3 rounded border border-gray-800 h-24" required></textarea>
            
            <div class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase">Profile Image</label>
                <select name="image_url" id="author-img" class="bg-black p-3 rounded border border-gray-800">
                    <option value="">-- No Image --</option>
                    {% for asset in assets %}
                    <option value="{{ asset.filename }}">{{ asset.filename }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="flex gap-4 mt-4">
                <button type="submit" class="flex-1 bg-red-600 py-3 rounded font-bold">Save Profile</button>
                <button type="button" onclick="closeAuthorModal()" class="flex-1 bg-gray-800 py-3 rounded font-bold">Cancel</button>
            </div>
        </form>
    </div>

    <script>
        function openAuthorModal() {
            document.getElementById('author-modal-title').innerText = "Add Author Profile";
            document.getElementById('author-action').value = "add";
            document.getElementById('author-name').value = "";
            document.getElementById('author-bio').value = "";
            document.getElementById('author-img').value = "";
            document.getElementById('author-modal').classList.remove('hidden');
        }
        function openEditAuthorModal(a) {
            document.getElementById('author-modal-title').innerText = "Edit Profile: " + a.name;
            document.getElementById('author-action').value = "edit";
            document.getElementById('author-uuid').value = a.author_uuid;
            document.getElementById('author-name').value = a.name;
            document.getElementById('author-bio').value = a.bio;
            document.getElementById('author-img').value = a.image_url || "";
            document.getElementById('author-modal').classList.remove('hidden');
        }
        function closeAuthorModal() {
            document.getElementById('author-modal').classList.add('hidden');
        }
    </script>
    {% endblock %}'''
    assets = cms.get_assets()
    return render_template_string(html, authors=authors_list, assets=assets, img_onerror=_IMG_ONERROR)

@app.route('/authors/delete/<uuid>')
def delete_author(uuid):
    cms.delete_author(uuid)
    return redirect(url_for('authors'))

@app.route('/ads', methods=['GET', 'POST'])
def ads():
    if request.method == 'POST':
        name = request.form.get('name')
        img = request.form.get('image_url') if request.form.get('ad_type') == 'image' else ""
        link = request.form.get('link_url')
        zone = request.form.get('zone')
        cms.add_ad(name, img, link, zone)
        flash('Ad added')
        return redirect(url_for('ads'))
    
    ads_list = cms.get_ads()
    assets = cms.get_assets()
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Ad Rotator</h1>
        <button onclick="document.getElementById('add-ad-modal').classList.remove('hidden')" class="bg-red-600 px-4 py-2 rounded font-bold text-sm">+ New Ad Unit</button>
    {% endblock %}
    {% block content %}
    <div class="bg-[#171717] rounded-xl overflow-hidden border border-gray-800">
        <div class="overflow-x-auto">
            <table class="w-full text-left">
                <thead class="bg-black/30">
                    <tr><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Name</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Type</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500">Zone</th><th class="p-4 text-xs uppercase tracking-wider text-gray-500 text-right">Status</th></tr>
                </thead>
                <tbody>
                    {% for a in ads %}
                    <tr class="border-t border-gray-800 hover:bg-white/5 transition-colors">
                        <td class="p-4 font-bold">{{ a.name }}</td>
                        <td class="p-4 text-[10px] font-bold uppercase text-gray-500">{{ 'Image' if a.image_url else 'Link Only' }}</td>
                        <td class="p-4 text-xs uppercase text-gray-400">{{ a.zone }}</td>
                        <td class="p-4 text-right"><span class="text-green-500 font-bold text-xs uppercase">Active</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    <div id="add-ad-modal" class="hidden fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
        <form method="POST" class="bg-[#171717] p-8 rounded-xl border border-gray-800 w-full max-w-md flex flex-col gap-4">
            <h2 class="text-xl font-bold mb-2">Create Ad Unit</h2>
            <input name="name" placeholder="Campaign Name" class="bg-black p-3 rounded border border-gray-800" required>
            
            <div class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase">Ad Type</label>
                <select name="ad_type" id="ad-type-select" onchange="toggleAdImageField()" class="bg-black p-3 rounded border border-gray-800">
                    <option value="image">Image Banner</option>
                    <option value="link">Text/Link Only</option>
                </select>
            </div>

            <div id="ad-image-field" class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase">Banner Image</label>
                <select name="image_url" class="bg-black p-3 rounded border border-gray-800">
                    {% for asset in assets %}
                    <option value="{{ asset.filename }}">{{ asset.filename }}</option>
                    {% endfor %}
                </select>
            </div>

            <input name="link_url" placeholder="Destination URL" class="bg-black p-3 rounded border border-gray-800" required>
            
            <div class="flex flex-col gap-1">
                <label class="text-[10px] font-bold text-gray-500 uppercase">Display Zone</label>
                <select name="zone" class="bg-black p-3 rounded border border-gray-800">
                    <option value="sidebar">Sidebar (Square/Vertical)</option>
                    <option value="header">Header (Leaderboard)</option>
                    <option value="footer">Footer (Small)</option>
                </select>
            </div>

            <div class="flex gap-4 mt-4">
                <button type="submit" class="flex-1 bg-red-600 py-3 rounded font-bold">Create</button>
                <button type="button" onclick="document.getElementById('add-ad-modal').classList.add('hidden')" class="flex-1 bg-gray-800 py-3 rounded font-bold">Cancel</button>
            </div>
        </form>
    </div>
    <script>
        function toggleAdImageField() {
            const type = document.getElementById('ad-type-select').value;
            const field = document.getElementById('ad-image-field');
            if (type === 'link') field.classList.add('hidden');
            else field.classList.remove('hidden');
        }
    </script>
    {% endblock %}'''
    return render_template_string(html, ads=ads_list, assets=assets)

@app.route('/about')
def about():
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">About System</h1>
    {% endblock %}
    {% block content %}
    <div class="max-w-3xl bg-[#171717] p-8 rounded-xl border border-gray-800">
        <h2 class="text-xl font-bold text-red-500 mb-4 uppercase tracking-wider">Core Credits</h2>
        <p class="text-gray-300 leading-relaxed mb-6">
            This high-performance static site engine was conceptualized and developed by 
            <span class="text-white font-bold underline decoration-red-500 underline-offset-4">Elton Boehnen</span>. 
            It is designed to be a lightweight, ultra-fast alternative to traditional bloated CMS platforms.
        </p>
        
        <h2 class="text-xl font-bold text-red-500 mb-4 uppercase tracking-wider">Technology Stack</h2>
        <ul class="list-disc list-inside text-gray-400 space-y-2 mb-8">
            <li><span class="text-white font-bold">BEJSON</span>: The Strict Tabular JSON Standard for high-speed data integrity.</li>
            <li><span class="text-white font-bold">MFDB</span>: Multi-File Database orchestration for scalable serverless architecture.</li>
            <li><span class="text-white font-bold">Jinja2</span>: Professional-tier Python templating engine.</li>
            <li><span class="text-white font-bold">Vanilla JS</span>: Zero-dependency frontend performance.</li>
        </ul>

        <div class="flex gap-4">
            <a href="https://github.com/boehnenelton" target="_blank" class="bg-gray-800 hover:bg-gray-700 px-6 py-2 rounded font-bold transition-all flex items-center gap-2">
                <i data-lucide="github"></i> GitHub
            </a>
            <a href="https://boehnenelton2024.pages.dev" target="_blank" class="bg-red-600 hover:bg-red-700 px-6 py-2 rounded font-bold transition-all flex items-center gap-2">
                <i data-lucide="external-link"></i> Live Site
            </a>
        </div>
    </div>
    {% endblock %}'''
    return render_template_string(html)

@app.route('/edit/<uuid>', methods=['GET', 'POST'])
def edit_page_basic(uuid):
    if request.method == 'POST':
        title = request.form.get('title')
        cat = request.form.get('category')
        ptype = request.form.get('page_type')
        html_body = request.form.get('html_body')
        
        content_data = {"html_body": html_body}
        cms.update_page(uuid, title, cat, ptype, content_data)
        flash("Page updated (Basic Editor)")
        return redirect(url_for('pages'))

    page_data = cms.get_full_page_data(uuid)
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    if not page_data: return "Page not found", 404
    
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Basic HTML Editor</h1>
        <div class="flex gap-4">
            <button onclick="document.getElementById('basic-editor-form').submit()" class="bg-red-600 px-6 py-2 rounded font-bold text-sm">SAVE CHANGES</button>
            <a href="/pages" class="bg-gray-800 px-6 py-2 rounded font-bold text-sm">CANCEL</a>
        </div>
    {% endblock %}
    {% block content %}
    <form id="basic-editor-form" method="POST" class="flex flex-col gap-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label class="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-widest">Title</label>
                <input name="title" value="{{ p.title }}" class="w-full bg-black p-3 rounded border border-gray-800 focus:border-red-500 outline-none transition-colors">
            </div>
            <div>
                <label class="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-widest">Category</label>
                <select name="category" class="w-full bg-black p-3 rounded border border-gray-800 focus:border-red-500 outline-none transition-colors">
                    {% for c in cats %}
                    <option value="{{ c.slug }}" {% if c.slug == p.category_fk %}selected{% endif %}>{{ c.name }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>
        <input type="hidden" name="page_type" value="{{ p.page_type }}">
        <div>
            <label class="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-widest">Raw HTML Content</label>
            <textarea name="html_body" class="w-full h-[500px] bg-black p-6 rounded border border-gray-800 font-mono text-sm focus:border-red-500 outline-none transition-colors">{{ p.html_body }}</textarea>
        </div>
    </form>
    {% endblock %}'''
    return render_template_string(html, p=page_data, cats=cats)

@app.route('/pages/new')
def pages_new_redirect():
    editor_url = f"http://{request.host.split(':')[0]}:5006"
    return redirect(f"{editor_url}/new")

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        for key, value in request.form.items():
            cms.add_global_config(key, value)
        flash('Configuration updated')
        return redirect(url_for('config'))
    
    configs = cms.get_global_configs()
    html = '''{% extends "admin_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Global Configuration</h1>
        <button onclick="document.getElementById('config-form').submit()" class="bg-red-600 px-6 py-2 rounded font-bold text-sm">SAVE SETTINGS</button>
    {% endblock %}
    {% block content %}
    <form id="config-form" method="POST" class="max-w-2xl bg-[#171717] p-8 rounded-xl border border-gray-800 flex flex-col gap-6">
        {% for key, value in configs.items() %}
        <div>
            <label class="block text-[10px] font-bold text-gray-500 mb-2 uppercase tracking-[0.2em]">{{ key }}</label>
            <input name="{{ key }}" value="{{ value }}" class="w-full bg-black p-3 rounded border border-gray-800 focus:border-red-500 outline-none transition-colors">
        </div>
        {% endfor %}
    </form>
    <div class="mt-12 pt-8 border-t border-gray-800">
        <h2 class="text-xl font-bold text-red-500 mb-4 uppercase tracking-widest">Danger Zone</h2>
        <a href="/factory_reset" class="bg-red-900/30 border border-red-600 text-red-500 px-6 py-3 rounded font-bold hover:bg-red-600 hover:text-white transition-all inline-block" onclick="return confirm('WARNING: This will delete ALL data, pages, and assets. Proceed?')">⚡ FACTORY RESET SYSTEM</a>
    </div>
    {% endblock %}'''
    return render_template_string(html, configs=configs)

@app.route('/factory_reset')
def reset_system():
    cms.factory_reset()
    cms.mount_system(force=True)
    flash("System has been factory reset and remounted.")
    return redirect(url_for('dashboard'))

@app.route('/build')
def build_site():
    if cms.is_dirty:
        flash("ERROR: Database is dirty. You must Repack Changes before building the site.", "error")
        return redirect(url_for('dashboard'))

    import subprocess
    try:
        # Use cwd instead of os.chdir to keep process state clean
        # Builder is now in Lib/tools/
        builder_path = os.path.join("Lib", "tools", "MFDB_Builder.py")
        result = subprocess.run([sys.executable, builder_path], cwd=BASE_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            flash("Site built successfully!")
        else:
            flash(f"Build failed: {result.stderr}")
    except Exception as e:
        flash(f"Build error: {str(e)}")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
