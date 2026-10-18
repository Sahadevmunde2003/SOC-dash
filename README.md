# Sentinel SOC

A portfolio-grade Security Operations Center (SOC) dashboard built with React + Vite and Flask. The first milestone ships a dark SIEM-style analyst console, a REST API, synthetic alerts, incident status workflows, a terminal CLI, sample lab logs, and API tests.

> **Lab/demo notice:** the included alerts and indicators are synthetic. The app is not a production SIEM and does not claim live monitoring until real telemetry sources are configured.

## Features

- Security overview: alert counts, severity distribution, and alert activity.
- Alert triage: search, severity/source filters, and investigation details.
- Incident workflow: update case status and add analyst notes.
- IOC-focused event details and MITRE ATT&CK technique references.
- Flask API for health, summaries, alerts, status updates, and event ingestion.
- Python CLI for terminal-based health checks, alert searches, status updates, and ingestion.
- Sample pfSense-style JSONL events and Ubuntu authentication log fixtures.
- Pytest API tests and a roadmap for real lab telemetry.

## Architecture

```text
React + Vite (5173)
       │ REST / JSON
       ▼
Flask API (5000) ─── In-memory demo store
       ▲
       ├── Python SOC CLI
       └── Future: pfSense / Ubuntu / Wazuh / Zeek / Suricata adapters
```

## Repository layout

```text
sentinel-soc/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── data.py
│   │   └── main.py
│   ├── data/
│   │   ├── sample-auth.log
│   │   └── sample-pfsense.jsonl
│   ├── tests/test_api.py
│   ├── requirements.txt
│   └── socctl.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       └── styles.css
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10+
- Node.js 18+ and npm

## Run locally

### 1. Start the backend

Linux/macOS (including Kali Linux):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

Health endpoint: http://127.0.0.1:5000/api/health

### 2. Start the frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### 3. Use the CLI

With the backend running, from the `backend/` directory:

```bash
python socctl.py health
python socctl.py alerts --query phishing
python socctl.py status SOC-2026-1042 Investigating
```

Use `python socctl.py --help` for available commands.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API status |
| GET | `/api/summary` | Dashboard KPIs and chart data |
| GET | `/api/alerts` | Search/filter alerts |
| GET | `/api/alerts/<id>` | Alert details |
| PATCH | `/api/alerts/<id>/status` | Update incident status |
| POST | `/api/events` | Ingest a normalized lab event |

Check the Flask route definitions for exact request and response schemas.

## Data and security notes

- The current backend uses an in-memory store; changes reset when the API restarts.
- Sample IP addresses are documentation ranges and should not be treated as real threat intelligence.
- Never ingest secrets, personal data, or real malicious files into a public portfolio repository.
- Keep API keys in environment variables; do not commit them.
- Only test against systems and networks you own or are authorized to assess.

## Roadmap

- [ ] Persist events, alerts, and cases in SQLite.
- [ ] Parse Ubuntu SSH/authentication logs into normalized events.
- [ ] Parse pfSense firewall exports and add validation/error handling.
- [ ] Add configurable detection rules for repeated failed logins and suspicious outbound connections.
- [ ] Correlate alerts into a unified incident timeline.
- [ ] Reuse the existing phishing-analysis workflow for header analysis, URL/IOC extraction, and report generation.
- [ ] Add role-aware analyst activity history and exportable incident reports.
- [ ] Add optional Wazuh, Zeek, or Suricata integration.
- [ ] Add CI checks and a deployment guide.

## Development status

Milestone 1 is a local portfolio MVP. Automated tests are included; run them with `pytest` from `backend/`. Validate frontend dependencies with `npm install` and build with `npm run build` before deployment.

## License

Choose and add a license before accepting contributions or redistributing the project.
