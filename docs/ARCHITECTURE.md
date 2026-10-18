# Architecture

## Milestone 1 data flow

1. The React + Vite single-page app requests dashboard summary and alerts from the Flask REST API.
2. Flask validates query parameters and returns normalized alert objects.
3. The UI supports triage filters, investigation details, ATT&CK technique references, and case status changes.
4. The Python CLI uses the same REST endpoints for terminal workflows.
5. The demo API keeps alerts in process memory. Restarting Flask resets changes.

## Normalized alert schema

| Field | Purpose |
|---|---|
| id | Stable case/alert identifier |
| title | Human-readable detection name |
| severity | Critical, High, Medium, or Low |
| status | New, Investigating, Contained, Closed, or False Positive |
| source | Log source / sensor name |
| src_ip / dst_ip | Observed source and destination |
| timestamp | Event time in ISO-8601 format |
| technique / technique_name | Optional MITRE ATT&CK mapping |
| description | Detection rationale / analyst context |
| evidence | List of evidence statements |

## Planned telemetry path

```text
pfSense firewall export ─┐
Ubuntu auth logs ────────┼─> parsers -> normalized events -> detection rules
Zeek / Suricata ─────────┘                              │
                                                       v
                                      persistent events + incidents
                                                       │
                                                       v
                                             Flask API -> React UI
```

## Security boundaries

- Bind the development API to loopback by default.
- Do not expose this demo API to the public internet without authentication, authorization, rate limiting, input validation, and production deployment configuration.
- Treat all ingested logs as untrusted input.
- Store credentials and API tokens in environment variables; never commit them.
- Only collect telemetry from systems you own or are authorized to monitor.
