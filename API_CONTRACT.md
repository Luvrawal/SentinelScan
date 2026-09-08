# REST API Contract

## Base rules

Base URL: `/api`. JSON uses snake_case. All scan/report operations require a valid JWT bearer token and must verify that the token subject owns the scan. The authorization checkbox is separate from JWT: it must be true on scan creation and is recorded with timestamp and submitting IP.

## Authentication

### `POST /api/auth/token`

Minimal hackathon token endpoint. It accepts a demo email and returns a signed JWT. Full registration and password lifecycle are out of scope.

Request:

| Field | Type | Required |
|---|---|---|
| `email` | string | yes |

Response `200`:

- `access_token`: string
- `token_type`: `bearer`
- `expires_in`: integer seconds

Errors: `422` invalid request; `500` signing/configuration failure.

## Scan lifecycle

### `POST /api/scan`

Creates a scan and enqueues a Celery job.

Request:

- `target_url`: absolute HTTP(S) URL
- `authorization_confirmed`: boolean, must be true

Response `202`:

- `scan_id`: UUID
- `status`: `queued`
- `progress`: `0`
- `status_url`: `/api/scan/{id}/status`
- `report_url`: `/api/scan/{id}/report`

Errors: `401` missing/invalid JWT; `400` authorization not confirmed; `422` malformed or unsafe URL; `503` queue unavailable.

### `GET /api/scan/{scan_id}/status`

Returns lifecycle state for an owned scan.

Response `200`:

- `scan_id`: UUID
- `target_url`: string
- `status`: `queued | scanning | analyzing | completed | failed`
- `progress`: integer 0-100
- `error`: nullable string
- `created_at`: ISO-8601 timestamp
- `updated_at`: ISO-8601 timestamp

Errors: `401` authentication failure; `403` scan belongs to another user; `404` scan not found.

### `GET /api/scan/{scan_id}/report`

Returns the completed report data. While a scan is active, return `409` with the current status rather than partial findings.

Response `200`:

- `scan_id`: UUID
- `target_url`: string
- `status`: `completed`
- `executive_summary`: string
- `technologies`: array of `{name, version, category, cpe}`
- `findings`: array of `{id, title, description, source, severity, cvss_score, cvss_version, cve_id, kev_known_exploited, owasp_category, evidence, remediation}`
- `pdf_url`: `/api/scan/{id}/report.pdf`
- `sbom_url`: `/api/scan/{id}/sbom`

Errors: `401`, `403`, `404`, `409` report not ready.

### `GET /api/scan/{scan_id}/report.pdf`

Returns the rendered WeasyPrint PDF as `application/pdf` with a download filename. Requires an owned completed scan.

Responses: `200` PDF; `401`, `403`, `404`, or `409` as above; `500` render failure, with the scan preserved and error logged.

### `GET /api/scan/{scan_id}/sbom`

Returns CycloneDX 1.6 JSON generated from the scan technology profile as `application/vnd.cyclonedx+json` with a download filename.

Responses: `200` SBOM; `401`, `403`, `404`, or `409` as above.

## Error shape

All API errors use `{ "detail": "human-readable message", "code": "stable_error_code" }`. Internal exception details, secrets, subprocess command output, and upstream credentials are never returned to clients.

## Worker state contract

The worker writes `queued` when accepted, `scanning` during Nuclei and custom checks, `analyzing` during NVD/KEV/OWASP/CVSS/AI enrichment, `completed` only after report and SBOM data are available, and `failed` with a bounded reason on timeout, invalid upstream data, or unrecoverable dependency failure.

## Explicitly absent endpoints

There are no ownership-verification, rate-limit administration, SOAR, approval, execution, scheduled-scan, CI/CD, share-link, trust-badge, chat, or false-positive-triage endpoints in this build.
