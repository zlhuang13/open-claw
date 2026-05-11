#!/usr/bin/env python3
"""UMI Dashboard - modular server."""
import http.server
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates', 'base.html')
CSS_PATH = os.path.join(BASE_DIR, 'static', 'style.css')
PHOTOS_DIR = os.path.join(BASE_DIR, '..', '..', 'photos')
CAT_PHOTOS_DIR = os.path.join(BASE_DIR, '..', '..', 'data', 'cat_photos')
STATIC_MAP = {
    '/style.css': (CSS_PATH, 'text/css'),
}

BIND = '100.86.143.43'
PORT = 80

# Load modules
from modules import discover_modules
modules = discover_modules(MODULES_DIR)
route_map = {}
for m in modules:
    route_map[m.ROUTE] = m

# Load base template
with open(TEMPLATE_PATH) as f:
    BASE_TEMPLATE = f.read()


def wrap(title, nav_html, content_html):
    return (BASE_TEMPLATE
            .replace('{{title}}', title)
            .replace('{{nav}}', nav_html)
            .replace('{{content}}', content_html))


def index_html():
    cards = ""
    for m in modules:
        if m.is_enabled():
            cards += f'''<div class="module-card" onclick="window.location.href='{m.ROUTE}'">
                <div class="module-icon">{m.ICON}</div>
                <h3>{m.TITLE.split(' ', 1)[-1]}</h3>
                <p>{m.DESCRIPTION}</p>
            </div>'''
        else:
            cards += f'''<div class="module-card disabled">
                <div class="module-icon">{m.ICON}</div>
                <h3>{m.TITLE.split(' ', 1)[-1]}</h3>
                <p>{m.DESCRIPTION}</p>
                <span class="badge">Coming Soon</span>
            </div>'''
    nav_html = '<span>🤍 UMI Dashboard</span>'
    return wrap('🤍 UMI Dashboard', nav_html,
                f'<h1>🤍 UMI</h1><p class="subtitle">Home Butler Dashboard</p><div class="module-grid">{cards}</div>')


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]

        if path in STATIC_MAP:
            fpath, ct = STATIC_MAP[path]
            with open(fpath, 'rb') as f:
                data = f.read()
        elif path.startswith('/photos/'):
            # Serve plant photos: /photos/P001/file.jpg
            rel = path[len('/photos/'):]
            fpath = os.path.join(PHOTOS_DIR, rel)
            if '..' in rel or not os.path.isfile(fpath):
                self.send_error(404)
                return
            ext = os.path.splitext(fpath)[1].lower()
            ct = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}.get(ext.lstrip('.'), 'application/octet-stream')
            with open(fpath, 'rb') as f:
                data = f.read()
        elif path.startswith('/cat-photos/'):
            rel = path[len('/cat-photos/'):]
            fpath = os.path.join(CAT_PHOTOS_DIR, rel)
            if '..' in rel or not os.path.isfile(fpath):
                self.send_error(404)
                return
            ext = os.path.splitext(fpath)[1].lower()
            ct = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}.get(ext.lstrip('.'), 'application/octet-stream')
            with open(fpath, 'rb') as f:
                data = f.read()
        elif path == '/cats/weight-chart.png':
            m = route_map.get('/cats')
            if not m:
                self.send_error(404)
                return
            if hasattr(m, 'set_request_query'):
                m.set_request_query(self.path.split('?', 1)[1] if '?' in self.path else '')
            data = m.render_weight_chart()
            if not data:
                self.send_error(404)
                return
            ct = 'image/png'
        elif path.startswith('/api/'):
            module_route = '/' + path[len('/api/'):]
            m = route_map.get(module_route)
            if not m or not hasattr(m, 'render_json'):
                self.send_error(404)
                return
            if hasattr(m, 'set_request_query'):
                m.set_request_query(self.path.split('?', 1)[1] if '?' in self.path else '')
            data = m.render_json()
            ct = 'application/json'
        elif path in route_map:
            m = route_map[path]
            if hasattr(m, 'set_request_query'):
                m.set_request_query(self.path.split('?', 1)[1] if '?' in self.path else '')
            data = wrap(m.TITLE, m.nav(), m.render()).encode('utf-8')
            ct = 'text/html'
        else:
            data = index_html().encode('utf-8')
            ct = 'text/html'

        self.send_response(200)
        if ct.startswith('text/'):
            self.send_header('Content-Type', f'{ct}; charset=utf-8')
        else:
            self.send_header('Content-Type', ct)
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    print(f'🤍 UMI Dashboard on http://{BIND}/')
    print(f'   Modules: {", ".join(m.ROUTE for m in modules)}')
    http.server.HTTPServer((BIND, PORT), Handler).serve_forever()
