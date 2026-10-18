"""Synthetic SOC events for local portfolio demonstrations."""
from datetime import datetime, timezone

ALERTS = [
    {"id":"SOC-2026-1042","title":"Repeated SSH authentication failures","severity":"High","status":"New","source":"Ubuntu auth","src_ip":"192.0.2.24","dst_ip":"10.10.20.10","timestamp":"2026-10-18T13:02:00Z","technique":"T1110","technique_name":"Brute Force","description":"Multiple failed SSH logins observed in the sample authentication log.","evidence":["8 failed login attempts in 2 minutes","Account: labuser","Sensor: ubuntu-dmz"]},
    {"id":"SOC-2026-1043","title":"Suspicious phishing URL","severity":"Critical","status":"Investigating","source":"Email analysis","src_ip":"198.51.100.18","dst_ip":"10.10.10.25","timestamp":"2026-10-18T12:44:00Z","technique":"T1566.002","technique_name":"Spearphishing Link","description":"A sample email contains a mismatched sender display name and an obfuscated URL.","evidence":["SPF: fail (sample result)","URL host differs from displayed link","IOC reputation: not checked"]},
    {"id":"SOC-2026-1044","title":"Unusual outbound connection","severity":"Medium","status":"New","source":"pfSense firewall","src_ip":"10.10.20.15","dst_ip":"203.0.113.42","timestamp":"2026-10-18T12:18:00Z","technique":"T1071.001","technique_name":"Web Protocols","description":"A synthetic firewall event records an outbound HTTPS connection requiring analyst review.","evidence":["Protocol: TCP","Destination port: 443","Disposition: pass"]},
    {"id":"SOC-2026-1045","title":"Multiple blocked inbound probes","severity":"Low","status":"Closed","source":"pfSense firewall","src_ip":"198.51.100.77","dst_ip":"10.10.20.10","timestamp":"2026-10-18T11:58:00Z","technique":"T1046","technique_name":"Network Service Discovery","description":"Sample firewall records show several blocked connection attempts.","evidence":["Action: block","Destination ports: 22, 80, 443","No confirmed compromise"]},
    {"id":"SOC-2026-1046","title":"New admin group membership","severity":"High","status":"Investigating","source":"Endpoint sample","src_ip":"10.10.20.21","dst_ip":"10.10.20.21","timestamp":"2026-10-18T10:36:00Z","technique":"T1098","technique_name":"Account Manipulation","description":"Simulated endpoint event indicates a privileged group membership change.","evidence":["Event type: group membership change","Host: lab-windows-01","User: demo-admin"]}
]

def get_alerts(query="", severity="All", status="All"):
    result = ALERTS
    if query:
        q = query.casefold()
        result = [a for a in result if q in " ".join(str(v) for v in a.values()).casefold()]
    if severity != "All":
        result = [a for a in result if a["severity"] == severity]
    if status != "All":
        result = [a for a in result if a["status"] == status]
    return sorted(result, key=lambda a: a["timestamp"], reverse=True)

def summary():
    severities = {s: sum(1 for a in ALERTS if a["severity"] == s) for s in ["Critical", "High", "Medium", "Low"]}
    return {"total_alerts": len(ALERTS), "open_incidents": sum(a["status"] != "Closed" for a in ALERTS), "critical_alerts": severities["Critical"], "investigating": sum(a["status"] == "Investigating" for a in ALERTS), "severity_counts": severities, "source":"synthetic demo data", "updated_at":datetime.now(timezone.utc).isoformat()}
