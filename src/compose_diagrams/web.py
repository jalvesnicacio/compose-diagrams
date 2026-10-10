import tempfile
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from werkzeug.serving import make_server

from . import DIRECTIONS, FORMATS, STYLES, ComposeError, load, render_data

STATIC = Path(__file__).parent / "static"


def create_app(initial_compose=""):
    app = Flask(__name__, static_folder=None)

    @app.get("/")
    def index():
        return send_file(STATIC / "index.html")

    @app.get("/initial")
    def initial():
        return jsonify(compose=initial_compose)

    @app.post("/render")
    def render():
        body = request.get_json(silent=True) or {}
        outformat = body.get("format", "svg")
        direction = body.get("direction", "TB")
        style = body.get("style", "ad-hoc")
        if outformat not in FORMATS or direction not in DIRECTIONS or style not in STYLES:
            return jsonify(error="unsupported format, direction or style"), 400
        try:
            data = load(body.get("compose", ""))
        except ComposeError as e:
            return jsonify(error=str(e)), 400

        with tempfile.TemporaryDirectory() as tmp:
            try:
                image, _ = render_data(data, Path(tmp) / "diagram", outformat, direction, style)
            except Exception as e:
                # the file parsed, but has a shape the diagram builder does not handle yet
                return jsonify(error="could not draw this file: " + (str(e) or type(e).__name__)), 422
            content = image.read_bytes()
        response = app.response_class(content, mimetype=_MIMETYPES[outformat])
        if body.get("download"):
            response.headers["Content-Disposition"] = 'attachment; filename="diagram.' + outformat + '"'
        return response

    return app


_MIMETYPES = {
    "png": "image/png",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
    "jpg": "image/jpeg",
}


def serve(host="127.0.0.1", port=8000, initial_compose="", open_browser=True):
    server = make_server(host, port, create_app(initial_compose), threaded=True)
    url = "http://" + host + ":" + str(port)
    print("compose-diagrams is running at " + url + " (Ctrl+C to stop)")
    if open_browser:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
