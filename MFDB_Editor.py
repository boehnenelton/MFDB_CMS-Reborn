"""
MFDB Editor - Standalone Content Editor
Description: A specialized editor for MFDB-CMS-Reborn.
             Provides dynamic, type-specific specialized views.
"""
import os
import sys
import json
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify

# Add Lib to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "Lib")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

app = Flask(__name__)
app.secret_key = 'mfdb-editor-secret'

DATA_ROOT = os.path.join(BASE_DIR, "Data")
cms = MFDB_CMS_Manager(DATA_ROOT)

# Ensure system is initialized
cms.initialize_system()

# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def list_pages():
    pages = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Page")
    html = '''{% extends "editor_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">Content Library</h1>
        <a href="/new" class="bg-red-600 text-white px-4 py-2 rounded font-bold text-sm hover:bg-red-700 transition-all">Create New Page</a>
    {% endblock %}
    {% block content %}
    <div class="max-w-5xl mx-auto">
        <div class="grid gap-4">
            {% for p in pages %}
            <div class="bg-[#171717] p-6 rounded-xl border border-gray-800 flex justify-between items-center group hover:border-gray-600 transition-colors">
                <div>
                    <h3 class="font-bold text-lg mb-1">{{ p.title }}</h3>
                    <div class="flex gap-4 text-sm text-gray-500">
                        <span><i data-lucide="folder" class="inline w-3 h-3"></i> {{ p.category_fk }}</span>
                        <span class="uppercase font-bold text-red-500/80 text-[10px] tracking-widest">{{ p.page_type }}</span>
                    </div>
                </div>
                <div class="flex gap-2">
                    <a href="/edit/{{ p.page_uuid }}" class="bg-gray-800 hover:bg-gray-700 p-3 rounded-lg transition-all"><i data-lucide="edit-3"></i></a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}'''
    return render_template_string(html, pages=pages)

@app.route('/new')
def new_page():
    # Pass an empty dict as 'p' to reuse the same form logic
    p = {
        "page_uuid": "", "title": "", "page_type": "article", 
        "category_fk": "uncategorized", "author_fk": "", 
        "featured_img": "", "html_body": "", "video_url": "", 
        "pdf_url": "", "source_files": []
    }
    return edit_page_view(p)

@app.route('/edit/<uuid>')
def edit_page(uuid):
    page_data = cms.get_full_page_data(uuid)
    if not page_data: return "Page not found", 404
    return edit_page_view(page_data)

def edit_page_view(p):
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    authors = cms.get_authors()
    assets = cms.get_assets()
    
    html = '''{% extends "editor_base.html" %}
    {% block toolbar %}
        <h1 class="text-xl font-bold">{% if p.page_uuid %}Edit Page{% else %}New Page{% endif %}</h1>
        <div class="flex gap-4">
             <button onclick="savePage()" class="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-all shadow-lg shadow-red-900/20">
                <i data-lucide="save"></i> <span id="save-btn-text" class="hidden sm:inline">SAVE PAGE</span><span class="sm:hidden">SAVE</span>
            </button>
        </div>
    {% endblock %}
    {% block content %}
    <div class="max-w-7xl mx-auto">
        <div id="editor-form" class="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <input type="hidden" id="page_uuid" value="{{ p.page_uuid }}">
            
            <!-- Main Content Area (3/4 width) -->
            <div class="lg:col-span-3 flex flex-col gap-6">
                <div class="bg-[#171717] p-6 rounded-xl border border-gray-800">
                    <label class="block text-[10px] font-bold text-gray-500 mb-2 uppercase tracking-widest">Page Title</label>
                    <input id="title" value="{{ p.title }}" class="form-input text-2xl font-bold bg-transparent border-none p-0 focus:ring-0 w-full" placeholder="Untitled Page" required>
                </div>
                
                <!-- TYPE SPECIFIC VIEW: Video -->
                <div id="view-video" class="type-view hidden bg-[#171717] p-6 rounded-xl border border-gray-800">
                    <label class="block text-sm font-bold text-gray-500 mb-2 uppercase">YouTube Embed URL</label>
                    <div class="flex gap-4">
                        <div class="bg-black p-3 rounded-lg text-red-500"><i data-lucide="youtube"></i></div>
                        <input id="video_url" value="{{ p.video_url }}" class="form-input" placeholder="https://www.youtube.com/embed/...">
                    </div>
                </div>

                <!-- TYPE SPECIFIC VIEW: PDF -->
                <div id="view-pdf" class="type-view hidden bg-[#171717] p-6 rounded-xl border border-gray-800">
                    <label class="block text-sm font-bold text-gray-500 mb-2 uppercase">Target Document (PDF)</label>
                    <div class="flex gap-4">
                        <div class="bg-black p-3 rounded-lg text-blue-500"><i data-lucide="file-text"></i></div>
                        <select id="pdf_url" class="form-input">
                            <option value="">-- Select from Media Library --</option>
                            {% for a in assets %}
                            <option value="{{ a.filename }}" {% if a.filename == p.pdf_url %}selected{% endif %}>{{ a.filename }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>

                <!-- TYPE SPECIFIC VIEW: Source Code -->
                <div id="view-source-code" class="type-view hidden bg-[#171717] p-6 rounded-xl border border-gray-800">
                    <div class="flex justify-between items-center mb-4">
                        <label class="block text-sm font-bold text-gray-500 uppercase text-red-500">Source Code Repositories</label>
                        <button type="button" onclick="addFile()" class="text-xs bg-red-600 px-3 py-1 rounded font-bold">+ ADD FILE</button>
                    </div>
                    <div id="file-editor-container" class="flex flex-col gap-4">
                        {% for file in p.source_files %}
                        <div class="file-entry border border-gray-800 p-4 rounded-lg bg-black/30">
                            <input class="file-name bg-black border border-gray-800 p-2 rounded text-xs w-full mb-2" value="{{ file.filename }}" placeholder="filename.js">
                            <textarea class="file-content bg-black border border-gray-800 p-2 rounded text-xs font-mono w-full h-[200px]">{{ file.content }}</textarea>
                            <button type="button" onclick="this.parentElement.remove()" class="text-red-500 text-[10px] font-bold mt-2">REMOVE FILE</button>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <!-- Global Content (Description/Body) -->
                <div class="bg-[#171717] p-6 rounded-xl border border-gray-800">
                    <label id="body-label" class="block text-sm font-bold text-gray-500 mb-2 uppercase">Page Content</label>
                    <textarea id="html_body" class="form-input h-[500px] font-mono">{{ p.html_body }}</textarea>
                </div>
            </div>

            <!-- Sidebar Sidebar (1/4 width) -->
            <div class="flex flex-col gap-6">
                <div class="bg-[#171717] p-6 rounded-xl border border-gray-800">
                    <h3 class="font-bold mb-4 border-b border-gray-800 pb-2 uppercase text-xs tracking-widest text-gray-500">Settings</h3>
                    <div class="flex flex-col gap-4">
                        <div>
                            <label class="block text-[10px] font-bold text-gray-500 mb-1 uppercase">Template Type</label>
                            <select id="page_type_select" class="form-input text-sm border-red-900/50" onchange="switchView(this.value)">
                                <option value="article" {% if p.page_type == 'article' %}selected{% endif %}>Standard Article</option>
                                <option value="video" {% if p.page_type == 'video' %}selected{% endif %}>YouTube Video</option>
                                <option value="pdf-viewer" {% if p.page_type == 'pdf-viewer' %}selected{% endif %}>PDF Viewer</option>
                                <option value="source-code" {% if p.page_type == 'source-code' %}selected{% endif %}>Source Code</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-[10px] font-bold text-gray-500 mb-1 uppercase">Category</label>
                            <select id="category" class="form-input text-sm">
                                {% for c in cats %}
                                <option value="{{ c.slug }}" {% if c.slug == p.category_fk %}selected{% endif %}>{{ c.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block text-[10px] font-bold text-gray-500 mb-1 uppercase">Author</label>
                            <select id="author_fk" class="form-input text-sm">
                                <option value="">None</option>
                                {% for a in authors %}
                                <option value="{{ a.author_uuid }}" {% if a.author_uuid == p.author_fk %}selected{% endif %}>{{ a.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block text-[10px] font-bold text-gray-500 mb-1 uppercase">Featured Image</label>
                            <select id="featured_img" class="form-input text-sm">
                                <option value="">-- No Image --</option>
                                {% for a in assets %}
                                <option value="{{ a.filename }}" {% if a.filename == p.featured_img %}selected{% endif %}>{{ a.filename }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchView(type) {
            // Hide all specialized views
            document.querySelectorAll('.type-view').forEach(v => v.classList.add('hidden'));
            
            // Show selected
            if (type === 'video') document.getElementById('view-video').classList.remove('hidden');
            if (type === 'pdf-viewer') document.getElementById('view-pdf').classList.remove('hidden');
            if (type === 'source-code') document.getElementById('view-source-code').classList.remove('hidden');
            
            // Update labels
            const label = document.getElementById('body-label');
            if (type === 'article') label.innerText = 'ARTICLE BODY (HTML)';
            else label.innerText = 'DESCRIPTION (HTML)';
        }

        function addFile() {
            const container = document.getElementById('file-editor-container');
            const div = document.createElement('div');
            div.className = 'file-entry border border-gray-800 p-4 rounded-lg bg-black/30';
            div.innerHTML = `
                <input class="file-name bg-black border border-gray-800 p-2 rounded text-xs w-full mb-2" placeholder="filename.js">
                <textarea class="file-content bg-black border border-gray-800 p-2 rounded text-xs font-mono w-full h-[200px]"></textarea>
                <button type="button" onclick="this.parentElement.remove()" class="text-red-500 text-[10px] font-bold mt-2">REMOVE FILE</button>
            `;
            container.appendChild(div);
            lucide.createIcons();
        }

        async function savePage() {
            const btnText = document.getElementById('save-btn-text');
            btnText.innerText = 'SAVING...';
            
            const source_files = [];
            document.querySelectorAll('.file-entry').forEach(entry => {
                source_files.push({
                    filename: entry.querySelector('.file-name').value,
                    content: entry.querySelector('.file-content').value
                });
            });

            const payload = {
                page_uuid: document.getElementById('page_uuid').value,
                title: document.getElementById('title').value,
                category: document.getElementById('category').value,
                page_type: document.getElementById('page_type_select').value,
                html_body: document.getElementById('html_body').value,
                video_url: document.getElementById('video_url').value,
                pdf_url: document.getElementById('pdf_url').value,
                featured_img: document.getElementById('featured_img').value,
                author_fk: document.getElementById('author_fk').value,
                source_files: source_files
            };

            try {
                const res = await fetch('/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if(data.success) {
                    window.location.href = '/';
                } else {
                    alert("Save failed: " + data.message);
                    btnText.innerText = 'SAVE PAGE';
                }
            } catch(e) {
                alert("Network error: " + e);
                btnText.innerText = 'SAVE PAGE';
            }
        }

        // Initialize view on load
        window.onload = () => switchView(document.getElementById('page_type_select').value);
    </script>
    {% endblock %}'''
    return render_template_string(html, p=p, cats=cats, authors=authors, assets=assets)

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    page_uuid = data.get('page_uuid')
    title = data.get('title')
    cat = data.get('category')
    ptype = data.get('page_type')
    
    content_data = {
        "html_body": data.get('html_body', ''),
        "source_files": data.get('source_files', []),
        "video_url": data.get('video_url', ''),
        "pdf_url": data.get('pdf_url', ''),
        "featured_img": data.get('featured_img', ''),
        "author_fk": data.get('author_fk', '')
    }

    try:
        if page_uuid:
            cms.update_page(page_uuid, title, cat, ptype, content_data)
        else:
            cms.create_page(title, cat, ptype, content_data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
