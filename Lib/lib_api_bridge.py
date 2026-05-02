"""
Library:     lib_api_bridge.py
Purpose:     Disconnected API Middleware for SwitchCore.
             Syndicates MFDB CMS content to external services (Blogger, etc.).
"""
import os
import sys
import json

# Pathing setup
HOME = "/data/data/com.termux/files/home"
LIB_AI_DIR = os.path.join(HOME, "lib/py/AI")
LIB_CORE_DIR = os.path.join(HOME, "lib/py/Core")

if LIB_AI_DIR not in sys.path: sys.path.append(LIB_AI_DIR)
if LIB_CORE_DIR not in sys.path: sys.path.append(LIB_CORE_DIR)

try:
    from lib_blogger_manager import BloggerManager
except ImportError:
    print("API Bridge: BloggerManager not found.")
    BloggerManager = None

class APIBridge:
    def __init__(self):
        self.blogger = None
        self._init_blogger()

    def _init_blogger(self):
        secret_path = os.path.join(HOME, ".env/blogger_credentials.bejson")
        if os.path.exists(secret_path) and BloggerManager:
            try:
                # Assuming state path is temp for now
                self.blogger = BloggerManager(secret_path, "/tmp/blogger_state.json")
                # Note: authenticate() might require user interaction on first run
            except Exception as e:
                print(f"API Bridge: Blogger init failed: {e}")

    def syndicate_to_blogger(self, blog_id, title, html_content, is_draft=True):
        if not self.blogger:
            return {"error": "Blogger not initialized"}
        
        try:
            self.blogger.authenticate()
            result = self.blogger.create_post(blog_id, title, html_content, is_draft=is_draft)
            return {"success": True, "post_id": result.get("id"), "url": result.get("url")}
        except Exception as e:
            return {"error": str(e)}

    def list_syndication_targets(self):
        return ["Blogger"]
