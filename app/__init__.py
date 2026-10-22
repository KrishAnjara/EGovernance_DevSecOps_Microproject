"""Academic simulation: e-governance citizen services portal (Flask + SQLite)."""
import os
import re
import secrets
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, render_template, request

from .data import COMPARISON, MODELS, SERVICES, STATUS_STEPS, admin_summary

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
REF_RE = re.compile(r"^SIM-[0-9A-F]{8}$")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        DB_PATH=os.environ.get("DB_PATH", os.path.join("data", "app.db")),
        STATUS_STEP_SECONDS=int(os.environ.get("STATUS_STEP_SECONDS", "20")),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    db_dir = os.path.dirname(app.config["DB_PATH"])
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with sqlite3.connect(app.config["DB_PATH"]) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS applications ("
                     "ref TEXT PRIMARY KEY, service TEXT NOT NULL, alias TEXT NOT NULL,"
                     "details TEXT NOT NULL, created_at TEXT NOT NULL)")

    @app.after_request
    def security_headers(resp):
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'self'")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok")

    @app.get("/api/models")
    def api_models():
        return jsonify(models=MODELS, comparison=COMPARISON)

    @app.get("/api/services")
    def api_services():
        return jsonify(services=SERVICES)

    @app.post("/api/applications")
    def create_application():
        body = request.get_json(silent=True) or {}
        service = str(body.get("service", ""))
        alias = str(body.get("alias", "")).strip()
        details = str(body.get("details", "")).strip()
        errors = {}
        if service not in {s["id"] for s in SERVICES}:
            errors["service"] = "Choose a service from the list."
        if not 2 <= len(alias) <= 40:
            errors["alias"] = "Use a made-up nickname of 2 to 40 characters."
        if len(details) > 300:
            errors["details"] = "Keep details under 300 characters."
        combined = f"{alias} {details}"
        if EMAIL_RE.search(combined) or len(re.sub(r"\D", "", combined)) >= 9:
            errors["details"] = ("This is a simulation. Remove email addresses and long "
                                 "numbers; never enter real personal data.")
        if errors:
            return jsonify(errors=errors), 400
        ref = "SIM-" + secrets.token_hex(4).upper()
        now = datetime.now(timezone.utc).isoformat()
        db = get_db()
        db.execute("INSERT INTO applications VALUES (?,?,?,?,?)",
                   (ref, service, alias, details, now))
        db.commit()
        return jsonify(ref=ref, status=STATUS_STEPS[0]), 201

    @app.get("/api/applications/<ref>")
    def get_application(ref):
        if not REF_RE.match(ref):
            return jsonify(error="Reference must look like SIM-XXXXXXXX."), 400
        row = get_db().execute("SELECT * FROM applications WHERE ref=?", (ref,)).fetchone()
        if row is None:
            return jsonify(error="No simulated application with that reference."), 404
        created = datetime.fromisoformat(row["created_at"])
        elapsed = (datetime.now(timezone.utc) - created).total_seconds()
        step = min(int(elapsed // max(app.config["STATUS_STEP_SECONDS"], 1)),
                   len(STATUS_STEPS) - 1)
        return jsonify(ref=row["ref"], service=row["service"], submitted=row["created_at"],
                       status=STATUS_STEPS[step], step=step, steps=STATUS_STEPS)

    @app.get("/api/admin/summary")
    def api_admin_summary():
        return jsonify(admin_summary())

    return app
