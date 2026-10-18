"""Terminal client for the Sentinel SOC demo API."""
import argparse, json, urllib.error, urllib.parse, urllib.request
BASE = "http://127.0.0.1:5000/api"
def call(path, method="GET", payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            print(json.dumps(json.load(response), indent=2))
    except urllib.error.URLError as exc:
        raise SystemExit(f"API unavailable: {exc}. Start Flask with: python -m app.main")
def main():
    parser = argparse.ArgumentParser(description="Sentinel SOC CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health")
    alerts = sub.add_parser("alerts"); alerts.add_argument("--query", default="")
    status = sub.add_parser("status"); status.add_argument("alert_id"); status.add_argument("status", choices=["New", "Investigating", "Contained", "Closed", "False Positive"])
    ingest = sub.add_parser("ingest"); ingest.add_argument("--title", required=True); ingest.add_argument("--severity", choices=["Critical", "High", "Medium", "Low"], required=True); ingest.add_argument("--source", required=True); ingest.add_argument("--src-ip", default="unknown"); ingest.add_argument("--dst-ip", default="unknown")
    args = parser.parse_args()
    if args.cmd == "health": call("/health")
    elif args.cmd == "alerts": call("/alerts?q=" + urllib.parse.quote(args.query))
    elif args.cmd == "status": call("/alerts/" + args.alert_id + "/status", "PATCH", {"status":args.status})
    elif args.cmd == "ingest": call("/events", "POST", {"title":args.title,"severity":args.severity,"source":args.source,"src_ip":args.src_ip,"dst_ip":args.dst_ip})
if __name__ == "__main__": main()
