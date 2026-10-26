# Sentinel SOC

A portfolio-grade Security Operations Center (SOC) dashboard built with React + Vite and Flask. The MVP includes a dark SIEM-style analyst console, REST API, synthetic alerts, incident status workflow, terminal CLI, and raw lab telemetry parsers for Ubuntu SSH authentication logs and pfSense JSONL exports.

> **Lab/demo notice:** included alerts and indicators are synthetic. This is not a production SIEM and does not claim live monitoring. Raw telemetry must be submitted to the local API; the project does not currently tail remote hosts or connect directly to pfSense.

## Features

- Security overview: alert counts, severity distribution, and alert activity.
- Alert triage: search, severity/source filters, and investigation details.
- Incident workflow: update case status and add analyst notes.
- Flask API for health, summaries, alerts, status updates, normalized event ingestion, and raw lab-log ingestion.
- Ubuntu auth.log parser for SSH failed/successful login events.
- pfSense JSONL parser with timestamp, IP address, and action validation.
- Starter detections for SSH authentication bursts and repeated firewall blocks.
- Per-line parser errors returned alongside successfully parsed records.
- Python CLI for terminal-based health checks, alert searches, status updates, and normalized event ingestion.
- Sample pfSense-style JSONL events and Ubuntu authentication log fixtures.
- Pytest-compatible API and telemetry parser tests.

## Architecture

\`\`\`text
React + Vite (5173)
       │ REST / JSON
       ▼
Flask API (5000) ─── In-memory demo alert store
       ▲
       ├── Python SOC CLI
       ├── Ubuntu auth.log text ingestion
       └── pfSense JSONL ingestion
\`\`\`

## Repository layout

\`\`\`text
SOC-dash/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── data.py
│   │   ├── main.py
│   │   └── telemetry.py
│   ├── data/
│   │   ├── sample-auth.log
│   │   └── sample-pfsense.jsonl
│   ├── tests/
│   ├── requirements.txt
│   └── socctl.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DETECTION-RULES.md
│   ├── ROADMAP.md
│   ├── RUNNING-KALI-WINDOWS.md
│   └── TELEMETRY-INGESTION.md
└── .github/workflows/ci.yml
\`\`\`

## Requirements

- Python 3.10+
- Node.js 18+ and npm

## Run locally

**Platform-specific setup:** follow [docs/RUNNING-KALI-WINDOWS.md](docs/RUNNING-KALI-WINDOWS.md) for step-by-step instructions for both Kali Linux and Windows PowerShell, including installation checks, virtual environment setup, starting the backend and frontend in separate terminals, sample telemetry ingestion, CLI usage, tests, and troubleshooting.

Quick start after cloning the repository:

1. Start the Flask backend from the `backend/` directory: create and activate a Python virtual environment, install `requirements.txt`, then run `python -m app.main`.
2. In a second terminal, start the frontend from `frontend/` with `npm install` and `npm run dev`.
3. Open http://127.0.0.1:5173 and verify the API at http://127.0.0.1:5000/api/health.

The activation command differs by platform; use the linked guide rather than copying the Linux-only commands into Windows PowerShell.

## Raw telemetry ingestion

Both endpoints accept JSON with a content string. They return parsed events, per-line errors, and detections; detections are inserted into the current in-memory alert list.

### Ubuntu SSH authentication log

\`\`\`bash
curl -X POST http://127.0.0.1:5000/api/ingest/auth-log \\
  -H 'Content-Type: application/json' \\
  --data-binary "$(python -c 'import json; print(json.dumps({"content": open("backend/data/sample-auth.log").read()}))')"
\`\`\`

The starter rule SSH-BRUTE-001 flags five or more failed SSH logins from one source IP within 120 seconds.

### pfSense JSONL

\`\`\`bash
curl -X POST http://127.0.0.1:5000/api/ingest/pfsense \\
  -H 'Content-Type: application/json' \\
  --data-binary "$(python -c 'import json; print(json.dumps({"content": open("backend/data/sample-pfsense.jsonl").read()}))')"
\`\`\`

The parser requires an ISO-8601 timestamp, valid source/destination IP addresses, and an action of pass, block, or reject. The starter rule PFSENSE-DENY-BURST-001 flags five or more blocked/rejected records from one source in the submitted batch.

See [docs/TELEMETRY-INGESTION.md](docs/TELEMETRY-INGESTION.md) for full request/response details and limitations.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/health | API status |
| GET | /api/summary | Dashboard KPIs and chart data |
| GET | /api/alerts | Search/filter alerts |
| GET | /api/alerts/<id> | Alert details |
| PATCH | /api/alerts/<id>/status | Update incident status |
| POST | /api/events | Ingest a normalized lab event |
| POST | /api/ingest/auth-log | Parse Ubuntu SSH auth log text |
| POST | /api/ingest/pfsense | Parse pfSense JSONL text |

## Test

From the repository root:

\`\`\`bash
cd backend
PYTHONPATH=. python -m pytest
\`\`\`

The repository includes a GitHub Actions workflow for Python tests and frontend build checks. Confirm the latest workflow result on GitHub before treating the project as verified.

## Data and security notes

- The current backend uses an in-memory store; changes reset when the API restarts.
- Parsed raw events are returned in the ingestion response and are not persisted.
- Sample IP addresses are documentation ranges and should not be treated as real threat intelligence.
- The API binds to loopback by default. Do not expose it directly to an untrusted network.
- Never ingest secrets, personal data, or real malicious files into a public portfolio repository.
- Keep API keys in environment variables; do not commit them.
- Only test against systems and networks you own or are authorized to assess.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md). Next priorities are SQLite persistence, incident timelines, phishing-analysis integration, and optional Wazuh / Zeek / Suricata adapters.

## License

No license has been added yet. Add one before accepting contributions or redistributing the project.
