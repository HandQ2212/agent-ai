"""Local web server for Agent 02; run `python3 code_web/server.py`.
Uses the actual Python agents and saved experiment artifacts, no fake API data.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import mimetypes
from pathlib import Path
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROJECT = Path(__file__).resolve().parents[1]
WEB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT / 'code_agent' / 'tutorial'))
from mas_system import Coordinator, PRODUCTS, STOCK

SCENARIOS = {'normal', 'timeout', 'malformed', 'stale', 'forged'}
PRODUCTS_BY_ID = {p.id: p for p in PRODUCTS}


def read_json(path):
    with path.open(encoding='utf-8') as file:
        return json.load(file)


def overview():
    intent = read_json(PROJECT / 'ket_qua/tutorial/intent_metrics.json')
    mas = read_json(PROJECT / 'ket_qua/tutorial/mas_metrics.json')
    assignment = read_json(PROJECT / 'ket_qua/assignment/summary.json')
    return {
        'catalog_count': len(PRODUCTS),
        'intent': {key: intent[key] for key in ('accuracy', 'macro_f1', 'splits', 'threshold', 'confusion_matrix')},
        'mas': mas['summary'],
        'assignment': assignment['aggregates'],
        'seeds': assignment['seeds'],
        'episodes': assignment['config']['episodes'],
    }


def catalog():
    return [{'id': p.id, 'name': p.name, 'category': p.category,
             'price': p.price, 'tags': list(p.tags), 'stock': STOCK[p.id]} for p in PRODUCTS]


def recommend(payload):
    if not isinstance(payload, dict):
        raise ValueError('Dữ liệu yêu cầu phải là JSON object.')
    query = payload.get('query')
    budget = payload.get('budget')
    scenario = payload.get('scenario', 'normal')
    if not isinstance(query, str) or len(query) > 100:
        raise ValueError('Từ khóa phải là chuỗi không quá 100 ký tự.')
    if isinstance(budget, bool) or not isinstance(budget, (int, float)):
        raise ValueError('Ngân sách phải là một số không âm.')
    if not isinstance(scenario, str) or scenario not in SCENARIOS:
        raise ValueError('Kịch bản không hợp lệ.')
    # A fresh coordinator per request keeps traces isolated across clients.
    coordinator = Coordinator(deadline=.01)
    result = asyncio.run(coordinator.shop(query, budget, scenario, task_id='web-request'))
    items = []
    for row in result['items']:
        product = PRODUCTS_BY_ID[row['id']]
        items.append({**row, 'name': product.name, 'category': product.category,
                      'tags': list(product.tags), 'stock': STOCK[product.id]})
    return {'status': result['status'], 'items': items, 'trace': coordinator.trace}


def classify(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('text'), str):
        raise ValueError('Yêu cầu phải chứa trường text dạng chuỗi.')
    text = payload['text'].strip()
    if not text or len(text) > 500:
        raise ValueError('Nhập nội dung từ 1 đến 500 ký tự.')
    # Load only when the classifier is requested; shopping demo needs no torch.
    from train_intent import Router
    return Router(PROJECT / 'ket_qua/tutorial').route(text)


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            path = self.path.split('?', 1)[0]
            if path == '/api/overview':
                return self.send_json(200, overview())
            if path == '/api/catalog':
                return self.send_json(200, catalog())
            static = {'/': 'index.html', '/index.html': 'index.html',
                      '/styles.css': 'styles.css', '/app.js': 'app.js'}
            if path not in static:
                return self.send_json(404, {'error': 'Không tìm thấy đường dẫn.'})
            file = WEB_DIR / static[path]
            body = file.read_bytes()
            content_type = mimetypes.guess_type(str(file))[0] or 'application/octet-stream'
            self.send_response(200)
            self.send_header('Content-Type', content_type + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (OSError, ValueError, KeyError) as exc:
            self.send_json(500, {'error': 'Không thể đọc dữ liệu dự án.', 'detail': str(exc)})

    def do_POST(self):
        if self.path not in ('/api/recommend', '/api/intent'):
            return self.send_json(404, {'error': 'Không tìm thấy đường dẫn.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 16384:
                raise ValueError('Kích thước yêu cầu không hợp lệ.')
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
            result = recommend(payload) if self.path == '/api/recommend' else classify(payload)
            return self.send_json(200, result)
        except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
            return self.send_json(400, {'error': str(exc)})
        except (OSError, ImportError) as exc:
            return self.send_json(500, {'error': 'Không thể chạy thành phần agent.', 'detail': str(exc)})


def main():
    parser = argparse.ArgumentParser(description='Chạy web demo Agent 02')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'Agent 02 đang chạy tại http://{args.host}:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
