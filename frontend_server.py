from http.server import HTTPServer, SimpleHTTPRequestHandler


class FrontendHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
    }


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8001), FrontendHandler)

    print("Forewalk Games frontend running at http://127.0.0.1:8001")

    server.serve_forever()