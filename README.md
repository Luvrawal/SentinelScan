# SentinelScan

SentinelScan is an authorized, read-only website vulnerability scanner for the GLS University hackathon. It combines Nuclei, OWASP Top 10:2025 mapping, CVE/KEV intelligence, AI remediation, PDF reporting, and SBOM export.

## Run locally

1. Copy `.env.example` to `.env` and add optional Gemini/NVD keys.
2. Run `docker compose up --build`.
3. Open `http://localhost:3000`.
4. Submit an approved public HTTP(S) target and confirm authorization.
5. Watch the scan progress, then open the report when complete.

The API is available at `http://localhost:8000/docs`. Scanning private, localhost, link-local, or reserved targets is rejected. Detection is read-only.
