# Detection Rules

The first two rules below are implemented in \`backend/app/telemetry.py\` for parsed lab fixtures. They are starter heuristics, not production detections. Rule thresholds are currently fixed defaults.

## SSH authentication burst — implemented

- **Rule ID:** \`SSH-BRUTE-001\`
- **Source:** Ubuntu SSH authentication log
- **Condition:** 5 or more failed SSH authentication attempts from one source IP within 120 seconds
- **Severity:** High
- **ATT&CK:** T1110 — Brute Force
- **Triage:** Check source address, target account, time window, and whether a successful login followed the failures.
- **False positives:** Misconfigured clients, stale automation credentials, or a user repeatedly mistyping a password.

## Repeated blocked connections — implemented

- **Rule ID:** \`PFSENSE-DENY-BURST-001\`
- **Source:** pfSense JSONL firewall events
- **Condition:** 5 or more block/reject records from one source IP in the submitted batch
- **Severity:** Low
- **ATT&CK:** T1046 — Network Service Discovery (hypothesis only; confirm the destination-port spread and context)
- **Triage:** Confirm action, interface, destination host, port spread, and whether the traffic was expected.
- **False positives:** Normal internet background noise, scanners used by the lab owner, and repeated legitimate connection failures.

## Unusual outbound destination — backlog

- **Source:** pfSense, Zeek, or Suricata events
- **Condition:** New or rare outbound destination, unusual port, or policy violation
- **Severity:** Medium by default; raise only with supporting evidence
- **Triage:** Review process/host owner, DNS resolution, destination reputation, TLS metadata, and approved change windows.

## Suspicious email link — integration backlog

- **Source:** Authorized phishing-analysis workflow
- **Condition:** URL host mismatch, suspicious redirect chain, failed sender authentication, or known malicious IOC
- **Severity:** High or Critical based on corroborating evidence
- **ATT&CK:** T1566.002 — Spearphishing Link
- **Triage:** Preserve headers, extract URLs and hashes safely, avoid opening suspicious links directly, and record confidence and evidence.

## Rule quality requirements

Every rule should include a unique ID, description, data source, query/logic, severity rationale, ATT&CK mapping where justified, false-positive notes, and a repeatable test fixture. ATT&CK mappings are hypotheses and must be supported by observed evidence.
