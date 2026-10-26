# Run Sentinel SOC on Kali Linux and Windows

This guide starts the **Sentinel SOC dashboard** locally on Kali Linux or Windows. You do not need pfSense, a separate Ubuntu server, or a Kali-to-Windows network setup to run the demo. The included sample logs are enough to try the ingestion features.

## What you need

- Git
- Python 3.10 or newer
- Node.js 18 or newer, with npm
- Internet access for the initial clone and dependency installation

Check installations:

```text
git --version
python --version
node --version
npm --version
```

On some Windows installations, use `py --version` if `python --version` does not work. On Kali, use `python3 --version`.

## 1. Download the repository

Run this in a terminal:

```bash
git clone https://github.com/Sahadevmunde2003/SOC-dash.git
cd SOC-dash
```

If you already cloned the project, enter its directory and update it:

```bash
git pull origin main
```

## 2A. Run on Kali Linux

Open a terminal in the repository directory.

### Install system requirements (if missing)

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nodejs npm
```

Check `node --version`; it should be 18 or newer. If the Kali repository's Node.js package is older, install a current Node.js LTS release before continuing.

### Start the Flask backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.main
```

Keep this terminal open. The API should be available at `http://127.0.0.1:5000`.

### Start the frontend

Open a **second terminal** and go to the repository directory (the directory containing `backend` and `frontend`). If you opened the second terminal elsewhere, replace the example path with your actual clone location.

```bash
cd SOC-dash/frontend
npm install
npm run dev
```

If you are already in the repository root, use `cd frontend` instead of `cd SOC-dash/frontend`.

Open **http://127.0.0.1:5173** in your browser.

## 2B. Run on Windows (PowerShell)

Install Git, Python 3.10+, and Node.js 18+ first. During Python installation, enable the option to add Python to PATH if available.

Open PowerShell in the folder where you want the project, then run:

```powershell
git clone https://github.com/Sahadevmunde2003/SOC-dash.git
cd SOC-dash
```

### Start the Flask backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.main
```

If PowerShell blocks activation scripts, allow activation for **this terminal session only** and retry the activation command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Keep this terminal open. The API should be available at `http://127.0.0.1:5000`.

### Start the frontend

Open a **second PowerShell window**. Change directory to your cloned project folder; for example:

```powershell
cd SOC-dash\frontend
npm install
npm run dev
```

If the second terminal is already at the repository root, run `cd frontend` instead.

Open **http://127.0.0.1:5173** in your browser.

### Windows Command Prompt alternative

If you use Command Prompt instead of PowerShell, activate the virtual environment with:

```bat
.venv\Scripts\activate.bat
```

Run the other backend commands from the `backend` directory as shown above.

## 3. Confirm the application is running

With both terminals still open:

1. Visit `http://127.0.0.1:5173` for the dashboard.
2. Visit `http://127.0.0.1:5000/api/health` to confirm the API responds with JSON containing `"status": "ok"`.
3. Do not close either terminal while using the app. Stop a service with **Ctrl+C** in its terminal.

If the frontend cannot reach the API, make sure the backend is running on port 5000 and that you opened the frontend at `127.0.0.1:5173` or `localhost:5173`.

## 4. Try the included sample telemetry

Run these from the **repository root** while the backend is running. They use Python's standard library, so the examples work on Kali and Windows without requiring curl-specific JSON quoting.

### Submit the Ubuntu SSH authentication log

```bash
python -c "import json,urllib.request; p=json.dumps({'content':open('backend/data/sample-auth.log',encoding='utf-8').read()}).encode(); r=urllib.request.Request('http://127.0.0.1:5000/api/ingest/auth-log',data=p,headers={'Content-Type':'application/json'},method='POST'); print(urllib.request.urlopen(r).read().decode())"
```

### Submit the pfSense JSONL sample

```bash
python -c "import json,urllib.request; p=json.dumps({'content':open('backend/data/sample-pfsense.jsonl',encoding='utf-8').read()}).encode(); r=urllib.request.Request('http://127.0.0.1:5000/api/ingest/pfsense',data=p,headers={'Content-Type':'application/json'},method='POST'); print(urllib.request.urlopen(r).read().decode())"
```

On Kali, you may use `python3` instead of `python` if needed. On Windows, run these commands from the repository root and ensure the backend virtual environment is activated if you are using it.

The response reports parsed events, invalid lines, and any detections generated. Return to the dashboard and inspect the alerts. The included data is synthetic and intended for practice.

## 5. Use the CLI (optional)

From the repository root, activate the backend virtual environment first if it is not already active, then:

```bash
python backend/socctl.py health
python backend/socctl.py alerts --query phishing
python backend/socctl.py --help
```

The CLI talks to the API at `127.0.0.1:5000`. The example alert ID in old screenshots or notes may not exist in your current in-memory data; use an ID returned by the API/dashboard when changing an alert's status.

## 6. Run tests (optional)

From the repository root, activate the backend virtual environment and run:

```bash
python -m pytest backend/tests
```

Build-check the frontend:

```bash
cd frontend
npm run build
```

## Troubleshooting

- **`python` or `py` not found on Windows:** reinstall Python and enable PATH, or use the Python launcher available on your system.
- **`venv` fails on Kali:** install `python3-venv` with apt, then recreate the environment.
- **Port 5000 or 5173 is busy:** stop the other process using that port before restarting this project.
- **`npm install` fails:** confirm Node.js is version 18+ and retry when the network is available.
- **PowerShell activation is blocked:** use the process-scoped policy command shown above, or use Command Prompt's `activate.bat`.
- **Dashboard opens but data/API is unavailable:** keep the backend terminal running and check `http://127.0.0.1:5000/api/health`.
- **Alerts disappear after restart:** expected for this demo; the backend stores alerts in memory and does not persist them to a database.

## Scope and safety

- The backend and frontend bind to loopback by default; this is for local use on the same computer.
- This guide does not configure a multi-VM network or expose the API to other machines.
- The project is a demo, not a production SIEM. It does not continuously monitor a host or connect directly to a live pfSense firewall.
- Only analyze logs from systems and networks you own or are authorized to assess.
