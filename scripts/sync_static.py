import os
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sync():
    index_path = os.path.join(ROOT_DIR, "index.html")
    style_path = os.path.join(ROOT_DIR, "style.css")
    app_path = os.path.join(ROOT_DIR, "app.js")

    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    with open(style_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    with open(app_path, "r", encoding="utf-8") as f:
        js_content = f.read()

    # 1. Update backend/app/static_content.py
    static_py_path = os.path.join(ROOT_DIR, "backend", "app", "static_content.py")
    with open(static_py_path, "w", encoding="utf-8") as f:
        f.write("# Auto-generated embedded static content for Vercel\n")
        f.write(f"INDEX_HTML = {repr(html_content)}\n")
        f.write(f"STYLE_CSS = {repr(css_content)}\n")
        f.write(f"APP_JS = {repr(js_content)}\n")
    print("Updated backend/app/static_content.py")

    # 2. Copy to public/
    public_dir = os.path.join(ROOT_DIR, "public")
    if os.path.exists(public_dir):
        shutil.copy2(index_path, os.path.join(public_dir, "index.html"))
        shutil.copy2(style_path, os.path.join(public_dir, "style.css"))
        shutil.copy2(app_path, os.path.join(public_dir, "app.js"))
        print("Updated public/ files")

    # 3. Copy to frontend/
    frontend_dir = os.path.join(ROOT_DIR, "frontend")
    if os.path.exists(frontend_dir):
        shutil.copy2(index_path, os.path.join(frontend_dir, "index.html"))
        shutil.copy2(style_path, os.path.join(frontend_dir, "style.css"))
        shutil.copy2(app_path, os.path.join(frontend_dir, "app.js"))
        print("Updated frontend/ files")

    # 4. Copy to backend/app/static/
    static_dir = os.path.join(ROOT_DIR, "backend", "app", "static")
    if os.path.exists(static_dir):
        shutil.copy2(index_path, os.path.join(static_dir, "index.html"))
        shutil.copy2(style_path, os.path.join(static_dir, "style.css"))
        shutil.copy2(app_path, os.path.join(static_dir, "app.js"))
        print("Updated backend/app/static/ files")

if __name__ == "__main__":
    sync()
