import http.server
import socketserver
import json
import os
import sys

sys.path.insert(0, "/tmp/feedback-server/pgserver")

import psycopg2

DB_CONFIG = {
    "database": "tokyiskayashiza",
    "user": "tokyiskayashiza"
}

PORT = 8029

class Handler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_POST(self):
        if self.path == "/feedback":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                name = data.get("name", "Аноним")
                message = data.get("message", "")

                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO feedbacks (name, message) VALUES (%s, %s);",
                    (name, message)
                )
                conn.commit()
                cursor.close()
                conn.close()

                self._set_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

            except Exception as e:
                print("Ошибка:", e)
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Running at http://0.0.0.0:{PORT}")
    httpd.serve_forever()
