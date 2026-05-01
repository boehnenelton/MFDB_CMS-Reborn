"""
Library:     lib_bejson_static_backend.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL) CoreEvo fork
Date:        2026-04-23
Description: Authoritative Data Backend for Static Site Generation.
             Unifies access to standard BEJSON files and MFDB v2.0 structures.
"""
import os
import json
import datetime

class BEJSONBackend:
    """
    Unified loader for BEJSON-based datasets.
    Handles standard 104/104a/104db files AND MFDB (Manifest-Entity) resolution.
    """
    def __init__(self, root_path=None):
        self.root = root_path or "/storage/7B30-0E0B/Core-Command"

    def _load_json(self, path):
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            return json.load(f)

    def resolve_dataset(self, source_path):
        """
        Determines if source is a single BEJSON file or an MFDB manifest.
        Returns a dictionary of datasets: { entity_name: { fields, values, metadata } }
        """
        data = self._load_json(source_path)
        if not data:
            return {}

        # Check if it's an MFDB Manifest (104a.mfdb.bejson)
        is_mfdb = os.path.basename(source_path) == "104a.mfdb.bejson"
        
        if is_mfdb:
            return self._load_mfdb(source_path, data)
        else:
            # Standard single-file BEJSON
            name = os.path.splitext(os.path.basename(source_path))[0]
            return {
                name: {
                    "fields": data.get("Fields", []),
                    "values": data.get("Values", []),
                    "metadata": {
                        "Format": data.get("Format"),
                        "Version": data.get("Format_Version"),
                        "Path": source_path
                    }
                }
            }

    def _load_mfdb(self, manifest_path, manifest_data):
        """Resolves all entities defined in an MFDB manifest."""
        mfdb_root = os.path.dirname(manifest_path)
        entities = {}
        
        headers = [f['name'] for f in manifest_data['Fields']]
        try:
            idx_name = headers.index("Entity_Name")
            idx_path = headers.index("Entity_File_Path")
        except ValueError:
            print(f"Error: Invalid MFDB Manifest structure at {manifest_path}")
            return {}

        for row in manifest_data['Values']:
            e_name = row[idx_name]
            # Handle relative paths within the MFDB data directory
            e_rel_path = row[idx_path]
            e_abs_path = os.path.join(mfdb_root, e_rel_path)
            
            e_data = self._load_json(e_abs_path)
            if e_data:
                entities[e_name] = {
                    "fields": e_data.get("Fields", []),
                    "values": e_data.get("Values", []),
                    "metadata": {
                        "Entity_Name": e_name,
                        "Path": e_abs_path,
                        "Parent_MFDB": manifest_path
                    }
                }
        return entities

    def get_static_context(self, source_path):
        """
        Transforms a BEJSON source into a flattened list of "Page Contexts"
        suitable for consumption by html2/wiki builders.
        """
        datasets = self.resolve_dataset(source_path)
        contexts = []
        
        for name, data in datasets.items():
            contexts.append({
                "page_title": name.replace("_", " ").title(),
                "file_name": f"{name.lower()}.html",
                "headers": [f['name'] for f in data['fields']],
                "rows": data['values'],
                "metadata": data['metadata']
            })
        return contexts

if __name__ == "__main__":
    # Self-Test
    backend = BEJSONBackend()
    print("Backend Library Loaded.")
