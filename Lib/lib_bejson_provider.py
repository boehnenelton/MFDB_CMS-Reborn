"""
Library:     lib_bejson_provider.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import json
import datetime

class BEJSONProvider:
    @staticmethod
    def get_paths_schema():
        return {
            "Format": "BEJSON",
            "Format_Version": "104a",
            "Format_Creator": "Elton Boehnen",
            "Schema_Version": "v1.0",
            "Application_Name": "BEJSON Pad",
            "Records_Type": ["PathEntry"],
            "Fields": [
                {"name": "path_id",    "type": "string"},
                {"name": "path_type",  "type": "string"},
                {"name": "path",       "type": "string"},
                {"name": "label",      "type": "string"},
                {"name": "created_at", "type": "string"},
            ],
            "Values": []
        }

    @staticmethod
    def get_index_schema():
        return {
            "Format": "BEJSON",
            "Format_Version": "104db",
            "Format_Creator": "Elton Boehnen",
            "Records_Type": ["Category", "Note"],
            "Fields": [
                {"name": "Record_Type_Parent",  "type": "string"},
                {"name": "cat_id",              "type": "string",  "Record_Type_Parent": "Category"},
                {"name": "cat_name",            "type": "string",  "Record_Type_Parent": "Category"},
                {"name": "created_at_cat",      "type": "string",  "Record_Type_Parent": "Category"},
                {"name": "note_id",             "type": "string",  "Record_Type_Parent": "Note"},
                {"name": "note_name",           "type": "string",  "Record_Type_Parent": "Note"},
                {"name": "cat_id_fk",           "type": "string",  "Record_Type_Parent": "Note"},
                {"name": "file_path",           "type": "string",  "Record_Type_Parent": "Note"},
                {"name": "created_at_note",     "type": "string",  "Record_Type_Parent": "Note"},
                {"name": "updated_at",          "type": "string",  "Record_Type_Parent": "Note"},
            ],
            "Values": []
        }

    @staticmethod
    def load_bejson(path, default_schema):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return default_schema

    @staticmethod
    def save_bejson(path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def get_fields_map(db):
        return {f["name"]: i for i, f in enumerate(db["Fields"])}

    @staticmethod
    def now_iso():
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
