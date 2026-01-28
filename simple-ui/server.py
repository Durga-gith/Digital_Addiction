import http.server
import socketserver
import webbrowser
import threading
import time

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f" Frontend server running at: http://localhost:{PORT}")
    print(f" Your backend should be at: http://localhost:8000")
    print("\nOpen your browser to: http://localhost:8080")
    
    def open_browser():
        time.sleep(1)
        webbrowser.open(f'http://localhost:{PORT}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")