"""Flask web app to manage Ideas/Draft, Ideas and Estrategias."""
from __future__ import annotations

import os
import re
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from ideas_core import cleanup, store

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 5001
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_\- ]+$")


def _safe_strategy(name) -> bool:
    return isinstance(name, str) and bool(_SAFE_NAME.match(name))


def _safe_draft(name) -> bool:
    # A plain file name inside Ideas/Draft: no separators, no traversal.
    return (
        isinstance(name, str)
        and name.endswith(".md")
        and Path(name).name == name
        and name not in ("", ".md", "..", ".")
        and ".." not in name
        and "/" not in name
        and "\\" not in name
    )


def create_app(root: Path = REPO_ROOT, llm_client=None) -> Flask:
    root = Path(root)
    app = Flask(__name__)
    app.config["LLM_CLIENT"] = llm_client

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/tree")
    def tree():
        return jsonify(store.list_files(root))

    @app.post("/api/strategy")
    def strategy():
        name = (request.get_json(silent=True) or {}).get("name")
        if not _safe_strategy(name):
            return jsonify(error="invalid strategy name"), 400
        try:
            path = store.create_strategy(root, name)
        except FileExistsError:
            return jsonify(error="strategy already exists"), 409
        return jsonify(strategy=path.name), 201

    @app.post("/api/promote")
    def promote():
        data = request.get_json(silent=True) or {}
        draft, name = data.get("draft"), data.get("strategy")
        if not _safe_draft(draft) or not _safe_strategy(name):
            return jsonify(error="invalid draft or strategy name"), 400
        try:
            target = store.promote_draft(root, draft, name)
        except FileNotFoundError:
            return jsonify(error="draft not found"), 404
        return jsonify(idea=target.name), 201

    @app.post("/api/clean")
    def clean():
        data = request.get_json(silent=True) or {}
        draft, name = data.get("draft"), data.get("strategy")
        if not _safe_draft(draft) or not _safe_strategy(name):
            return jsonify(error="invalid draft or strategy name"), 400
        client = app.config["LLM_CLIENT"]
        if client is None:
            from ideas_core.llm import ClaudeClient
            client = ClaudeClient()
        try:
            target = cleanup.clean_draft(root, draft, name, client)
        except FileNotFoundError:
            return jsonify(error="draft or persona not found"), 404
        except Exception as exc:  # LLM/API failure: draft stays in place
            return jsonify(error=f"cleanup failed: {exc}"), 502
        return jsonify(idea=target.name), 201

    return app


def app_url(port: int = DEFAULT_PORT) -> str:
    return f"http://127.0.0.1:{port}/"


if __name__ == "__main__":
    # debug=True restarts this script in a child process; open the browser only
    # from the parent so it opens once.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.0, webbrowser.open, args=[app_url()]).start()
    create_app().run(debug=True, port=DEFAULT_PORT)
