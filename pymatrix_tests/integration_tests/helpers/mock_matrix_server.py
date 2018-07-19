import http.server
import io
import sys

class StaticResponseHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Returns a static string response with a predetermined HTTP status code.
    """
    status_code = None
    response_body = None

    def setup_response(status_code, response_body):
        StaticResponseHTTPRequestHandler.status_code = status_code
        StaticResponseHTTPRequestHandler.response_body = response_body

    def __init__(self, request, client_address, server):
        if(StaticResponseHTTPRequestHandler.status_code is None
            or StaticResponseHTTPRequestHandler.response_body is None):
            raise Exception("Error no status code or response body")
        super().__init__(request, client_address, server)

    def send_static_response(self):
        self.send_response_only(StaticResponseHTTPRequestHandler.status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(StaticResponseHTTPRequestHandler.response_body \
            .encode(sys.getfilesystemencoding()))


    def do_GET(self):
        self.send_static_response()
    def do_POST(self):
        self.send_static_response()
    def do_PUT(self):
        self.send_static_response()
    def do_DELETE(self):
        self.send_static_response()
