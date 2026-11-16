#!/usr/bin/env python3
"""
Local-First Second Brain Server
Built with Python Standard Library (http.server, json, re, os, urllib)
Zero external dependencies.
"""

import http.server
import socketserver
import os
import json
import re
import urllib.parse
from datetime import datetime

PORT = 8000
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTES_DIR = os.path.join(BASE_DIR, "notes")
SRC_DIR = os.path.abspath(os.path.dirname(__file__))

PARA_CATEGORIES = ["Inbox", "Projects", "Areas", "Resources", "Archives"]

def parse_markdown_note(file_path, category):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return None

    filename = os.path.basename(file_path)
    frontmatter_match = re.match(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$", content)

    metadata = {}
    body = content

    if frontmatter_match:
        yaml_text = frontmatter_match.group(1)
        body = frontmatter_match.group(2).strip()

        current_array_key = None
        for line in yaml_text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if line_str.startswith("- ") and current_array_key:
                val = line_str[2:].strip().strip("\"'")
                metadata.setdefault(current_array_key, []).append(val)
                continue
            if ":" in line_str:
                key, val = line_str.split(":", 1)
                key = key.strip()
                val = val.strip()
                if not val:
                    current_array_key = key
                    metadata[key] = []
                else:
                    current_array_key = None
                    if val.startswith("[") and val.endswith("]"):
                        items = [s.strip().strip("\"'") for s in val[1:-1].split(",")]
                        metadata[key] = items
                    else:
                        metadata[key] = val.strip("\"'")

    title = metadata.get("title", os.path.splitext(filename)[0])
    stat = os.stat(file_path)
    created = metadata.get("created", datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"))
    updated = metadata.get("updated", datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

    return {
        "id": f"srv-{abs(hash(file_path)) % 10000000}",
        "filename": filename,
        "category": category,
        "title": title,
        "created": created,
        "updated": updated,
        "tags": metadata.get("tags", []),
        "status": metadata.get("status", "active"),
        "type": metadata.get("type", "note"),
        "source": metadata.get("source", ""),
        "content": body
    }

def get_all_notes():
    notes = []
    for cat in PARA_CATEGORIES:
        cat_dir = os.path.join(NOTES_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        for fname in os.listdir(cat_dir):
            if fname.endswith(".md") or fname.endswith(".markdown"):
                full_path = os.path.join(cat_dir, fname)
                parsed = parse_markdown_note(full_path, cat)
                if parsed:
                    notes.append(parsed)
    # Sort notes by updated date descending
    notes.sort(key=lambda x: str(x.get("updated", "")), reverse=True)
    return notes

class SecondBrainHandler(http.server.BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        response_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def serve_static_file(self, file_path, content_type):
        if not os.path.exists(file_path):
            self.send_error(404, "File Not Found")
            return
        with open(file_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path in ["/", "/index.html"]:
            self.serve_static_file(os.path.join(SRC_DIR, "index.html"), "text/html")
        elif path == "/styles.css":
            self.serve_static_file(os.path.join(SRC_DIR, "styles.css"), "text/css")
        elif path == "/app.js":
            self.serve_static_file(os.path.join(SRC_DIR, "app.js"), "application/javascript")
        elif path == "/api/notes":
            notes = get_all_notes()
            self.send_json({"count": len(notes), "notes": notes})
        elif path == "/api/search":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            q = query_params.get("q", [""])[0].lower()
            all_notes = get_all_notes()
            filtered = [
                n for n in all_notes
                if q in n["title"].lower() or q in n["content"].lower() or any(q in t.lower() for t in n["tags"])
            ]
            self.send_json({"query": q, "count": len(filtered), "notes": filtered})
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/api/notes":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                self.send_json({"error": "Invalid JSON"}, status=400)
                return

            title = data.get("title", "").strip()
            if not title:
                self.send_json({"error": "Title is required"}, status=400)
                return

            category = data.get("category", "Inbox")
            if category not in PARA_CATEGORIES:
                category = "Inbox"

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tags = data.get("tags", [])
            status = data.get("status", "draft")
            note_type = data.get("type", "fleeting")
            source = data.get("source", "власні думки")
            content = data.get("content", "")

            # Формування YAML Frontmatter + Markdown
            yaml_lines = [
                "---",
                f'title: "{title}"',
                f'created: "{now_str}"',
                f'updated: "{now_str}"',
                "tags:"
            ]
            for t in tags:
                yaml_lines.append(f'  - "{t}"')
            yaml_lines.extend([
                f'status: "{status}"',
                f'type: "{note_type}"',
                f'source: "{source}"',
                "---",
                "",
                content
            ])

            full_text = "\n".join(yaml_lines)
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
            target_file = os.path.join(NOTES_DIR, category, f"{safe_title}.md")

            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(full_text)

            created_note = parse_markdown_note(target_file, category)
            self.send_json({"success": True, "note": created_note}, status=201)
        else:
            self.send_error(404, "Not Found")

def run(port=PORT):
    server_address = ("127.0.0.1", port)
    httpd = socketserver.TCPServer(server_address, SecondBrainHandler)
    print(f"🧠 Second Brain server running at http://127.0.0.1:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run()
