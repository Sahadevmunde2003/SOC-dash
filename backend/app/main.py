"""Sentinel SOC REST API. Demo-only in-memory store; use auth and persistence before deployment."""
from flask import Flask, jsonify, request
from flask_cors import CORS
from app.data import ALERTS, get_alerts, summary

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
VALID_STATUSES = {"New", "Investigating", "Contained", "Closed", "False Positive"}

@app.get("/api/health")
def health():
    return jsonify({"status":"ok", "service":"sentinel-soc-api", "mode":"demo"})

@app.get("/api/summary")
def dashboard_summary():
    return jsonify(summary())

@app.get("/api/alerts")
def alerts():
    return jsonify({"items":get_alerts(request.args.get("q", ""), request.args.get("severity", "All"), request.args.get("status", "All")), "count":len(get_alerts(request.args.get("q", ""), request.args.get("severity", "All"), request.args.get("status", "All")))})

@app.get("/api/alerts/<alert_id>")
def alert_detail(alert_id):
    item = next((a for a in ALERTS if a["id"] == alert_id), None)
    if not item:
        return jsonify({"error":"alert_not_found"}), 404
    return jsonify(item)

@app.patch("/api/alerts/<alert_id>/status")
def update_status(alert_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in VALID_STATUSES:
        return jsonify({"error":"invalid_status", "allowed":sorted(VALID_STATUSES)}), 400
    item = next((a for a in ALERTS if a["id"] == alert_id), None)
    if not item:
        return jsonify({"error":"alert_not_found"}), 404
    item["status"] = status
    if payload.get("note"):
        item.setdefault("analyst_notes", []).append(str(payload["note"])[:1000])
    return jsonify(item)

@app.post("/api/events")
def ingest_event():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error":"expected_json_object"}), 400
    required = ["title", "severity", "source"]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        return jsonify({"error":"missing_fields", "fields":missing}), 400
    if payload["severity"] not in {"Critical", "High", "Medium", "Low"}:
        return jsonify({"error":"invalid_severity"}), 400
    import uuid
    item = {"id":"SOC-" + uuid.uuid4().hex[:8].upper(), "title":str(payload["title"])[:200], "severity":payload["severity"], "status":"New", "source":str(payload["source"])[:100], "src_ip":str(payload.get("src_ip", "unknown"))[:64], "dst_ip":str(payload.get("dst_ip", "unknown"))[:64], "timestamp":str(payload.get("timestamp", "")) or __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "technique":str(payload.get("technique", "Unmapped"))[:30], "technique_name":str(payload.get("technique_name", "Unmapped"))[:100], "description":str(payload.get("description", "Ingested lab event"))[:1000], "evidence":payload.get("evidence", []) if isinstance(payload.get("evidence", []), list) else []}
    ALERTS.insert(0, item)
    return jsonify(item), 201

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
