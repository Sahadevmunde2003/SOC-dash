# Roadmap

## Milestone 1 — Analyst console
- [x] React + Vite dark SOC dashboard
- [x] Flask health, summary, alert list, detail, status, and normalized-event ingestion endpoints
- [x] Synthetic alert dataset and sample lab log fixtures
- [x] Terminal CLI
- [x] API tests and initial documentation

## Milestone 2 — Real lab telemetry
- [x] Parse Ubuntu SSH authentication logs
- [x] Parse pfSense JSONL firewall exports
- [x] Normalize events and validate timestamps / IP addresses / firewall actions
- [x] Implement starter failed-login and repeated-block rules
- [x] Add ingestion results, parser errors, and detection test fixtures
- [x] Document raw ingestion API usage and limitations
- [ ] Add configurable thresholds and additional export-format adapters
- [ ] Add live/tail ingestion from authorized lab hosts (opt-in, secured)

## Milestone 3 — Case management
- [ ] Persist alerts, events, and notes in SQLite
- [ ] Add incident timeline and related-event correlation
- [ ] Add analyst ownership and an audit trail
- [ ] Export incident reports as JSON and Markdown/PDF

## Milestone 4 — Phishing workflow integration
- [ ] Reuse existing email-header parsing
- [ ] Extract URLs, domains, IPs, and file hashes
- [ ] Record SPF/DKIM/DMARC results where available
- [ ] Add evidence-based verdict and confidence score
- [ ] Link phishing alerts to related network events

## Milestone 5 — Advanced integrations
- [ ] Optional Wazuh event source
- [ ] Optional Zeek / Suricata import
- [ ] Role-based access control and secure configuration
- [ ] CI, deployment guide, and screenshots / demo video

## Definition of done

A milestone is complete when its features have tests, documentation, sample inputs, expected outputs, and clear limitations. Avoid describing sample data as live telemetry.
