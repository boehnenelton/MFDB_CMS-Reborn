"""
MFDB Builder - Static Site Generator
Description: Builds the static website from MFDB data using boehnenelton2024 skeletons.
"""
import os
import sys
import shutil
import random
import re
from jinja2 import Template

# Add Lib to path
# Since this tool is in Lib/tools/, project root is two levels up
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB_DIR = os.path.join(PROJECT_ROOT, "Lib")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_cms_mfdb import MFDB_CMS_Manager
import lib_mfdb_core as MFDBCore

class MFDB_Builder:
    def __init__(self, data_root: str, skel_dir: str, output_dir: str):
        self.cms = MFDB_CMS_Manager(data_root)
        self.skel_dir = skel_dir
        self.output_dir = output_dir
        
        # Load Global Skeletons
        with open(os.path.join(skel_dir, "Global_Skeleton.html"), "r") as f:
            self.global_skel = f.read()
        self.random = random
        self.site_urls = []

    def build_site(self):
        print(f"Starting build to: {self.output_dir}")
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
        
        # 1. Copy Physical Files
        self._copy_apps()
        self._copy_assets()

        self.site_urls = []
        # 2. Prepare Global Data
        site_config = self.cms.get_global_configs()
        self.base_url = site_config.get("base_url", "https://boehnenelton2024.pages.dev").rstrip('/')
        nav_links = self.cms.get_nav_links()
        all_categories = MFDBCore.mfdb_core_load_entity(self.cms.content_manifest, "Category")
        
        # Filter: Only keep categories that have at least one page or app
        categories = []
        for cat in all_categories:
            pages = self.cms.get_pages_in_category(cat["slug"])
            apps = self.cms.get_apps_in_category(cat["slug"])
            if len(pages) > 0 or len(apps) > 0:
                categories.append(cat)
        
        # Sort: Alphabetically by name
        categories.sort(key=lambda x: x["name"].lower())

        social_links = MFDBCore.mfdb_core_load_entity(self.cms.global_manifest, "SocialLink")
        all_ads = self.cms.get_ads()
        all_authors = self.cms.get_authors()

        global_context = {
            "site_title": site_config.get("site_title", "boehnenelton2024"),
            "site_tagline": site_config.get("site_tagline", "personal page for my projects"),
            "nav_links": nav_links,
            "categories": categories,
            "social_links": social_links,
            "all_ads": all_ads,
            "all_authors": all_authors
        }

        # 3. Build Homepage
        self._build_homepage(global_context)

        # 4. Build Categories & Pages
        for cat in categories:
            self._build_category(cat, global_context)
            
        # 5. Generate Sitemap
        self._generate_sitemap()

    def _copy_apps(self):
        apps_dest = os.path.join(self.output_dir, "apps")
        if os.path.exists(self.cms.apps_dir):
            try:
                if os.path.exists(apps_dest):
                    shutil.rmtree(apps_dest)
                shutil.copytree(self.cms.apps_dir, apps_dest)
                print(f"[SUCCESS] Copied apps to {apps_dest}")
            except Exception as e:
                print(f"[ERROR] Failed to copy apps: {e}")

    def _copy_assets(self):
        """Copy media library assets and system assets to the static build assets folder."""
        assets_dest = os.path.join(self.output_dir, "assets")
        if os.path.exists(assets_dest):
            shutil.rmtree(assets_dest)
        os.makedirs(assets_dest)
        
        success_count = 0
        fail_count = 0
        
        # 1. Copy Content Assets
        if os.path.exists(self.cms.assets_dir):
            for item in os.listdir(self.cms.assets_dir):
                s = os.path.join(self.cms.assets_dir, item)
                d = os.path.join(assets_dest, item)
                if os.path.isfile(s):
                    try:
                        shutil.copy2(s, d)
                        success_count += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to copy content asset {item}: {e}")
                        fail_count += 1
        
        # 2. Copy System Assets (e.g., default-feature.png)
        system_assets_dir = os.path.join(PROJECT_ROOT, "Assets")
        # Special case: Copy MFDBCMS.png from root if it exists
        root_stock_img = os.path.join(PROJECT_ROOT, "MFDBCMS.png")
        if os.path.exists(root_stock_img):
            shutil.copy2(root_stock_img, os.path.join(assets_dest, "MFDBCMS.png"))
            success_count += 1
        if os.path.exists(system_assets_dir):
            for item in os.listdir(system_assets_dir):
                s = os.path.join(system_assets_dir, item)
                d = os.path.join(assets_dest, item)
                if os.path.isfile(s):
                    try:
                        shutil.copy2(s, d)
                        success_count += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to copy system asset {item}: {e}")
                        fail_count += 1

        print(f"[ASSETS] Copy complete. Success: {success_count}, Failed: {fail_count}")

    def _get_content_preview(self, html: str, length: int = 120) -> str:
        clean = re.sub('<[^<]+?>', '', html)
        return (clean[:length] + '...') if len(clean) > length else clean

    def _generate_sitemap(self):
        print("Generating sitemap.xml...")
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += f'  <url><loc>{self.base_url}/index.html</loc><priority>1.0</priority></url>\n'
        for url in self.site_urls:
            xml += f'  <url><loc>{self.base_url}/{url}</loc><priority>0.8</priority></url>\n'
        xml += '</urlset>'
        with open(os.path.join(self.output_dir, "sitemap.xml"), "w") as f:
            f.write(xml)

    def _get_random_ad(self, ads: list, zone: str):
        active_zone_ads = [a for a in ads if a.get("zone") == zone]
        if not active_zone_ads: return None
        return self.random.choice(active_zone_ads)

    def _render_page(self, main_content: str, context: dict, rel_prefix: str = "", page_title: str = "", breadcrumbs_html: str = "") -> str:
        page_context = {
            **context, 
            "main_content": main_content, 
            "rel_prefix": rel_prefix,
            "page_title": page_title,
            "breadcrumbs_html": breadcrumbs_html,
            "ad_sidebar": self._get_random_ad(context.get("all_ads", []), "sidebar"),
            "ad_header": self._get_random_ad(context.get("all_ads", []), "header")
        }
        return Template(self.global_skel).render(page_context)

    def _get_all_content_items(self):
        """Collects all pages and apps from all categories, sorted by created_at desc."""
        categories = MFDBCore.mfdb_core_load_entity(self.cms.content_manifest, "Category")
        all_items = []
        
        for cat in categories:
            pages = self.cms.get_pages_in_category(cat["slug"])
            apps = self.cms.get_apps_in_category(cat["slug"])
            
            for p in pages:
                p_data = self.cms.get_full_page_data(p["page_uuid"])
                # Requirement: Always take msdb default image if none assigned
                img = p.get("featured_img")
                if not img or str(img).lower() == "none" or img == "":
                    img = "MFDBCMS.png"

                all_items.append({
                    "title": p["title"],
                    "slug": p["slug"],
                    "cat_slug": cat["slug"],
                    "url": f"{cat['slug']}/{p['slug']}/index.html",
                    "img": img,
                    "desc": self._get_content_preview(p_data.get("html_body", "") if p_data else ""),
                    "type": "page",
                    "page_type": p.get("page_type"),
                    "video_url": p_data.get("video_url") if p_data else None,
                    "created_at": p.get("created_at", ""),
                    "feed_type": cat.get("feed_type", "blog")
                })
            for a in apps:
                img = a.get("featured_img")
                if not img or str(img).lower() == "none" or img == "":
                    img = "MFDBCMS.png"

                all_items.append({
                    "title": a["name"],
                    "slug": a["slug"],
                    "cat_slug": cat["slug"],
                    "url": f"apps/{a['app_uuid']}/{a['entry_file']}",
                    "img": img,
                    "desc": a.get("description", ""),
                    "type": "app",
                    "created_at": a.get("created_at", ""),
                    "feed_type": cat.get("feed_type", "blog")
                })
        
        # Sort by created_at descending
        all_items.sort(key=lambda x: x["created_at"], reverse=True)
        return all_items

    def _generate_item_card_html(self, item: dict, rel_prefix: str = "", force_blog: bool = False) -> str:
        """Generates the HTML for a single content card."""
        # Requirement: Default to default-feature.png
        img = item.get("img")
        if not img or str(img).lower() == "none" or img == "":
            img = "MFDBCMS.png"
        img_url = f"{rel_prefix}assets/{img}"
        
        feed_type = "blog" if force_blog else item.get("feed_type", "blog")
        item_url = f"{rel_prefix}{item['url']}"
        
        # Requirement: If video page, load video onto feed instead of image
        media_tag = f'<img src="{img_url}" class="w-full h-48 object-contain p-4">'
        if item.get("page_type") == "video" and item.get("video_url"):
            v_url = item["video_url"]
            if "youtube.com" in v_url or "youtu.be" in v_url:
                v_id = v_url.split("v=")[-1] if "v=" in v_url else v_url.split("/")[-1]
                media_tag = f'<div class="aspect-video w-full"><iframe class="w-full h-full" src="https://www.youtube.com/embed/{v_id}" frameborder="0" allowfullscreen></iframe></div>'

        if feed_type == "gallery":
            # For gallery, we still prefer image but can swap to video if needed. 
            # Sticking to image for clean grid unless asked otherwise.
            gallery_img = f'<img src="{img_url}" class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500">'
            return f'''<a href="{item_url}" class="group relative aspect-video rounded-xl overflow-hidden border border-brand-surfaceBorder bg-black/40">
                {gallery_img}
                <div class="absolute inset-0 bg-gradient-to-t from-black/90 to-transparent flex items-end p-6">
                    <h3 class="font-bold text-lg">{item["title"]}</h3>
                </div>
            </a>'''
        else:
            img_container = f'<div class="bg-black/40 border-b border-brand-surfaceBorder">{media_tag}</div>'
            type_badge = f'<span class="bg-red-600 text-white text-[8px] font-bold px-2 py-0.5 rounded ml-2">APP</span>' if item["type"] == "app" else ""

            # Format timestamp (Simple slice for brevity)
            ts = item.get("created_at", "")
            if ts and "T" in ts:
                ts = ts.split("T")[0] # Just the date

            ts_tag = f'<span class="text-[10px] text-gray-500 font-mono uppercase tracking-tighter">{ts}</span>' if ts else ""
            btn_text = "LAUNCH APP" if item["type"] == "app" else "VIEW ON FEED"

            return f'''<div class="bg-brand-surface border border-brand-surfaceBorder rounded-xl overflow-hidden flex flex-col hover:border-gray-500 transition-all">
                {img_container}
                <div class="p-6 flex-grow">
                    <div class="mb-2">{ts_tag}</div>
                    <h3 class="font-bold text-xl mb-3 flex items-center"><a href="{item_url}" class="hover:text-brand-red">{item["title"]}</a> {type_badge}</h3>
                    <p class="text-gray-400 text-sm line-clamp-2 mb-6">{item["desc"]}</p>
                </div>
                <div class="px-6 pb-6 mt-auto">
                    <a href="{item_url}" class="text-brand-red text-xs font-bold uppercase tracking-widest hover:underline flex items-center gap-2">
                        {btn_text} <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </a>
                </div>
            </div>'''


    def _build_homepage(self, context: dict):
        with open(os.path.join(self.skel_dir, "Home_Skeleton.html"), "r") as f:
            home_skel = f.read()
        
        all_items = self._get_all_content_items()
        # Take latest 6 items for the homepage grid
        latest_items = all_items[:6]
        
        item_html = ""
        for item in latest_items:
            item_html += self._generate_item_card_html(item, rel_prefix="")

        # Use the first item's image as featured hero if available
        featured_img = None
        for item in latest_items:
            if item.get("img"):
                featured_img = item['img']
                break

        home_content = Template(home_skel).render({
            **context,
            "rel_prefix": "",
            "hero_title": f"Welcome to {context['site_title']}",
            "site_description": context['site_tagline'],
            "latest_items_grid": item_html,
            "featured_hero_img": f"assets/{featured_img}" if featured_img else None
        })
        
        html = self._render_page(home_content, context)
        with open(os.path.join(self.output_dir, "index.html"), "w") as f:
            f.write(html)

    def _build_category(self, cat: dict, context: dict):
        cat_dir = os.path.join(self.output_dir, cat["slug"])
        os.makedirs(cat_dir, exist_ok=True)
        self.site_urls.append(f"{cat['slug']}/index.html")
        
        rel_prefix = "../"
        with open(os.path.join(self.skel_dir, "Category_Feed_Skeleton.html"), "r") as f:
            feed_skel = f.read()
            
        pages = self.cms.get_pages_in_category(cat["slug"])
        apps = self.cms.get_apps_in_category(cat["slug"])
        
        all_items = []
        for p in pages:
            p_data = self.cms.get_full_page_data(p["page_uuid"])
            # Requirement: Always take msdb default image if none assigned
            img = p.get("featured_img")
            if not img or str(img).lower() == "none" or img == "":
                img = "MFDBCMS.png"

            all_items.append({
                "title": p["title"],
                "url": f"{cat['slug']}/{p['slug']}/index.html",
                "img": img,
                "desc": self._get_content_preview(p_data.get("html_body", "") if p_data else ""),
                "type": "page",
                "page_type": p.get("page_type"),
                "video_url": p_data.get("video_url") if p_data else None,
                "created_at": p.get("created_at", ""),
                "feed_type": cat.get("feed_type", "blog")
            })
        for a in apps:
            all_items.append({
                "title": a["name"],
                "url": f"apps/{a['app_uuid']}/{a['entry_file']}",
                "img": a.get("featured_img"),
                "desc": a.get("description", ""),
                "type": "app",
                "created_at": a.get("created_at", ""),
                "feed_type": cat.get("feed_type", "blog")
            })

        item_html = ""
        for item in all_items:
            item_html += self._generate_item_card_html(item, rel_prefix=rel_prefix)

        feed_content = Template(feed_skel).render({
            "category_name": cat["name"],
            "category_description": cat["description"],
            "grid_class": "grid-cols-1 md:grid-cols-3",
            "content_items": item_html,
            "pagination_html": ""
        })
        
        # Generate Breadcrumbs for Category
        bc = f'<a href="{rel_prefix}index.html" class="hover:text-brand-red">HUB</a>'
        bc += f' <span class="opacity-30">/</span> <span class="text-brand-red font-bold">{cat["name"]}</span>'

        html = self._render_page(feed_content, context, rel_prefix=rel_prefix, breadcrumbs_html=bc)
        with open(os.path.join(cat_dir, "index.html"), "w") as f:
            f.write(html)
            
        for p in pages:
            self._build_page(p, cat, context)

    def _build_page(self, page: dict, cat: dict, context: dict):
        page_uuid = page["page_uuid"]
        page_data = self.cms.get_full_page_data(page_uuid)
        page_dir = os.path.join(self.output_dir, cat["slug"], page["slug"])
        os.makedirs(page_dir, exist_ok=True)
        self.site_urls.append(f"{cat['slug']}/{page['slug']}/index.html")
        
        skel_file = "Article_Skeleton.html"
        if page["page_type"] == "video": skel_file = "Video_Skeleton.html"
        elif page["page_type"] == "source-code": skel_file = "SourceCode_Skeleton.html"
        
        with open(os.path.join(self.skel_dir, skel_file), "r") as f:
            page_skel = f.read()
            
        rel_prefix = "../../"
        # Fix relative image paths
        page_data["page_title"] = page_data.get("title")
        
        # Requirement: Fallback to default-feature.png
        feat_img = page_data.get('featured_img')
        if not feat_img or str(feat_img).lower() == "none" or feat_img == "":
            feat_img = "MFDBCMS.png"
            
        page_data["featured_img"] = feat_img
        page_data["featured_img_url"] = f"{rel_prefix}assets/{feat_img}"
        page_data["pdf_url_full"] = f"{rel_prefix}assets/{page_data.get('pdf_url')}" if page_data.get('pdf_url') else None
        page_data["cat_slug"] = cat["slug"]
        
        if page_data.get("author"):
            page_data["author_img_url"] = f"{rel_prefix}assets/{page_data['author'].get('image_url')}" if page_data['author'].get("image_url") else None
        
        related_pages = []
        for rp in self.cms.get_pages_in_category(cat["slug"]):
            if rp["page_uuid"] != page_uuid:
                rp_copy = rp.copy()
                
                # Defensive check for None/Empty
                rp_img = rp.get("featured_img")
                if not rp_img or str(rp_img).lower() == "none" or rp_img == "":
                    rp_img = "MFDBCMS.png"
                    
                rp_copy["featured_img_url"] = f"{rel_prefix}assets/{rp_img}"
                rp_copy["url"] = f"../{rp['slug']}/index.html"
                related_pages.append(rp_copy)

        # Generate Breadcrumbs for Page
        bc = f'<a href="{rel_prefix}index.html" class="hover:text-brand-red">HUB</a>'
        bc += f' <span class="opacity-30">/</span> <a href="../index.html" class="hover:text-brand-red">{cat["name"]}</a>'
        bc += f' <span class="opacity-30">/</span> <span class="text-brand-red font-bold">{page["title"]}</span>'

        page_content = Template(page_skel).render({
            **page_data,
            "rel_prefix": rel_prefix,
            "category_name": cat["name"],
            "related_pages": related_pages
        })

        html = self._render_page(page_content, context, rel_prefix=rel_prefix, page_title=page["title"], breadcrumbs_html=bc)
        with open(os.path.join(page_dir, "index.html"), "w") as f:

            f.write(html)

if __name__ == "__main__":
    builder = MFDB_Builder(
        data_root=os.path.join(PROJECT_ROOT, "Data"),
        skel_dir=os.path.join(PROJECT_ROOT, "HTML_Skeletons"),
        output_dir=os.path.join(PROJECT_ROOT, "Processing", "www")
    )
    builder.build_site()
