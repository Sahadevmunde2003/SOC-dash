# Detection Rules — Initial Backlog

These are candidate rules for the lab telemetry milestone, not claims that the current MVP detects them from raw logs.

## Rule 1: SSH authentication burst

- **Source:** Ubuntu /var/log/auth.log or journald SSH service logs
- **Condition:** 5 or more failed SSH authentication attempts from one source IP within 2 minutes
- **Severity:** High
- **ATT&CK:** T1110 — Brute Force
- **Triage:** Check source address, target account, time window, and whether a successful login followed the failures.

## Rule 2: Repeated denied inbound connections

- **Source:** pfSense firewall log
- **Condition:** Multiple denied inbound connections to different destination ports from the same source in a short window
- **Severity:** Low to Medium, depending on volume and exposure
- **ATT&CK:** T1046 — Network Service Discovery (only if the evidence supports a discovery hypothesis)
- **Triage:** Confirm action, interface, destination host, port spread, and whether the traffic was expected.

## Rule 3: Unusual outbound destination

- **Source:** pfSense, Zeek, or Suricata events
- **Condition:** New or rare outbound destination, unusual port, or policy violation
- **Severity:** Medium by default; raise only with supporting evidence
- **Triage:** Review process/host owner, DNS resolution, destination reputation, TLS metadata, and approved change windows.

## Rule 4: Suspicious email link

- **Source:** Authorized phishing-analysis workflow
- **Condition:** URL host mismatch, suspicious redirect chain, failed sender authentication, or known malicious IOC
- **Severity:** High or Critical based on corroborating evidence
- **ATT&CK:** T1566.002 — Spearphishing Link
- **Triage:** Preserve headers, extract URLs and hashes safely, avoid opening suspicious links directly, and record confidence and evidence.

## Rule quality requirements

Every rule should include a unique ID, description, data source, query/logic, severity rationale, ATT&CK mapping where justified, false-positive notes, and a repeatable test fixture. ATT&CK mappings are hypotheses and must be supported by observed evidence.
