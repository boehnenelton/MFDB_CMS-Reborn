"""
MFDB Site Manager - Configuration & Preview Tool
Description: Handles site-wide settings, sitemap generation triggers, 
             and provides a local preview server for the static build.
"""
import os
import sys
import threading
import http.server
import socketserver
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify

# Add Lib to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "Lib")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager

app = Flask(__name__)
app.secret_key = 'mfdb-manager-secret'

DATA_ROOT = os.path.join(BASE_DIR, "Data")
WWW_ROOT = os.path.join(BASE_DIR, "Processing", "www")
cms = MFDB_CMS_Manager(DATA_ROOT)

# Global for preview server
_preview_srv = {
    "thread": None,
    "httpd": None,
    "port": 8080,
    "running": False
}

@app.route('/')
def index():
    configs = cms.get_global_configs()
    html = '''{% extends "manager_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Site Configuration</h1>
        <button onclick="document.getElementById('config-form').submit()" class="bg-red-600 px-6 py-2 rounded font-bold text-sm">UPDATE CORE SETTINGS</button>
    {% endblock %}
    {% block content %}
    <form id="config-form" action="/save_config" method="POST" class="max-w-2xl bg-[#171717] p-8 rounded-xl border border-gray-800 flex flex-col gap-6">
        <div>
            <label class="block text-sm font-bold text-gray-500 mb-2 uppercase">Base URL (For Sitemap)</label>
            <input name="base_url" value="{{ configs.get('base_url', '') }}" placeholder="https://yoursite.com" class="w-full bg-black p-3 rounded border border-gray-800 focus:border-red-500 outline-none transition-colors">
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-500 mb-2 uppercase">Site Title</label>
            <input name="site_title" value="{{ configs.get('site_title', '') }}" class="w-full bg-black p-3 rounded border border-gray-800 focus:border-red-500 outline-none transition-colors">
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-500 mb-2 uppercase">SEO Tagline</label>
            <input name="site_tagline" value="{{ configs.get('site_tagline', '') }}" class="w-full bg-black p-3 rounded border border-gray-800 focus:border-red-500 outline-none transition-colors">
        </div>
    </form>
    {% endblock %}'''
    return render_template_string(html, configs=configs)

@app.route('/save_config', methods=['POST'])
def save_config():
    for key, val in request.form.items():
        cms.add_global_config(key, val)
    flash("Settings updated")
    return redirect(url_for('index'))

@app.route('/preview')
def preview():
    status = _preview_srv["running"]
    url = f"http://{request.host.split(':')[0]}:{_preview_srv['port']}"
    html = '''{% extends "manager_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Live Preview Server</h1>
        <div class="flex gap-4">
            {% if not running %}
            <a href="/srv/start" class="bg-green-600 px-6 py-2 rounded font-bold text-sm">START SERVER</a>
            {% else %}
            <a href="/srv/stop" class="bg-gray-800 px-6 py-2 rounded font-bold text-sm">STOP SERVER</a>
            {% endif %}
        </div>
    {% endblock %}
    {% block content %}
    <div class="bg-[#171717] p-8 rounded-xl border border-gray-800 flex flex-col gap-8 max-w-2xl">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-gray-500 uppercase text-xs font-bold mb-1">Server Status</p>
                {% if running %}
                <span class="text-green-500 font-bold flex items-center gap-2"><i data-lucide="zap" class="fill-current"></i> ONLINE</span>
                {% else %}
                <span class="text-red-500 font-bold flex items-center gap-2"><i data-lucide="zap-off"></i> OFFLINE</span>
                {% endif %}
            </div>
        </div>

        {% if running %}
        <div class="bg-black p-6 rounded-lg border border-gray-800">
            <p class="text-gray-500 uppercase text-xs font-bold mb-4">Preview URL</p>
            <div class="flex items-center gap-4">
                <code id="preview-url" class="text-xl text-red-500 font-bold flex-grow">{{ url }}</code>
                <button onclick="copyURL()" class="bg-white text-black px-4 py-2 rounded font-bold text-sm">COPY</button>
            </div>
        </div>
        {% endif %}
    </div>
    <script>
        function copyURL() {
            const url = document.getElementById('preview-url').innerText;
            navigator.clipboard.writeText(url);
            alert('URL Copied to Clipboard!');
        }
    </script>
    {% endblock %}'''
    return render_template_string(html, running=status, url=url)

@app.route('/srv/start')
def srv_start():
    if not _preview_srv["running"]:
        def run_srv():
            # Use directory parameter instead of os.chdir to keep process state clean
            handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=WWW_ROOT, **kwargs)
            # Use Allow Reuse Address to avoid port being held
            socketserver.TCPServer.allow_reuse_address = True
            _preview_srv["httpd"] = socketserver.TCPServer(("", _preview_srv["port"]), handler)
            _preview_srv["running"] = True
            _preview_srv["httpd"].serve_forever()
        
        _preview_srv["thread"] = threading.Thread(target=run_srv, daemon=True)
        _preview_srv["thread"].start()
        flash("Preview server started")
    return redirect(url_for('preview'))

@app.route('/srv/stop')
def srv_stop():
    if _preview_srv["running"] and _preview_srv["httpd"]:
        _preview_srv["httpd"].shutdown()
        _preview_srv["httpd"].server_close()
        _preview_srv["running"] = False
        flash("Preview server stopped")
    return redirect(url_for('preview'))

@app.route('/build_trigger')
def build_trigger():
    import subprocess
    try:
        # Use cwd instead of os.chdir to keep process state clean
        # Builder is now in Lib/tools/
        builder_path = os.path.join("Lib", "tools", "MFDB_Builder.py")
        result = subprocess.run([sys.executable, builder_path], cwd=BASE_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            flash("Build completed successfully!")
        else:
            flash(f"Build failed: {result.stderr}")
    except Exception as e:
        flash(f"Build error: {str(e)}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
