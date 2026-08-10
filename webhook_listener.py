import subprocess
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook received. Triggering collectors...\n")
        
        print("Webhook triggered! Running collectors in the background...")
        script_path = os.path.join(os.path.dirname(__file__), "run_all_collectors.py")
        # Popen runs it asynchronously so the webhook returns immediately
        subprocess.Popen([sys.executable, script_path])

if __name__ == "__main__":
    port = 8001
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"Listening for n8n webhooks on http://localhost:{port} ...")
    server.serve_forever()
